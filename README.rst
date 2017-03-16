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

    pyfido -u 1112224444 -p MYPASSWORD


Print help

::

    pyfido -h
    usage: pyfido [-h] -u USERNAME [-n NUMBER] -p PASSWORD [-l] [-j] [-t TIMEOUT]

    optional arguments:
      -h, --help            show this help message and exit
      -u USERNAME, --username USERNAME
                            Fido username
      -n NUMBER, --number NUMBER
                            Fido phone number
      -p PASSWORD, --password PASSWORD
                            Password
      -l, --list            List phone numbers
      -j, --json            Json output
      -t TIMEOUT, --timeout TIMEOUT
                            Request timeout

Dev env
#######

::

    virtualenv -p /usr/bin/python3.5 env
    pip install -r requirements.txt 
