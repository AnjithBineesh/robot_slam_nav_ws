
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg = get_package_share_directory('slam_sim')

    # Launch arguments
    world = LaunchConfiguration('world')
    use_rviz = LaunchConfiguration('rviz')
    gui = LaunchConfiguration('gui')
    lidar_update_rate = LaunchConfiguration('lidar_update_rate')
    lidar_noise_stddev = LaunchConfiguration('lidar_noise_stddev')
    wheel_radius = LaunchConfiguration('wheel_radius')
    drive_wheel_radius = LaunchConfiguration('drive_wheel_radius')
    wheel_separation = LaunchConfiguration('wheel_separation')
    drive_wheel_separation = LaunchConfiguration('drive_wheel_separation')
    wheel_mu = LaunchConfiguration('wheel_mu')

    # File paths
    robot_file = os.path.join(
        pkg,
        'urdf',
        'robot.urdf.xacro'
    )

    rviz_config = os.path.join(
        pkg,
        'rviz',
        'slam.rviz'
    )

    bridge_file = os.path.join(
        pkg,
        'launch',
        'bridge.launch.py'
    )

    # Generate robot description from Xacro
    robot_description = ParameterValue(
        Command([
            'xacro ',
            robot_file,
            ' lidar_update_rate:=',
            lidar_update_rate,
            ' lidar_noise_stddev:=',
            lidar_noise_stddev,
            ' wheel_radius:=',
            wheel_radius,
            ' drive_wheel_radius:=',
            drive_wheel_radius,
            ' wheel_separation:=',
            wheel_separation,
            ' drive_wheel_separation:=',
            drive_wheel_separation,
            ' wheel_mu:=',
            wheel_mu,
        ]),
        value_type=str
    )

    # Gazebo Fortress - GUI mode
    gazebo_gui = ExecuteProcess(
        cmd=[
            'ign',
            'gazebo',
            world,
            '-r'
        ],
        output='screen',
        condition=IfCondition(gui)
    )

    # Gazebo Fortress - headless mode
    gazebo_headless = ExecuteProcess(
        cmd=[
            'ign',
            'gazebo',
            '-s',
            world,
            '-r'
        ],
        output='screen',
        condition=UnlessCondition(gui)
    )

    # Publish robot description and static transforms
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {
                'robot_description': robot_description,
                'use_sim_time': True
            }
        ]
    )

    # Spawn robot in Gazebo Fortress
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_diff_bot',
        arguments=[
            '-name', 'diff_bot',
            '-topic', 'robot_description',
            '-x', '-4.0',
            '-y', '-1.5',
            '-z', '0.0',
            '-Y', '0.0'
        ],
        output='screen'
    )

    # Spawn after Gazebo and robot description are ready
    delayed_spawn = TimerAction(
        period=5.0,
        actions=[
            spawn_robot
        ]
    )

    # Include Gazebo-ROS bridge
    bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            bridge_file
        )
    )

    delayed_bridge = TimerAction(
        period=2.0,
        actions=[
            bridge_launch
        ]
    )

    # RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=[
            '-d',
            rviz_config
        ],
        parameters=[
            {
                'use_sim_time': True
            }
        ],
        condition=IfCondition(use_rviz),
        output='screen'
    )

    return LaunchDescription([

        # Launch arguments
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(
                pkg,
                'worlds',
                'rooms.sdf'
            )
        ),

        DeclareLaunchArgument(
            'rviz',
            default_value='true'
        ),

        DeclareLaunchArgument(
            'gui',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'lidar_update_rate',
            default_value='10',
            description='LiDAR scan update rate in Hz'
        ),
        DeclareLaunchArgument(
            'lidar_noise_stddev',
            default_value='0.0',
            description='Gaussian LiDAR range noise standard deviation in metres'
        ),
        DeclareLaunchArgument(
            'wheel_radius',
            default_value='0.05',
            description='Physical and Gazebo wheel radius in metres'
        ),
        DeclareLaunchArgument(
            'wheel_separation',
            default_value='0.34',
            description='Physical wheel separation in metres'
        ),
        DeclareLaunchArgument(
            'drive_wheel_radius',
            default_value='0.05',
            description='Differential-drive odometry wheel radius in metres'
        ),
        DeclareLaunchArgument(
            'drive_wheel_separation',
            default_value='0.31',
            description='Differential-drive odometry wheel separation in metres'
        ),
        DeclareLaunchArgument(
            'wheel_mu',
            default_value='1.0',
            description='Wheel-ground friction coefficient'
        ),

        # Start Gazebo
        gazebo_gui,
        gazebo_headless,

        # Start ROS nodes
        robot_state_publisher,

        # Start bridge and spawn robot
        delayed_bridge,
        delayed_spawn,

        # Start RViz
        rviz

    ])
