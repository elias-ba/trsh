#!/usr/bin/env python3
from setuptools import setup
from pathlib import Path

readme = Path('README.md').read_text() if Path('README.md').exists() else ''

setup(
    name='trsh',
    version='1.0.0',
    description='Delete with confidence, restore with ease',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Elias W. BA',
    author_email='eliaswalyba@gmail.com',
    url='https://github.com/yourusername/trsh',
    license='MIT',
    py_modules=['trsh'],
    entry_points={
        'console_scripts': [
            'trsh=trsh:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)