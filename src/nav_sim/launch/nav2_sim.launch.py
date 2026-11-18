#!/usr/bin/env python3

"""
Launch Gazebo simulation with Nav2 navigation.

Supports:
    1. AMCL localisation with a saved map.
    2. SLAM-based localisation.
    3. Regulated Pure Pursuit controller (rpp).
    4. DWB local planner (dwb).
"""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml


def launch_navigation(context, *args, **kwargs):
    """Configure and launch localisation and Nav2 stack."""
    nav_sim_dir = get_package_share_directory('nav_sim')
    slam_sim_dir = get_package_share_directory('slam_sim')
    nav2_dir = get_package_share_directory('nav2_bringup')

    slam = LaunchConfiguration('slam')
    controller = context.perform_substitution(
        LaunchConfiguration('controller')
    )
    map_file = LaunchConfiguration('map')
    use_composition = LaunchConfiguration('use_composition')
    startup_delay = float(
        context.perform_substitution(LaunchConfiguration('startup_delay'))
    )

    if controller == 'rpp':
        params_file = os.path.join(
            nav_sim_dir,
            'config',
            'nav2_params.yaml',
        )
    elif controller == 'dwb':
        params_file = os.path.join(
            nav_sim_dir,
            'config',
            'nav2_params_dwb.yaml',
        )
    else:
        raise RuntimeError(
            f"Invalid controller '{controller}'. Choose 'rpp' or 'dwb'."
        )

    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            param_rewrites={
                'use_sim_time': 'true',
                'yaml_filename': map_file,
            },
            convert_types=True,
        ),
        allow_substs=True,
    )

    nav_args = {
        'use_sim_time': 'true',
        'params_file': params_file,
        'autostart': 'true',
        'use_composition': use_composition,
        'container_name': 'nav2_container',
        'use_respawn': 'False',
    }

    # Component container for composed Nav2 bringup (avoids FastRTPS discovery storm)
    nav2_container = Node(
        condition=IfCondition(use_composition),
        name='nav2_container',
        package='rclcpp_components',
        executable='component_container_isolated',
        parameters=[configured_params, {'autostart': True}],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
        output='screen',
    )

    # AMCL localisation (uses set_initial_pose: true at (0, 0, 0) in map frame)
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_dir,
                'launch',
                'localization_launch.py',
            )
        ),
        launch_arguments={
            **nav_args,
            'map': map_file,
        }.items(),
        condition=UnlessCondition(slam),
    )

    # SLAM localisation
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                slam_sim_dir,
                'launch',
                'slam.launch.py',
            )
        ),
        condition=IfCondition(slam),
    )

    # Nav2 navigation stack
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_dir,
                'launch',
                'navigation_launch.py',
            )
        ),
        launch_arguments=nav_args.items(),
    )

    # Delay Nav2 startup until Gazebo, bridge, and robot spawn are ready
    nav_stack = TimerAction(
        period=startup_delay,
        actions=[
            nav2_container,
            localization,
            slam_launch,
            navigation,
        ],
    )

    return [nav_stack]


def generate_launch_description():
    """Generate the Nav2 simulation launch description."""
    slam_sim_dir = get_package_share_directory('slam_sim')
    nav_sim_dir = get_package_share_directory('nav_sim')

    slam_arg = DeclareLaunchArgument(
        'slam',
        default_value='false',
        description='Use SLAM instead of AMCL',
    )

    controller_arg = DeclareLaunchArgument(
        'controller',
        default_value='rpp',
        description='Local controller: rpp or dwb',
    )

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(
            nav_sim_dir,
            'maps',
            'rooms_map.yaml',
        ),
        description='Path to the occupancy map YAML file',
    )

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz',
    )

    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Launch Gazebo GUI',
    )

    use_composition_arg = DeclareLaunchArgument(
        'use_composition',
        default_value='True',
        description='Run Nav2 nodes in a single component container',
    )

    startup_delay_arg = DeclareLaunchArgument(
        'startup_delay',
        default_value='12.0',
        description='Delay (seconds) before starting Nav2',
    )

    # Gazebo simulation (scoped so rviz:='false' does not overwrite our own rviz arg)
    simulation = GroupAction(
        scoped=True,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        slam_sim_dir,
                        'launch',
                        'sim.launch.py',
                    )
                ),
                launch_arguments={
                    'rviz': 'false',
                    'gui': LaunchConfiguration('gui'),
                }.items(),
            ),
        ],
    )

    # Nav2 RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='nav_rviz',
        arguments=[
            '-d',
            os.path.join(
                nav_sim_dir,
                'rviz',
                'nav.rviz',
            ),
        ],
        parameters=[
            {'use_sim_time': True},
        ],
        output='screen',
        condition=IfCondition(
            LaunchConfiguration('rviz')
        ),
    )

    return LaunchDescription([
        slam_arg,
        controller_arg,
        map_arg,
        rviz_arg,
        gui_arg,
        use_composition_arg,
        startup_delay_arg,
        simulation,
        OpaqueFunction(function=launch_navigation),
        rviz_node,
    ])
