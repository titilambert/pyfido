from pip.req import parse_requirements
from setuptools import setup
from pip.download import PipSession

session = PipSession()
install_reqs = parse_requirements('requirements.txt', session=session)
test_reqs = parse_requirements('test_requirements.txt', session=session)

setup(name='pyfido',
      version='0.1.4',
      description='Get your Fido consumption (wwww.fido.ca)',
      author='Thibault Cohen',
      author_email='titilambert@gmail.com',
      url='http://github.org/titilambert/pyfido',
      packages=['pyfido'],
      entry_points={
          'console_scripts': [
              'pyfido = pyfido.__main__:main'
          ]
      },
      install_requires=[str(r.req) for r in install_reqs],
      tests_require=[str(r.req) for r in test_reqs],
)
