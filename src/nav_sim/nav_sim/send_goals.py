#!/usr/bin/env python3

"""Send single or multi-waypoint navigation goals to Nav2."""

import argparse
import math
import sys

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy


# Safe free-space waypoints in the rooms_map frame (map = gazebo + (4.0, 1.5))
ROOM_WAYPOINTS = {
    'sw': (0.0, 0.0, 0.0),
    'center': (4.0, 1.5, 0.0),
    'nw': (1.5, 4.0, 1.57),
    'ne': (6.5, 3.5, 0.0),
    'se': (6.5, -0.5, -1.57),
}

DEFAULT_PATROL = ['center', 'nw', 'ne', 'se', 'sw']


def make_pose(x: float, y: float, yaw: float) -> PoseStamped:
    """Create a PoseStamped in the map frame with zero stamp (latest TF)."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    # Leave header.stamp at (0, 0) so TF2 uses the latest transform regardless of sim/wall clock.
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = 0.0
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def parse_args(argv):
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description='Send navigation goals to Nav2 using BasicNavigator.'
    )
    parser.add_argument(
        '--room',
        choices=list(ROOM_WAYPOINTS.keys()),
        help='Navigate to a named room waypoint (sw, center, nw, ne, se).',
    )
    parser.add_argument(
        '--patrol',
        action='store_true',
        help='Patrol through all rooms (center -> nw -> ne -> se -> sw).',
    )
    parser.add_argument('--x', type=float, help='Goal X coordinate in map frame (m).')
    parser.add_argument('--y', type=float, help='Goal Y coordinate in map frame (m).')
    parser.add_argument(
        '--yaw',
        type=float,
        default=0.0,
        help='Goal yaw orientation in radians (default: 0.0).',
    )
    parser.add_argument(
        '--slam',
        action='store_true',
        help='Use when Nav2 is running with slam:=true (skips waiting for AMCL).',
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Run the navigation goal sender."""
    cli_args = rclpy.utilities.remove_ros_args(sys.argv if argv is None else argv)[1:]
    args = parse_args(cli_args)

    rclpy.init(args=argv)
    navigator = BasicNavigator()

    localizer = 'bt_navigator' if args.slam else 'amcl'
    navigator.get_logger().info(f'Waiting for Nav2 to become active (localizer={localizer})...')
    navigator.waitUntilNav2Active(localizer=localizer)

    if args.x is not None and args.y is not None:
        goals = [(f'custom ({args.x:.2f}, {args.y:.2f})', args.x, args.y, args.yaw)]
    elif args.room:
        gx, gy, gyaw = ROOM_WAYPOINTS[args.room]
        goals = [(args.room, gx, gy, gyaw)]
    else:
        # Default to full room patrol if no specific goal is given
        goals = [(name, *ROOM_WAYPOINTS[name]) for name in DEFAULT_PATROL]

    exit_code = 0
    try:
        for label, gx, gy, gyaw in goals:
            navigator.get_logger().info(
                f'Navigating to {label}: x={gx:.2f}, y={gy:.2f}, yaw={gyaw:.2f}'
            )
            goal_pose = make_pose(gx, gy, gyaw)
            navigator.goToPose(goal_pose)

            last_log_sec = -1
            while not navigator.isTaskComplete():
                feedback = navigator.getFeedback()
                if feedback and feedback.navigation_time.sec != last_log_sec:
                    if feedback.navigation_time.sec % 5 == 0:
                        last_log_sec = feedback.navigation_time.sec
                        navigator.get_logger().info(
                            f'[{label}] Distance remaining: '
                            f'{feedback.distance_remaining:.2f} m'
                        )

            result = navigator.getResult()
            if result == TaskResult.SUCCEEDED:
                navigator.get_logger().info(f'Reached goal: {label}')
            elif result == TaskResult.CANCELED:
                navigator.get_logger().warn(f'Goal canceled: {label}')
                exit_code = 1
                break
            else:
                navigator.get_logger().error(f'Goal failed: {label} (result={result})')
                exit_code = 1
                break
    except KeyboardInterrupt:
        navigator.get_logger().info('Navigation interrupted; canceling active goal.')
        navigator.cancelTask()
    finally:
        navigator.destroy_node()
        rclpy.shutdown()

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
