# dodocker setuptools configuration

from setuptools import setup, find_packages
setup(
    name = "dodocker",
    version = "0.5",
    zip_safe = True,
    packages = find_packages(),
    install_requires = ['docker-py>=1.3.0,<2',
                        'PyYAML>=3.11,<4',
                        'doit==0.29',
                        'GitPython==1.0.1',
                        ],
    package_data = {},
    author = 'Andreas Elvers',
    author_email = 'andreas@work.de',
    description = 'Dodocker is a docker image build tool based on doit.',
    license = 'Apache License 2.0',
    keywords = 'docker',
    url = 'http://www.work.de/dodocker',
    entry_points = {'console_scripts': ['dodocker = dodocker.do:main']}
)
