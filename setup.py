from setuptools import setup

setup(name='snappy',
      version='0.1',
      url='http://github.com/eivindbergem/snappy',
      author='Eivind Alexander Bergem',
      author_email='eivind.bergem@gmail.com',
      license='GPL',
      packages=['snappy'],
      scripts=['bin/snappy'],
      test_suite='nose.collector',
      tests_require=['nose'])
