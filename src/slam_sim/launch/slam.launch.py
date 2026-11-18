
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # Get package directory
    pkg = get_package_share_directory('slam_sim')

    # SLAM Toolbox configuration
    slam_config = os.path.join(
        pkg,
        'config',
        'slam_toolbox.yaml'
    )

    # Asynchronous SLAM Toolbox node
    slam_toolbox = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',

        parameters=[
            slam_config,
            {
                'use_sim_time': True
            }
        ]
    )

    return LaunchDescription([
        slam_toolbox
    ])
