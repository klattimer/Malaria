from setuptools import setup
import setuptools

MALARIA_VERSION = '0.1'
MALARIA_DOWNLOAD_URL = (
    'https://github.com/klattimer/malaria/tarball/' + MALARIA_VERSION
)

setup(
    name='Malaria',
    packages=setuptools.find_packages(),
    version=MALARIA_VERSION,
    description='Malaria monitoring tool.',
    long_description='',
    license='MIT',
    author='Karl Lattimer',
    author_email='karl@qdh.org.uk',
    url='https://github.com/klattimer/malaria',
    download_url=MALARIA_DOWNLOAD_URL,
    entry_points={
        'console_scripts': [
            'malaria=Malaria:main',
            'malaria_setup=Malaria:setup'
        ]
    },
    keywords=[
        'smarthome', 'mqtt', 'malaria', 'iot', 'monitor', 'dnla', 'zeroconf', 'raspberrypi', 'statistics'
    ],
    install_requires=[
        'paho-mqtt',
        'psutil',
        'mdstat',
        'zeroconf',
        'smbus',
        'uptime'
    ],
    data_files=[
        ('data/', ['data/malaria.service']),
        ('data/', ['data/config.json'])
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
    ],
)
