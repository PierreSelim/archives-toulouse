"""Setup script."""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import archivestls
    version = archivestls.__version__
except ImportError:
    version = 'Undefined'


classifiers = ['Development Status :: 4 - Beta',
               'Environment :: Console',
               'Intended Audience :: Developers',
               'Intended Audience :: Science/Research',
               'License :: OSI Approved :: MIT License',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Utilities']

packages = ['archivestls']
requires = []

setup(name='archivestls',
      version=version,
      author='PierreSelim',
      author_email='ps.huard@gmail.com',
      url='http://github.com/PierreSelim/archivestls',
      description='Mass Upload for Toulouse Archives Collections',
      long_description="""...""",
      license='MIT',
      packages=packages,
      install_requires=requires,
classifiers=classifiers)
