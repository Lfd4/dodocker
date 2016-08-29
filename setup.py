# dodocker setuptools configuration

from setuptools import setup, find_packages
setup(
    name = "dodocker",
    packages = ["dodocker"],
    version = "1.0a01",
    zip_safe = True,
    packages = find_packages(),
    install_requires = ['docker-py',
                        'PyYAML',
                        'doit',
                        'GitPython',
                        ],
    package_data = {},
    author = 'Andreas Elvers',
    author_email = 'andreas@work.de',
    description = 'dodocker is a docker image build tool based on doit and docker-py.',
    license = 'Apache License 2.0',
    keywords = ['docker','authoring','development'],
    download_url = 'https://github.com/nawork/dodocker/tarball/1.0a01',
    url = 'http://www.work.de/dodocker',
    entry_points = {'console_scripts': ['dodocker = dodocker.do:main']}
)
