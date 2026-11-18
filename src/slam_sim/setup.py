import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'slam_sim'

setup(
    name=package_name,
    version='1.0.0',

    packages=find_packages(exclude=['test']),

    data_files=[
        # Ament package resource marker
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),

        # Package manifest
        (
            os.path.join('share', package_name),
            ['package.xml'],
        ),

        # Launch files
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py'),
        ),

        # SLAM configuration
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*'),
        ),

        # RViz configuration
        (
            os.path.join('share', package_name, 'rviz'),
            glob('rviz/*'),
        ),

        # Robot description
        (
            os.path.join('share', package_name, 'urdf'),
            glob('urdf/*'),
        ),

        # Gazebo Fortress worlds
        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*'),
        ),
    ],

    install_requires=['setuptools'],

    zip_safe=True,

    maintainer='Anjith Bineesh',
    maintainer_email='anjithbineesh@gmail.com',

    description=(
        'ROS 2 Humble SLAM simulation using Gazebo Fortress '
        'and SLAM Toolbox'
    ),

    license='Apache-2.0',

    tests_require=['pytest'],

)
