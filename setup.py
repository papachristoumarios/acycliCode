import setuptools
from distutils.core import setup

setup(name='acycliCode',
      version='1.0',
      description='Testing Routine for detecting layering violations built with Python 3.x and GNU Cflow',
      author='Marios Papachristou',
      author_email='papachristoumarios@gmail.com',
      url='https://github.com/papachristoumarios/acycliCode',
      scripts=['acycliCode/acyclicode.py'],
      packages=['acycliCode'],
     )
