######
Pyfido
######

TODO
####

* Add multi account support

Installation
############

::

    pip install pyfido


Usage
#####

Print your current data

::

    pyfido -n 1112224444 -p MYPASSWORD


Print help

::

    pyfido -h
    usage: pyfido [-h] -n NUMBER -p PASSWORD [-j] [-t TIMEOUT]

    optional arguments:
      -h, --help            show this help message and exit
      -n NUMBER, --number NUMBER
                            Fido phone number
      -p PASSWORD, --password PASSWORD
                            Password
      -j, --json            Json output
      -t TIMEOUT, --timeout TIMEOUT
                            Request timeout



Dev env
#######

::

    virtualenv -p /usr/bin/python3.5 env
    pip install -r requirements.txt 
