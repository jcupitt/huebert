# this is the setup file - run once only to make the package:
# python setup.py sdist
# will make the tarball. This can be unpacked then:
# python setup.py install --prefix=/usr/local/bin

from distutils.core import setup, Extension

setup(name='hubert',
    version='0.1dev',
    packages=['huebert'],
    scripts=['bin/huebert'],
    author='J. Cupitt',
    author_email='jcupitt@gmail.com',
    license='LICENSE.txt',
    description='sound-to-light audio playback', 
    ext_modules=[Extension('huebert.analyse', ['huebert/analyse.c'], 
        libraries=['fftw3'])],
    package_data={'huebert': ['data/*']},
    requires=['request', 'gstreamer'],
    long_description=open('README.md').read(),
)
