import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class OdometryMonitor(Node):
    def __init__(self):
        super().__init__('odometry_monitor')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            20,
        )
        self.last_position = None
        self.distance = 0.0
        self.start_position = None

    def odom_callback(self, msg):
        position = msg.pose.pose.position
        current = (position.x, position.y)

        if self.start_position is None:
            self.start_position = current

        if self.last_position is not None:
            dx = current[0] - self.last_position[0]
            dy = current[1] - self.last_position[1]
            self.distance += math.hypot(dx, dy)

        self.last_position = current

        if not hasattr(self, '_report_count'):
            self._report_count = 0
        self._report_count += 1
        if self._report_count % 100 == 0:
            start_dx = current[0] - self.start_position[0]
            start_dy = current[1] - self.start_position[1]
            travel = math.hypot(start_dx, start_dy)
            covariance = msg.pose.covariance
            nonzero_covariance = sum(value != 0.0 for value in covariance)
            self.get_logger().info(
                f'odometry_x={current[0]:.3f} odometry_y={current[1]:.3f} '
                f'displacement={travel:.3f} incremental_path={self.distance:.3f} '
                f'nonzero_pose_covariance_entries={nonzero_covariance}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = OdometryMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
