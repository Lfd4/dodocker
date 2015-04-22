"""
doit task file

this task file reads the task definition from dodocker.yaml

"""

DOIT_CONFIG = {'default_tasks': ['build']}
REGISTRY = 'dr.work.de:443'




import os, yaml, json, sys, re, time
from doit.tools import result_dep
import docker
import subprocess

class RegistryPath(object):
    def __init__(self,path):
        self.path = path
        (tmp,port) = path.rsplit(':')
        self.port = int(port)

taskname_regexp = re.compile('^[a-zA-Z0-9 ._\-]+$')

doc = docker.Client(base_url='unix://var/run/docker.sock',
                    version='1.17',
                    timeout=10)

def git_build_count(path):
    orig_path = os.getcwd()
    os.chdir(path)
    buildnr = int(subprocess.check_output(['git','rev-list','HEAD','--count']))
    os.chdir(orig_path)
    return buildnr

def image_id(image):
    def image_id_callable():
        try:
            data = doc.inspect_image(image)
        except docker.errors.APIError as e:
            if e.response.status_code != 404:
                raise
            return False
        return data['Id']
    return image_id_callable

def check_available(image):
    def check_available_callable():
        try:
            data = doc.inspect_image(image)
        except docker.errors.APIError as e:
            if e.response.status_code != 404:
                raise
            return False
        return True
    return check_available_callable

def docker_build(path,tag,dockerfile):
    def docker_build_callable():
        error = False
        print path,tag
        for line in doc.build(path,tag=tag,rm=True,stream=True,pull=True,dockerfile=dockerfile):
            line_parsed = json.loads(line)
            if 'stream' in line_parsed:
                sys.stdout.write(line_parsed['stream'].encode('utf8'))
            if 'errorDetail' in line_parsed:
                sys.stdout.write(line_parsed['errorDetail'])
                error = True
        if not error:
            return True
        else:
            return False
    return docker_build_callable

def docker_tag(image,repository,tag=None):
    def docker_tag_callable():
        print "TAG:",image,repository,tag
        return doc.tag(image,repository,tag,force=True)
    return docker_tag_callable

def docker_push(repository,tag):
    def docker_push_callable():
        error = False
        print "push:",repository,tag
        for line in doc.push(repository,stream=True,tag=tag):
            line_parsed = json.loads(line)
            if 'status' in line_parsed:
                sys.stdout.write(line_parsed['status']+'\n')
            else:
                print "hmmm", line_parsed
            if "errorDetail" in line:
                error = True
        if not error:
            return True
        else:
            return False
    return docker_push_callable
        

def get_file_dep(path):
    file_list = []
    for root,dirs,files in os.walk(path):
        [dirs.remove(i) for i in dirs if i.startswith('.')]
        for i in files:
            if i.startswith('.'):
                continue
            file_list.append(os.path.join(root,i))
    return file_list

def parse_dodocker_yaml(mode):
    dep_groups = {}
    with open('dodocker.yaml','r') as f:
        yaml_data = yaml.safe_load(f)
    for task_description in yaml_data:
        image = task_description['image']

        if not 'tags' in task_description:
            tags = []
        else:
            tags = task_description['tags']

        name = '%s_%s' % (mode, task_description['taskname'])
        path = task_description.get('path',None)
        dockerfile = task_description.get('dockerfile','Dockerfile')
        assert taskname_regexp.match(name), 'invalid taskname %s' % name
        new_task = {'basename':name, 'verbosity':0}
        
        """ task dependencies
        """
        new_task['uptodate'] = []
        new_task['task_dep'] = []

        if 'depends' in task_description:
            depends_subtask_name = task_description['depends']
            new_task['task_dep'] = ['%s_%s' % (mode,depends_subtask_name)]

        """ groups (not working yet)
        """
        #if 'group' in task_description:
        #    group = task_description['group']
        #    if not group in dep_groups:
        #        dep_groups[group] = []
        #    dep_groups[group].append('build:'+name)
        
        if mode == 'build':
            assert not(task_description.get('shell_action') and task_description.get('docker_build'))
            if 'shell_action' in task_description:
                new_task['actions'] = [task_description['shell_action']]
            if 'docker_build' in task_description:
                assert path
                new_task['actions'] = [docker_build(path,tag=image,dockerfile=dockerfile)]


            # tagging
            tag = None
            image_no_tag = image
            if ':' in image:
                image_no_tag, tag = image.split(':')
            new_task['actions'].append(docker_tag(image, '%s/%s' % (REGISTRY,image_no_tag),tag))
            for tag in tags:
                new_task['actions'].append(docker_tag(image,'%s/%s' % (REGISTRY,image) ,tag=tag))
                new_task['actions'].append(docker_tag(image,image ,tag=tag))
                   
            # IMPORTANT: image_id has to be the last action. The output of the last action is used for result_dep.
            new_task['actions'].append(image_id(image))
            
            # intra build dependencies 
            if task_description.get('file_dep'):
                new_task['file_dep'] = [os.path.join(path,i) 
                                    for i in task_description.get('file_dep')]
            elif path:
                new_task['file_dep'] = get_file_dep(path)
            if 'depends' in task_description:
                new_task['uptodate'].append(result_dep('%s_%s' % (mode,depends_subtask_name)))

            new_task['uptodate'].append(check_available(image))

        elif mode == 'upload':
            tag = None
            if ':' in image:
                image, tag = image.split(':')
            new_task['actions'] = [docker_push('%s/%s' % (REGISTRY,image), tag)]
            new_task['task_dep'].append('tagging_*')
            #for tag in tags:
            #    new_task['actions'].append(docker_push(image,'%s/%s' % (REGISTRY,image)))

        yield new_task
    # Groups are not yet implemented
    #for group in dep_groups.keys():
    #    new_task = {
    #        'basename': group,
    #        'actions': None,
    #        'task_dep': dep_groups[group]}
    #    yield new_task


def task_build():
    all_build_tasks = []
    for task in parse_dodocker_yaml('build'):
        all_build_tasks.append(task['basename'])
        yield task
    if all_build_tasks:
        yield {'basename':'build',
               'actions': None,
               'task_dep': all_build_tasks}

def task_upload():
    all_upload_tasks = []
    for task in parse_dodocker_yaml('upload'):
        all_upload_tasks.append(task['basename'])
        yield task

    yield {'basename':'upload',
           'actions': None,
           'task_dep': all_upload_tasks}

def main():
    import doit
    doit.run(globals())
    #    from pprint import pprint
    #    pprint(list(task_build()))
