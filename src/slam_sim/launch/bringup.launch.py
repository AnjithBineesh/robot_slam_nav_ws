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
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg = get_package_share_directory('slam_sim')

    # Launch arguments
    rviz = LaunchConfiguration('rviz')
    gui = LaunchConfiguration('gui')
    lidar_update_rate = LaunchConfiguration('lidar_update_rate')
    lidar_noise_stddev = LaunchConfiguration('lidar_noise_stddev')
    wheel_radius = LaunchConfiguration('wheel_radius')
    drive_wheel_radius = LaunchConfiguration('drive_wheel_radius')
    wheel_separation = LaunchConfiguration('wheel_separation')
    drive_wheel_separation = LaunchConfiguration('drive_wheel_separation')
    wheel_mu = LaunchConfiguration('wheel_mu')
    odom_translation_noise_stddev = LaunchConfiguration(
        'odom_translation_noise_stddev'
    )
    odom_yaw_noise_stddev = LaunchConfiguration('odom_yaw_noise_stddev')
    odom_noise_seed = LaunchConfiguration('odom_noise_seed')

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
            'lidar_update_rate': lidar_update_rate,
            'lidar_noise_stddev': lidar_noise_stddev,
            'wheel_radius': wheel_radius,
            'drive_wheel_radius': drive_wheel_radius,
            'wheel_separation': wheel_separation,
            'drive_wheel_separation': drive_wheel_separation,
            'wheel_mu': wheel_mu,
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

    scan_monitor = Node(
        package='slam_sim',
        executable='scan_monitor',
        name='scan_monitor',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    odometry_monitor = Node(
        package='slam_sim',
        executable='odometry_monitor',
        name='odometry_monitor',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    odometry_noise = Node(
        package='slam_sim',
        executable='odometry_noise',
        name='odometry_noise',
        output='screen',
        parameters=[{
            'translation_noise_stddev': ParameterValue(
                odom_translation_noise_stddev,
                value_type=float,
            ),
            'yaw_noise_stddev': ParameterValue(
                odom_yaw_noise_stddev,
                value_type=float,
            ),
            'noise_seed': ParameterValue(
                odom_noise_seed,
                value_type=int,
            ),
        }],
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
            description='Wheel radius in metres'
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
        DeclareLaunchArgument(
            'odom_translation_noise_stddev',
            default_value='0.0',
            description='Gaussian forward odometry noise per moving update in metres'
        ),
        DeclareLaunchArgument(
            'odom_yaw_noise_stddev',
            default_value='0.0',
            description='Gaussian yaw odometry noise per moving update in radians'
        ),
        DeclareLaunchArgument(
            'odom_noise_seed',
            default_value='42',
            description='Random seed for reproducible odometry noise'
        ),

        # Start Gazebo and robot
        sim_launch,

        # Start SLAM Toolbox
        delayed_slam,
        scan_monitor,
        odometry_monitor,
        odometry_noise,

    ])
