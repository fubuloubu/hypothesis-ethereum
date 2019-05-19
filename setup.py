#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)

extras_require = {
    'test': [
        "pytest>=4.4.0",
        "pytest-xdist",
        "tox>=2.9.1,<3",
    ],
    'lint': [
        'black>=18.6b4,<19',
        "flake8==3.4.1",
        "isort>=4.2.15,<5",
        "mypy<0.600",
    ],
    'doc': [
        "Sphinx>=1.6.5,<2",
        "sphinx_rtd_theme>=0.1.9",
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "pytest-watch>=4.1.0,<5",
        "wheel",
        "twine",
        "ipython",
        "vyper",
    ],
}

extras_require['dev'] = (
    extras_require['dev'] +
    extras_require['test'] +
    extras_require['lint'] +
    extras_require['doc']
)

setup(
    name='hypothesis-ethereum',
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version='0.0.1-alpha.1',
    description="""hypothesis-ethereum: Hypothesis library for ethereum projects.""",
    long_description_markdown_filename='README.md',
    author='hypothesis-ethereum-contributors',
    author_email='',
    url='https://github.com/fubuloubu/hypothesis-ethereum',
    include_package_data=True,
    install_requires=[
        'hypothesis>=4.23.5',
        'eth_abi[tools] @ https://github.com/davesque/eth-abi/archive/tools-submodule.zip',
        'web3[tester]>=5.0.0b2',
    ],
    setup_requires=['setuptools-markdown'],
    python_requires='>=3.6, <4',
    extras_require=extras_require,
    py_modules=['hypothesis_ethereum'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
