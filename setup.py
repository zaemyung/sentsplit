import os
from distutils.util import convert_path

from setuptools import find_packages, setup

meta = {}
meta_path = convert_path('sentsplit/meta_data.py')
with open(meta_path) as meta_file:
    exec(meta_file.read(), meta)


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
