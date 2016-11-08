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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

DEFAULT_DODOCKER_CONFIG = {'registry_path' : 'localhost:5000',
                           'insecure'      : True}

DOIT_CONFIG = {'default_tasks': ['build']}

dodocker_config_path = '.dodocker.cfg'

from . import parser
from . import do as do_module
import docker, argparse, os, sys, yaml
from dodocker.parser import TaskGroup

dodocker_config = {}



"""
========================
Config related functions
========================
"""

import doit
LICENSE_TEXT = """
dodocker (c) 2014-2016 n@work Internet Informationssysteme GmbH
written by Andreas Elvers - powered by doit by Eduardo Schettino.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
        http://www.apache.org/licenses/LICENSE-2.0
"""

def load_dodocker_config():
    if os.path.exists(dodocker_config_path):
        try:
            with open(dodocker_config_path,'r') as f:
                config = yaml.safe_load(f.read())
        except IOError:
            sys.exit('Failed to read {}'.format(dodocker_config_path))
        return config
    return DEFAULT_DODOCKER_CONFIG
    
def save_dodocker_config(config):
    try:
        with open(dodocker_config_path,'w') as f:
            f.write(yaml.safe_dump(config))
    except IOError:
        sys.exit('Failed to write {}'.format(path))
    
def config_set(key,value):
    if not key in DEFAULT_DODOCKER_CONFIG.keys():
        sys.exit('error: config knows these keys: {}'.format(" ".join(CONFIG.keys())))
    config = load_dodocker_config()
    config[key] = value
    save_dodocker_config(config)

def config_list():
    config = load_dodocker_config()
    for key in config:
        print('{} : {}'.format(key,config[key]))

"""
===============================
Argument parsing and processing
===============================
"""

def process_args(parsed,unparsed):
    doit_args = []
    if parsed.output_file:
        doit_args.extend(('-o',parsed.output_file))
    if parsed.subcommand == 'build':
        if parsed.verbose:
            doit_args.extend(('--verbosity','2'))
        if parsed.parallel:
            doit_args.extend(('-n',str(parsed.parallel[0])))
    if parsed.subcommand in ('build','upload'):
        if parsed.targets:
            
            for target in parsed.targets:
                doit_args.append("{}_{}".format(parsed.subcommand, target))
        else:
            doit_args.append(parsed.subcommand)
    if parsed.subcommand == 'build' and parsed.no_cache:
        dodocker_config['no_cache'] = True
        dodocker_config['no_cache_targets'] = parsed.targets

    elif parsed.subcommand == 'doit':
        doit_args.extend(unparsed)
    elif parsed.subcommand == 'config':
        if parsed.config_mode == 'list':
            config_list()
        elif parsed.set_secure:
            config_set('insecure',False)
        elif parsed.set_insecure:
            config_set('insecure',True)
        elif parsed.set_registry_path:
            config_set('registry_path', parsed.set_registry_path)
        sys.exit(0)
    elif parsed.subcommand == 'alias':
        print("alias dodocker='docker run --rm --privileged -itv /var/run/docker.sock:/var/run/docker.sock {} -v $(pwd):/build nawork/dodocker dodocker'".format(
            ['','-v $(dirname $SSH_AUTH_SOCK):$(dirname $SSH_AUTH_SOCK) -e SSH_AUTH_SOCK=$SSH_AUTH_SOCK'][parsed.ssh_agent]))
        sys.exit(0)
    elif parsed.subcommand == 'quickstart':
        if not os.path.exists('/dodocker/quickstart'):
            sys.exit('dodocker: quickstart files not found.')
        if os.listdir('.'):
            sys.exit('dodocker: directory not empty. quickstart project NOT created')
        copy_tree('/dodocker/quickstart','/build')
        sys.exit(0)
    return doit_args

def create_parser():
    parser = argparse.ArgumentParser(epilog=LICENSE_TEXT,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', dest='configfile',
                        metavar='config file',
                        help='use this dodocker config file')
    parser.add_argument('-d', '--dodocker-file', dest='dodocker_file',
                        default='dodocker.yaml',
                        help='alternate path to a dodocker yaml description file')
    parser.add_argument('-o', dest='output_file',
                        metavar='report output file',
                        help='capture report in output file')
    subparsers = parser.add_subparsers(
        title='sub-commands of dodocker',
        description='dodocker is devided into sub-commands. Please refer to their help.',
        dest='subcommand',
        help='sub-command help')
    build_parser = subparsers.add_parser(
        'build',
        help='build all or selected dodocker targets')
    build_parser.add_argument('-v','--verbose',action='store_true',help='display the build stdout')
    build_parser.add_argument('-n',nargs=1,type=int,metavar='count',
                              dest='parallel',help='number of tasks run in parallel')
    build_parser.add_argument('--no-cache', action='store_true', help='do a docker build without using the cache')
    
    build_parser.add_argument('targets',metavar='target',nargs='*',help='list of targets to build',
                              default=[])
    upload_parser = subparsers.add_parser(
        'upload',
        help='upload built images to registry')
    upload_parser.add_argument('targets',metavar='target',nargs='*',help='list of targets to upload')
    doit_parser = subparsers.add_parser(
        'doit',
        help='pass raw doit commands')
    config_parser = subparsers.add_parser(
        'config',
        help='set config parameter')
    group = config_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--set-insecure', action='store_true',
                       help='given registry is connected insecure (http/self-signed)')
    group.add_argument('--set-secure', action='store_true',
                       help='given registry is connected secure')
    group.add_argument('--set-registry-path', help='url to registry',metavar='url')
    group.add_argument('--list',dest='config_mode', action='store_const', const='list')
    alias_parser = subparsers.add_parser(
        'alias',
        help='return an alias command to conveniently call dodocker as a docker run command')
    alias_parser.add_argument('--ssh-agent', action='store_true',
                              help='Forwarding ssh into container by host-mounting agent socket.')
    quickstart_parser = subparsers.add_parser(
        'quickstart',
        help='populate an empty directory with the quickstart project')
    return parser

"""
============
Entry points
============
"""

from doit.cmd_base import ModuleTaskLoader

def create_task_config_list(argparsed):
    tg = parser.TaskGroup()
    tg.load_task_description_from_file(filename=argparsed.dodocker_file)
    return tg.create_group_data()

def run_dodocker_cli(args):
    """
    helper function for external programs like tests
    """
    parser = create_parser()
    parsed = parser.parse_known_args(args)
    dodocker_config.clear()
    dodocker_config.update(load_dodocker_config())
    try:
        doit_args = process_args(*parsed)
        task_config_list = list(create_task_config_list(parsed[0]))
        do_module.task_config_list = task_config_list
        do_module.dodocker_config = dodocker_config
        doit.doit_cmd.DoitMain(
            ModuleTaskLoader(do_module)).run(doit_args)
    except SystemExit as e:
        # catch normal zero exit, but re-raise other
        if e.code != 0:
            raise
        
def main():
    parser = create_parser()
    parsed = parser.parse_known_args()
    dodocker_config.update(load_dodocker_config())
    doit_args = process_args(*parsed)
    task_config_list = list(create_task_config_list(parsed[0]))
    do_module.task_config_list = task_config_list
    do_module.dodocker_config = dodocker_config
    sys.exit(
        doit.doit_cmd.DoitMain(
            ModuleTaskLoader(do_module)).run(doit_args))
