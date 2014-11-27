# coding=utf-8
from __future__ import unicode_literals
from setuptools import setup, find_packages

VERSION = 0.1

with open('requirements_base.txt') as f:
    requirements = f.readlines()

setup(
    name="djangit",
    version=VERSION,
    author="Víðir Valberg Guðmundsson",
    author_email="valberg@orn.li",
    description="A git source code inspection tool.",
    keywords="django git",
    packages=find_packages(exclude=["djangit_project", "djangit_project.*"]),
    zip_safe=False,
    install_requires=[r.strip() for r in requirements],
    include_package_data=True,
)
