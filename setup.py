### Go back and revise this once the package is actually written.

 from setuptools import setup

 setup(
   name='nest',
   version='0.1.0',
   author='Bob Jenkins & Marc Teale',
   author_email='friendjenkins@gmail.com & marc.teale@gmail.com',
   packages=['package_name', 'package_name.test'],
   scripts=['bin/script1','bin/script2'],
   url='http://pypi.python.org/pypi/PackageName/',
   license='LICENSE.txt',
   description='An awesome package that does something',
   long_description=open('README.txt').read(),
   install_requires=[
       "Django >= 1.1.1",
       "pytest",
   ],
)