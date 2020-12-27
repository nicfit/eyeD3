
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='eyeD3',
    version='0.9.6a0',
    description='Python audio data toolkit (ID3 and MP3)',
    python_requires='==3.*,>=3.6.0',
    author='Travis Shirk',
    author_email='travis@pobox.com',
    license='GPL-3.0-or-later',
    keywords='id3 mp3 python',
    classifiers=['Environment :: Console', 'Intended Audience :: End Users/Desktop', 'Topic :: Multimedia :: Sound/Audio :: Editors', 'Topic :: Software Development :: Libraries :: Python Modules', 'Intended Audience :: Developers', 'Operating System :: POSIX', 'Natural Language :: English', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Programming Language :: Python', 'Programming Language :: Python :: 3.6', 'Programming Language :: Python :: 3.7', 'Programming Language :: Python :: 3.8'],
    entry_points={"console_scripts": ["eyeD3 = eyed3.main:_main"]},
    packages=['eyed3', 'eyed3.id3', 'eyed3.mp3', 'eyed3.plugins', 'eyed3.utils'],
    package_dir={"": "."},
    package_data={"eyed3.plugins": ["*.ebnf"]},
    install_requires=['coverage[toml]==5.*,>=5.3.1', 'dataclasses==0.*,>=0.8.0; python_version == "3.6.*" and python_version >= "3.6.0"', 'deprecation==2.*,>=2.1.0', 'filetype==1.*,>=1.0.7', 'sphinx-issues==1.*,>=1.2.0'],
    dependency_links=['git+https://github.com/nicfit/gitchangelog.git@nicfit.py#egg=gitchangelog'],
    extras_require={"art-plugin": ["pillow==8.*,>=8.0.1", "pylast==4.*,>=4.0.0", "requests==2.*,>=2.25.0"], "dev": ["check-manifest==0.*,>=0.45.0", "cogapp==3.*,>=3.0.0", "gitchangelog", "nicfit.py[cookiecutter]==0.*,>=0.8.7", "paver==1.*,>=1.3.4", "regarding==0.*,>=0.1.4", "sphinx==3.*,>=3.4.1", "sphinx-rtd-theme==0.*,>=0.5.0", "twine==3.*,>=3.3.0", "wheel==0.*,>=0.36.2"], "display-plugin": ["grako==3.*,>=3.99.9"], "test": ["factory-boy==3.*,>=3.1.0", "flake8==3.*,>=3.8.4", "pytest==6.*,>=6.2.1", "pytest-cov==2.*,>=2.10.1", "tox==3.*,>=3.20.1"], "yaml-plugin": ["ruamel.yaml==0.*,>=0.16.12"]},
)
