"""
======================================================================
dodocker. A build tool for independent docker images and registries.
Copyright (C) 2014-2016  n@work Internet Informationssysteme GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
======================================================================
"""


import os, yaml, json, sys, re, time, hashlib, docker
import requests, shutil
from doit.tools import result_dep, run_once
from distutils.dir_util import copy_tree
import subprocess
import git

dodocker_config = None

doc = docker.Client(base_url='unix://var/run/docker.sock',
                    version='auto',
                    timeout=10)


"""
===============================
Action and Dependency functions
===============================
"""

def image_id(image):
    def image_id_callable():
        try:
            data = doc.inspect_image(image)
        except docker.errors.APIError as e:
            if e.response.status_code != 404: # pragma: no cover
                raise
            return False
        return data['Id']
    return image_id_callable

def check_available(image):
    def check_available_callable():
        try:
            data = doc.inspect_image(image)
        except docker.errors.APIError as e:
            if e.response.status_code != 404: # pragma: no cover
                raise
            return False
        return True
    return check_available_callable

def docker_build(ddtask):
    def docker_build_callable():
        error = False
        print(ddtask.path, ddtask.doit_image_name, ddtask.buildargs)
        if ddtask.templates and ddtask.jinja_env:
            build_path = dodocker_build_path(repository_name=ddtask.doit_image_name)
            if os.path.exists(build_path):
                shutil.rmtree(build_path)
            shutil.copytree(ddtask.path, build_path)
            for tmpl_path in ddtask.jinja_env.list_templates():
                if tmpl_path.endswith('.j2'):
                    destination, rest = os.path.splitext(tmpl_path)
                else:
                    destination = tmpl_path
                with open(os.path.join(build_path, destination),'w') as f:
                    f.write(ddtask.jinja_env.get_template(tmpl_path).render(
                        template=ddtask.templateargs,
                        t=ddtask.templateargs,
                        build=ddtask.buildargs,
                        b=ddtask.buildargs))
        else:
            build_path = ddtask.path
        for line in doc.build(build_path, tag=ddtask.doit_image_name, stream=True,
                              pull=ddtask.pull, dockerfile=ddtask.dockerfile,
                              buildargs=ddtask.buildargs, rm=ddtask.rm,
                              nocache=dodocker_config.get('no_cache',False)):
            line_parsed = json.loads(line.decode('utf-8'))
            if 'stream' in line_parsed:
                sys.stdout.write(line_parsed['stream'])
            if line_parsed.get('errorDetail'):
                sys.stdout.write(line_parsed['errorDetail']['message']+'\n')
                error = True
        return not error
    return docker_build_callable

def docker_flatten(ddtask):
    def docker_flatten_callable():
        container = doc.create_container(ddtask.doit_image_name,'/data')
        stream, stat = doc.get_archive(container,'/')
        stripped_image = doc.import_image(stream, ddtask.doit_image_name)
        return True
    return docker_flatten_callable

