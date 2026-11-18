from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'nav_sim'

setup(
    name=package_name,
    version='0.0.1',

    packages=find_packages(exclude=['test']),

    data_files=[
        # Package resource
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),

        # Package manifest
        (
            os.path.join('share', package_name),
            ['package.xml']
        ),

        # Launch files
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),

        # Nav2 configuration
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')
        ),

        # Map files
        (
            os.path.join('share', package_name, 'maps'),
            glob('maps/*.yaml') + glob('maps/*.pgm')
        ),

        # RViz configuration
        (
            os.path.join('share', package_name, 'rviz'),
            glob('rviz/*.rviz')
        ),
    ],

    install_requires=['setuptools'],

    zip_safe=True,

    maintainer='Anjith Bineesh',
    maintainer_email='anjithbineesh@gmail.com',

    description='Nav2 navigation package for differential drive robot simulation.',

    license='Apache-2.0',

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'send_goals = nav_sim.send_goals:main',
        ],
    },
)