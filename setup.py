from setuptools import setup, find_packages

with open('README.rst', encoding='UTF-8') as f:
    readme = f.read()

__version__ = "0.3.1"

setup(
    name='mtr2mqtt',
    version=__version__,
    description='MTR receiver readings to MQTT server',
    author='topo',
    author_email='tvallas@iki.fi',
    url='https://github.com/tvallas/mtr2mqtt',
    install_requires=['pyserial', 'paho-mqtt', 'PyYAML'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mtr2mqtt=mtr2mqtt.cli:main',
        ]
    }
)