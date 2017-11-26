from pip.req import parse_requirements
from setuptools import setup
from pip.download import PipSession

session = PipSession()
install_reqs = parse_requirements('requirements.txt', session=session)
test_reqs = parse_requirements('test_requirements.txt', session=session)

setup(name='pyfido',
      version='2.0.1',
      description='Get your Fido consumption (wwww.fido.ca)',
      author='Thibault Cohen',
      author_email='titilambert@gmail.com',
      url='http://github.com/titilambert/pyfido',
      package_data={'': ['LICENSE.txt']},
      include_package_data=True,
      packages=['pyfido'],
      entry_points={
          'console_scripts': [
              'pyfido = pyfido.__main__:main'
          ]
      },
      license='Apache 2.0',
      install_requires=[str(r.req) for r in install_reqs],
      tests_require=[str(r.req) for r in test_reqs],
      classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
)
