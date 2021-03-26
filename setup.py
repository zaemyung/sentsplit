import os
from distutils.util import convert_path

from setuptools import find_packages, setup

# read meta-data of the project
meta = {}
meta_path = convert_path('sentsplit/meta_data.py')
with open(meta_path) as meta_file:
    exec(meta_file.read(), meta)

# read the contents README.md file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


def requirements():
    reqfile = 'requirements.txt'
    with open(os.path.join(os.path.dirname(__file__), reqfile)) as f:
        ret = []
        for eachline in f.read().splitlines():
            if eachline.startswith("-"):
                continue
            ret.append(eachline)
        return ret


setup(name='sentsplit',
      version=meta['version'],
      description=meta['description'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=meta['author'],
      author_email=meta['author_email'],
      url=meta['url'],
      packages=find_packages(),
      entry_points={
          'console_scripts': ['sentsplit=sentsplit:main'],
      },
      include_package_data=True,
      install_requires=requirements(),
      python_requires='>=3.6',
)
