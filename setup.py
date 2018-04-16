from setuptools import setup

install_requires = list(val.strip() for val in open('requirements.txt'))
tests_require = list(val.strip() for val in open('test_requirements.txt'))

setup(name='pyfido',
      version='2.1.0',
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
      install_requires=install_requires,
      tests_require=tests_require,
      classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
)
