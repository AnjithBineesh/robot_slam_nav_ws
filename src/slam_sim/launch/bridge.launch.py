
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    gazebo_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gazebo_ros_bridge',
        output='screen',

        arguments=[

            # Simulation clock: Gazebo -> ROS 2
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',

            # LiDAR: Gazebo -> ROS 2
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',

            # Odometry: Gazebo -> ROS 2
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',

            # Velocity commands: ROS 2 -> Gazebo
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',

            # Joint states: Gazebo -> ROS 2
            '/world/rooms_world/model/diff_bot/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model',

            # Robot TF: Gazebo -> ROS 2
            '/model/diff_bot/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',

        ],

        remappings=[
            # Gazebo joint states -> ROS joint states
            (
                '/world/rooms_world/model/diff_bot/joint_state',
                '/joint_states'
            ),

            # Gazebo TF -> ROS TF
            (
                '/model/diff_bot/tf',
                '/tf'
            ),
        ],
    )

    return LaunchDescription([
        gazebo_bridge
    ])
