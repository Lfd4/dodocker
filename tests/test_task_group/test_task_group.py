from dodocker.do import TaskGroup
import os, pytest

class TestSimpleTask:
    dodocker_yaml = """
    - image: test
      path: test
    """

    def test_parsing(self):
        tg = TaskGroup()
        tg.load_task_descriptions(self.dodocker_yaml)
        gd = list(tg.create_group_data())
        pytest.set_trace()
