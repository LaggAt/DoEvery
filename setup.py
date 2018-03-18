#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2018 Florian Lagg <github@florian.lagg.at>
# Under Terms of GPL v3

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def get_long_description():
    readme_file = "README.md"
    if not os.path.isfile(readme_file):
        return ""
    # Try to transform the README from Markdown to reStructuredText.
    try:
        os.system("pandoc --from=markdown --to=rst --output=README.rst README.md")
        description = open("README.rst").read()
        os.remove("README.rst")
    except Exception:
        description = open(readme_file).read()
    return description

setup(
    name = "DoEvery",
    version = "0.0.1",
    author = "Florian Lagg",
    author_email = "github@florian.lagg.at",
    description = ("Running tasks every x seconds in threads."),
    license = "GPL v3",
    keywords = "threads threading schedule cProfile profiling",
    url = "https://github.com/LaggAt/DimensionTabler",
    packages=find_packages(),
    install_requires=[
        "readchar >= 0.7",
    ],
    long_description=get_long_description(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
        "Topic :: Database",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)