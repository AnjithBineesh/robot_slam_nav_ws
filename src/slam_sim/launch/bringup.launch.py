
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    pkg = get_package_share_directory('slam_sim')

    # Launch arguments
    rviz = LaunchConfiguration('rviz')
    gui = LaunchConfiguration('gui')

    # Gazebo simulation launch
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg,
                'launch',
                'sim.launch.py'
            )
        ),
        launch_arguments={
            'rviz': rviz,
            'gui': gui,
        }.items()
    )

    # SLAM Toolbox launch
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg,
                'launch',
                'slam.launch.py'
            )
        )
    )

    # Start SLAM after simulation initialisation
    delayed_slam = TimerAction(
        period=10.0,
        actions=[
            slam_launch
        ]
    )

    return LaunchDescription([

        # Launch arguments
        DeclareLaunchArgument(
            'rviz',
            default_value='true'
        ),

        DeclareLaunchArgument(
            'gui',
            default_value='true'
        ),

        # Start Gazebo and robot
        sim_launch,

        # Start SLAM Toolbox
        delayed_slam,

    ])
