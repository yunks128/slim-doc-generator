#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="slim-doc-generator",
    version="0.1.0",
    author="SLIM Team",
    author_email="slim@example.com",
    description="Documentation generator that uses SLIM docsite template and AI enhancement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NASA-AMMOS/slim-doc-generator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "gitpython>=3.1.0",
        "pyyaml>=6.0",
        "openai>=1.0.0",
        "click>=8.0.0",
        "jinja2>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "slim-doc-generator=slim_doc_generator.cli:main",
        ],
    },
)