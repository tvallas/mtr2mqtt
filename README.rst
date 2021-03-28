mtr2mqtt
========

CLI tool for reading Nokeval MTR wireless receivers and forwarding readings as json objects to mqtt topic

Preparing the Development
-------------------------

1. Ensure ``pip`` and ``pipenv`` are installed.
2. Clone repository ``git clone git @github.com:tvallas/mtr2mqtt``
3. ``cd`` into the repository.
4. Fetch development dependencies ``make install``
5. Activate virtualenv: ``pipenv shell``

Usage
-----

Pass in serial port settings and mqtt server address, if not provided serial port autodetection is used and localhost for mqtt.

example

::

    $ mtr2mqtt --serial-port /dev/ttyUSB12345 --mqtt 192.168.1.2



Running Tests
-------------


Run tests locally using ``make`` if virtualenv is active:

::

    $ make test

If virtualenv isn't active then use:

::

    $ pipenv run make
