"""
======================================================================
dodocker. A build tool for independent docker images and registries.
Copyright (C) 2014-2016  n@work Internet Informationssysteme GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
======================================================================
"""

from __future__ import print_function

CONFIG = {'registry_path': 'localhost:5000',
          'insecure': True}

DOIT_CONFIG = {'default_tasks': ['build']}


import os, yaml, json, sys, re, time
from doit.tools import result_dep
import docker
import subprocess

doc = docker.Client(base_url='unix://var/run/docker.sock',
                    version='1.17',
                    timeout=10)
config = {}

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

def docker_build(path,tag,dockerfile,pull=False,rm=True):
    def docker_build_callable():
        error = False
        print(path,tag)
        for line in doc.build(path,tag=tag,stream=True,pull=pull,dockerfile=dockerfile,rm=rm):
            line_parsed = json.loads(line)
            if 'stream' in line_parsed:
                sys.stdout.write(line_parsed['stream'].encode('utf8'))
            if line_parsed.get('errorDetail'):
                sys.stdout.write(line_parsed['errorDetail']['message']+'\n')
                error = True
        return not error
    return docker_build_callable

def docker_tag(image,repository,tag=None):
    def docker_tag_callable():
        print("TAG:",image,repository,tag)
        return doc.tag(image,repository,tag,force=True)
    return docker_tag_callable

def docker_push(repository,tag):
    def docker_push_callable():
        error = False
        print("push:",repository,tag)
        try:
            result = doc.push(repository,stream=True,tag=tag,insecure_registry=config['insecure'])
        except docker.errors.DockerException as e:
            sys.exit(e)
        for line in result:
            line_parsed = json.loads(line)
            if 'status' in line_parsed:
                sys.stdout.write(line_parsed['status']+'\n')
            if line_parsed.get('errorDetail'):
                sys.stdout.write(line_parsed['errorDetail']['message']+'\n')
                error = True
        return not error
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
    try:
        with open('dodocker.yaml','r') as f:
            yaml_data = yaml.safe_load(f)
    except IOError:
        sys.exit('No dodocker.yaml found')
    for task_description in yaml_data:
        image = task_description['image']

        if not 'tags' in task_description:
            tags = []
        else:
            tags = task_description['tags']

        name = '%s_%s' % (mode, task_description['image'])
        path = task_description.get('path',None)
        dockerfile = task_description.get('dockerfile','Dockerfile')
        new_task = {'basename':name, 'verbosity':0}
        
        """ task dependencies
        """
        new_task['uptodate'] = []
        new_task['task_dep'] = []

        if 'depends' in task_description:
            depends_subtask_name = task_description['depends']
            new_task['task_dep'] = ['%s_%s' % (mode,depends_subtask_name)]

        if mode == 'build':
            task_type = task_description.get('type','dockerfile')
            if task_type not in ('dockerfile','shell'):
                sys.exit('Image {}: unknown type {}'.format(image, task_type))
            if task_type == 'shell':
                if 'shell_action' in task_description:
                    new_task['actions'] = [task_description['shell_action']]
                else:
                    sys.exit('Image {}: shell_action missing for build type shell'.format(image))
            elif task_type == 'dockerfile':
                if not path:
                    sys.exit('Image {}: path missing for build type dockerfile'.format(image))
                pull = task_description.get('pull',False)
                rm = task_description.get('rm',True)
                new_task['actions'] = [docker_build(path,tag=image,dockerfile=dockerfile,pull=pull,rm=rm)]

            # tagging
            tag = None
            image_no_tag = image
            if ':' in image:
                image_no_tag, tag = image.split(':')
            new_task['actions'].append(docker_tag(image, '%s/%s' % (config['registry_path'],image_no_tag),tag))
            for tag in tags:
                new_task['actions'].append(docker_tag(image,'%s/%s' % (config['registry_path'],image) ,tag=tag))
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
            new_task['actions'] = [docker_push('%s/%s' % (config['registry_path'],image), tag)]
            new_task['task_dep'].append('tagging_*')
        yield new_task

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

def load_config():
    path = os.path.expanduser('~/.dodocker.yaml')
    if os.path.exists(path):
        try:
            with open(path,'r') as f:
                config = yaml.safe_load(f.read())
        except IOError:
            sys.exit('Failed to read {}'.format(path))
        return config
    return CONFIG
    
def save_config(config):
    try:
        path = os.path.expanduser('~/.dodocker.yaml')
        with open(path,'w') as f:
            f.write(yaml.safe_dump(config))
    except IOError:
        sys.exit('Failed to write {}'.format(path))
    
def task_set_insecure():
    def set_insecure(flag):
        if flag[0] == 'yes':
            flag = True
        else:
            flag = False
        config = load_config()
        config['insecure'] = flag
        save_config(config)
    return {'actions': [(set_insecure,)],
            'pos_arg': 'flag'}

def task_set_registry():
    def set_registry(pos):
        if not pos:
            sys.exit('Error: please give a registry path (i.e. your.reg.com:443)')
        config = load_config()
        config['registry_path'] = pos[0]
        save_config(config)
    return {'actions': [(set_registry,)],
            'pos_arg': 'pos'}
    
"""
pretty print a dump of build tasks for debugging purposes
"""
def task_build_dump():
    def build_dump():
        from pprint import pprint
        pprint(list(task_build()))
    return {'actions':[build_dump],
            'verbosity':2}

import doit

HELP_TEXT = """
   dodocker help
   
   build images: dodocker
   upload images: dodocker upload
   set registry: dodocker set_registry registry.yourdomain.com:443
   set insecure registry: dodocker set_insecure yes/no

   dodocker (c) 2014-2016 n@work Internet Informationssysteme GmbH
   based on doit by Eduardo Schettino.

   This program comes with ABSOLUTELY NO WARRANTY
   This is free software, and you are welcome to redistribute it
   under certain conditions. See this link for more information:
   http://www.gnu.org/licenses/gpl-3.0.en.html

"""

def dodocker_help_usage(cmd):
    print(HELP_TEXT)
    doit.cmd_help.Help.print_usage_orig(cmd)
    
def main():
    global config
    config = load_config()
    # monkey patch for dodocker specific usage help
    doit.cmd_help.Help.print_usage_orig = staticmethod(doit.cmd_help.Help.print_usage)
    doit.cmd_help.Help.print_usage = staticmethod(dodocker_help_usage)
    doit.run(globals())

