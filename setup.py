# this is the setup file - run once only to make the package:
# python setup.py sdist
# will make the tarball. This can be unpacked then:
# python setup.py install --prefix=/usr/local/bin

from distutils.core import setup, Extension

import commands

# from http://code.activestate.com/recipes/502261-python-distutils-pkg-config
def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % 
                                    ' '.join(packages)).split():
        if flag_map.has_key(token[:2]):
            kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else: # throw others to extra_link_args
            kw.setdefault('extra_link_args', []).append(token)

    for k, v in kw.iteritems(): # remove duplicated
        kw[k] = list(set(v))

    return kw

setup(name='hubert',
    version='0.1dev',
    packages=['huebert'],
    scripts=['bin/huebert'],
    author='J. Cupitt',
    author_email='jcupitt@gmail.com',
    license='LICENSE.txt',
    description='sound-to-light audio playback', 
    ext_modules=[Extension('huebert.signal', ['huebert/signal.c'], 
      **pkgconfig('glib-2.0'))],
    package_data={'huebert': ['data/*']},
    requires=['request', 'gstreamer'],
    long_description=open('README.md').read(),
)