def shell_build(shell_cmd,image,path='.',force=False):
    def docker_build_callable():
        print(shell_cmd,image)
        if check_available(image)() and not force:
            return True
        p = subprocess.Popen([shell_cmd],cwd=path,shell=True,
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        while p.poll() is None:
            sys.stdout.write(p.stdout.readline().decode('utf-8'))
        return p.wait() == 0
    return docker_build_callable

def docker_tag(image,repository,tag=None):
    def docker_tag_callable():
        print("TAG:",image,repository,tag)
        return doc.tag(image,repository,tag,force=True)
    return docker_tag_callable

def docker_push(repository,tag):
    def docker_push_callable():
        error = False
        try_count = dodocker_config['push_retries']
        print("push:",repository,tag)
        try:
            while try_count > 0:
                try_count -= 1
                try:
                    result = doc.push(repository,stream=True,tag=tag,insecure_registry=dodocker_config['insecure'])
                    try_count = 0
                except requests.ReadTimeoutError:
                    if try_count < 1:
                        raise DodockerRegistryError('registry failed to answer after retrying request')
                    time.sleep(dodocker_config['push_retry_wait'])
        except docker.errors.DockerException as e:
            sys.exit(e)
        for line in result:
            line_parsed = json.loads(line.decode('utf-8'))
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

def dodocker_build_path(url=None, checkout_type=None, checkout=None, repository_name=None):
    return "dodocker_repos/{}".format(
        hashlib.md5(".".join((str(url),
                              str(checkout_type),
                              str(checkout),
                              str(repository_name))).encode('utf-8')).hexdigest())

def update_git(git_url, checkout_type, checkout):
    def update_git_callable():
        error = False
        path = dodocker_build_path(git_url,checkout_type,checkout)
        if os.path.exists(path):
            if checkout_type in ('commit','tags'):
                # commit and tags don't change
                return not error
            repository = git.Repo(path)
            try:
                response = repository.git.pull()
            except git.GitCommandError:
                error = True
                print ("error on pull for {} {}/{}".format(git_url,checkout_type,checkout))
            else:
                print("git pull on {}".format(git_url))
                print(response)
        else:
            repository = git.Repo.clone_from(git_url,path)
            if checkout_type in ('branch', 'commit'):
                repository.git.checkout(checkout)
            elif checkout_type == 'tags':
                repository.git.checkout('tags/{}'.format(checkout))
            print("done git clone {}".format(git_url))
        return not error
    return update_git_callable


def create_doit_tasks(mode, task_list):
    # loop over tasks
    for dodocker_task in task_list:
        ddtask = dodocker_task
        # general task attributes

        doit_task_name = '{}_{}'.format(mode, ddtask.doit_image_name)
        doit_task = {'basename':doit_task_name, 'verbosity':0}


        """ task dependencies
        """
        doit_task['uptodate'] = []
        doit_task['task_dep'] = []

        if ddtask.depends_subtask_name and mode in ('build','upload'):
            doit_task['task_dep'].append('{}_{}'.format(mode,ddtask.depends_subtask_name))

        if mode == 'git':
            if ddtask.git_url:
                doit_task['actions'] = [update_git(ddtask.git_url,
                                                   ddtask.git_checkout_type,
                                                   ddtask.git_checkout)]
            else:
                continue

        elif mode == 'build':
            doit_task['actions'] = []

            if ddtask.git_url:
                doit_task['task_dep'].append('git_{}'.format(ddtask.doit_image_name))
                path = "{}/{}".format(dodocker_build_path(ddtask.git_url,
                                                     ddtask.git_checkout_type,
                                                     ddtask.git_checkout)
                                      ,ddtask.path)
            if ddtask.task_type == 'shell':
                doit_task['actions'].append(
                    shell_build(ddtask.shell_action, ddtask.doit_image_name, path=ddtask.path,
                                force=dodocker_config.get('no_cache',False)))
            elif ddtask.task_type == 'dockerfile':
                doit_task['actions'].append(
                    docker_build(ddtask))
                if ddtask.flatten:
                    doit_task['actions'].append(
                        docker_flatten(ddtask))
            for image_no_tag, tag in ddtask.tags: 
                doit_task['actions'].append(
                    docker_tag(
                        ddtask.doit_image_name,
                        '%s/%s' % (dodocker_config['registry_path'],image_no_tag),
                        tag))
                doit_task['actions'].append(
                    docker_tag(ddtask.doit_image_name, image_no_tag, tag))
            """ IMPORTANT: 
                image_id has to be the last action. The output of the last action is 
                used for result_dep by doit
            """
            doit_task['actions'].append(image_id(ddtask.doit_image_name))

            # intra build dependencies 
            if ddtask.file_dep:
                doit_task['file_dep'] = [os.path.join(ddtask.path,i) for i in ddtask.file_dep]
            elif ddtask.path:
                doit_task['file_dep'] = get_file_dep(ddtask.path)
            if ddtask.depends_subtask_name:
                doit_task['uptodate'].append(result_dep('%s_%s' % (mode,ddtask.depends_subtask_name)))
            if ( dodocker_config.get('no_cache') and
                 ( not dodocker_config['no_cache_targets'] or
                   ddtask.doit_image_name in dodocker_config['no_cache_targets'] )):
                # the image is not up to date when the cache is disabled by the user
                # thus return always False
                doit_task['uptodate'].append(lambda x=None: False)
            else:
                # an image has to be available
                doit_task['uptodate'].append(check_available(ddtask.doit_image_name))
            # every task has to run once to build the result_dep chain for every image
            doit_task['uptodate'].append(run_once)
        elif mode == 'upload':
            doit_task['actions'] = []
            for image,tag in ddtask.tags:
                doit_task['actions'].append(docker_push('{}/{}'.format(dodocker_config['registry_path'],image), tag))
        yield doit_task


"""
==============================
D O I T - M A I N  - T A S K S
==============================
"""

import doit

task_config_list = None

def task_git():
    all_git_tasks = []
    for task in create_doit_tasks('git',task_config_list):
        all_git_tasks.append(task['basename'])
        yield task
    if all_git_tasks:
        yield {'basename':'git',
               'actions': None,
               'task_dep': all_git_tasks}

        
def task_build():
    all_build_tasks = []
    for task in create_doit_tasks('build',task_config_list):
        all_build_tasks.append(task['basename'])
        yield task
    if all_build_tasks:
        yield {'basename':'build',
               'actions': None,
               'task_dep': all_build_tasks}

def task_upload():
    all_upload_tasks = []
    for task in create_doit_tasks('upload',task_config_list):
        all_upload_tasks.append(task['basename'])
        yield task

    yield {'basename':'upload',
           'actions': None,
           'task_dep': all_upload_tasks}
    
"""
pretty print a dump of build tasks for debugging purposes
"""
def task_build_dump():
    def build_dump():
        from pprint import pprint
        pprint(list(task_build()))
    return {'actions':[build_dump],
            'verbosity':2}


