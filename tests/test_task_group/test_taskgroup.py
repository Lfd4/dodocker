from dodocker.parser import TaskGroup, DodockerParseError
import dodocker
import os, pytest

class TestTasks:
    def test_simple(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: testimagename
          path: testpath
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'testimagename'
        assert td.path == 'testpath'
        assert td.dockerfile == 'Dockerfile'
        assert td.task_type == 'dockerfile'
        assert td.file_dep == None
        assert not td.pull
        assert td.rm == True
        assert td.tags == [('testimagename',None)]
        assert td.doit_image_name == 'testimagename'

    def test_simple_namespace(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: namespace/testimagename
          path: testpath
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'namespace/testimagename'
        assert td.path == 'testpath'
        assert td.dockerfile == 'Dockerfile'
        assert td.task_type == 'dockerfile'
        assert td.file_dep == None
        assert not td.pull
        assert td.rm == True
        assert td.tags == [('namespace/testimagename',None)]
        assert td.doit_image_name == 'namespace/testimagename'

    def test_path_always_str(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: testimagename
          path: 8
          pull: True
          rm: False # is True by default
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'testimagename'
        assert td.path == '8'
        assert td.dockerfile == 'Dockerfile'
        assert td.task_type == 'dockerfile'
        assert td.pull == True
        assert td.rm == False
        assert td.doit_image_name == 'testimagename'
        
    def test_missing_path_should_error(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: testimagename
        ''')
        with pytest.raises(dodocker.DodockerParseError):
            d = list(t.create_group_data())

    def test_shell(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: testimagename2
          shell_action: make something
          path: testpath2
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'testimagename2'
        assert td.path == 'testpath2'
        assert td.dockerfile == None
        assert td.task_type == 'shell'
        assert td.doit_image_name == 'testimagename2'
        
    def test_git(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: company/solr-typo3:3.1
          depends: company/jre7
          git_url: git@git.somewhere.com:company/dockerimg-solr-typo3 branch/3.1
          path: .
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'company/solr-typo3'
        assert td.path.startswith('dodocker_repos')
        assert td.path.endswith('/.')
        assert td.task_type == 'dockerfile'
        assert td.git_url == 'git@git.somewhere.com:company/dockerimg-solr-typo3'
        assert td.git_checkout_type == 'branch'
        assert td.git_checkout == '3.1'
        assert td.depends_subtask_name == 'company/jre7'
        assert td.dockerfile == 'Dockerfile'
        assert td.tags == [('company/solr-typo3','3.1')]
        assert td.doit_image_name == 'company/solr-typo3:3.1'
        
    def test_git_tags(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: company/solr-typo3:3.1
          depends: company/jre7
          git_url: git@git.somewhere.com:company/dockerimg-solr-typo3 tags/3.1
          path: .
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'company/solr-typo3'
        assert td.path.startswith('dodocker_repos')
        assert td.path.endswith('/.')
        assert td.task_type == 'dockerfile'
        assert td.git_url == 'git@git.somewhere.com:company/dockerimg-solr-typo3'
        assert td.git_checkout_type == 'tags'
        assert td.git_checkout == '3.1'
        assert td.depends_subtask_name == 'company/jre7'
        assert td.dockerfile == 'Dockerfile'
        assert td.tags == [('company/solr-typo3','3.1')]
        assert td.doit_image_name == 'company/solr-typo3:3.1'
        
    def test_git_commit(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: company/solr-typo3:3.1
          depends: company/jre7
          git_url: git@git.somewhere.com:company/dockerimg-solr-typo3 commit/abcde
          path: .
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'company/solr-typo3'
        assert td.path.startswith('dodocker_repos')
        assert td.path.endswith('/.')
        assert td.task_type == 'dockerfile'
        assert td.git_url == 'git@git.somewhere.com:company/dockerimg-solr-typo3'
        assert td.git_checkout_type == 'commit'
        assert td.git_checkout == 'abcde'
        assert td.depends_subtask_name == 'company/jre7'
        assert td.dockerfile == 'Dockerfile'
        assert td.tags == [('company/solr-typo3','3.1')]
        assert td.doit_image_name == 'company/solr-typo3:3.1'

    def test_git_default_master(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: company/solr-typo3:3.1
          depends: company/jre7
          git_url: git@git.somewhere.com:company/dockerimg-solr-typo3
          path: .
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'company/solr-typo3'
        assert td.path.startswith('dodocker_repos')
        assert td.path.endswith('/.')
        assert td.task_type == 'dockerfile'
        assert td.git_url == 'git@git.somewhere.com:company/dockerimg-solr-typo3'
        assert td.git_checkout_type == 'branch'
        assert td.git_checkout == 'master'
        assert td.depends_subtask_name == 'company/jre7'
        assert td.dockerfile == 'Dockerfile'
        assert td.tags == [('company/solr-typo3','3.1')]
        assert td.doit_image_name == 'company/solr-typo3:3.1'
        
    def test_git_wrong_tree_format_should_fail(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: company/solr-typo3:3.1
          depends: company/jre7
          git_url: git@git.somewhere.com:company/dockerimg-solr-typo3 master
          path: .
        ''')
        with pytest.raises(dodocker.DodockerParseError):
            d = list(t.create_group_data())

        
    def test_tags(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage:3.5
          depends: company/jre7
          path: somewhere/else
          file_dep: 
            - Dockerfile
          tags:
            - :3
            - :hey
            - blub:bla
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'someimage'
        assert td.doit_image_name == 'someimage:3.5'
        assert td.file_dep == ['Dockerfile',]
        assert td.tags == [
            ('someimage','3.5'),
            ('someimage','3'),
            ('someimage','hey'),
            ('blub','bla')
        ]

    def test_tags_two_names_with_no_tag(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage
          depends: company/jre7
          path: somewhere/else
          file_dep: 
            - Dockerfile
          tags:
            - someotherimage
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'someimage'
        assert td.doit_image_name == 'someimage'
        assert td.file_dep == ['Dockerfile',]
        assert td.tags == [
            ('someimage',None),
            ('someotherimage',None),
        ]
        
    def test_tags_no_tag_on_image_with_tags(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage
          depends: company/jre7
          path: somewhere/else
          tags:
            - :3
            - :hey
            - blub:bla
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'someimage'
        assert td.doit_image_name == 'someimage'
        assert td.tags == [
            ('someimage',None),
            ('someimage','3'),
            ('someimage','hey'),
            ('blub','bla')
        ]

    def test_explicit_no_tag_in_image_attribute(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage
          depends: company/jre7
          path: somewhere/else
          tags:
            - :3
            - :hey
            - blub:bla
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'someimage'
        assert td.doit_image_name == 'someimage'
        assert td.tags == [
            ('someimage',None),
            ('someimage','3'),
            ('someimage','hey'),
            ('blub','bla')
        ]

    def test_explicit_no_tag_in_tags_attribute(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: "someimage:3"
          depends: company/jre7
          path: somewhere/else
          tags:
            - blub
            - :hey
            - blub:bla
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'someimage'
        assert td.doit_image_name == 'someimage:3'
        assert td.tags == [
            ('someimage','3'),
            ('blub',None),
            ('someimage','hey'),
            ('blub','bla')
        ]

        
    def test_tags_non_unique_tags_in_one_image_should_error(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage
          depends: company/jre7
          path: somewhere/else
          tags:
            - :3
            - :hey
            - :hey
            - blub:bla
        ''')
        with pytest.raises(dodocker.DodockerParseError):
            d = list(t.create_group_data())

    def test_tags_non_unique_tags_in_one_image_should_error_2(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage
          depends: company/jre7
          path: somewhere/else
          tags:
            - someimage
            - :hey
            - blub:bla
        ''')
        with pytest.raises(DodockerParseError):
            d = list(t.create_group_data())
            
    def test_tags_non_unique_tags_in_multiple_images_should_error(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage
          depends: company/jre7
          path: somewhere/else
          tags:
            - :3
            - :hey
        - image: someimage
          depends: company/jre7
          path: somewhere/else
          tags:
            - :4
            - :hey
        ''')
        with pytest.raises(dodocker.DodockerParseError):
            d = list(t.create_group_data())

    def test_shell_with_tags(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: testimagename2
          shell_action: make something
          path: testpath2
          tags:
            - :v1
            - :bla
        ''')
        d = list(t.create_group_data())
        assert len(d) == 1
        td = d[0]
        assert td.bare_image_name == 'testimagename2'
        assert td.path == 'testpath2'
        assert td.dockerfile == None
        assert td.task_type == 'shell'
        assert td.doit_image_name == 'testimagename2'
        assert td.tags == [('testimagename2',None),
                           ('testimagename2','v1'),
                           ('testimagename2','bla')]
            
    def test_parameter(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage
          path: image1
          parameter:
            mode: fixed
            setup:
              - a: one
                b: two
                c: three
                tags:
                  - :v1
              - b: no_default
                tags:
                  - :v2
              - a: eins
                b: zwei
                c: drei
                tags:
                  - :v3
                  - :latest
                  - bla:blub
        ''')
        d = list(t.create_group_data())
        assert len(d) == 3
        td1, td2, td3 = d
        assert td1.buildargs == {'a':'one','b':'two','c':'three'}
        assert td2.buildargs == {'b':'no_default'}
        assert td3.buildargs == {'a':'eins','b':'zwei','c':'drei'}
        assert td1.tags == [('someimage','v1')]
        assert td2.tags == [('someimage','v2')]
        assert td3.tags == [('someimage','v3'),
                            ('someimage','latest'),
                            ('bla','blub')]
        assert td1.doit_image_name == 'someimage:v1'
        assert td2.doit_image_name == 'someimage:v2'
        assert td3.doit_image_name == 'someimage:v3'

    def test_parameter_image_attribute_no_tag_allowed(self):
        t = TaskGroup()
        t.load_task_descriptions(
        '''
        - image: someimage:sometag
          path: image1
          parameter:
            mode: fixed
            setup:
              - a: one
                tags:
                  - :v3
              - a: eins
                tags:
                  - :v5
        ''')
        with pytest.raises(DodockerParseError):
            d = list(t.create_group_data())

#    def test_wrong_type_of_(self):
#        raise

        
