from setuptools import setup, find_packages

with open('README.rst', encoding='UTF-8') as f:
    readme = f.read()

setup(
    name='mtr2mqtt',
    version='0.1.0',
    description='MTR receiver readings to MQTT server',
    author='topo',
    author_email='tvallas@iki.fi',
    install_requires=['pyserial', 'paho-mqtt'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mtr2mqtt=mtr2mqtt.cli:main',
        ]
    }
)