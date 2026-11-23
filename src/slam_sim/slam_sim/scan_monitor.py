import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class ScanMonitor(Node):
    def __init__(self):
        super().__init__('scan_monitor')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10,
        )
        self.last_stamp = None
        self.intervals = []
        self.scan_count = 0
        self.create_timer(5.0, self.report)

    def scan_callback(self, msg):
        stamp = self.get_clock().now().nanoseconds
        if self.last_stamp is not None:
            interval = (stamp - self.last_stamp) / 1e9
            if interval > 0:
                self.intervals.append(interval)
                if len(self.intervals) > 100:
                    self.intervals.pop(0)
        self.last_stamp = stamp
        self.scan_count += 1

    def report(self):
        if not self.intervals:
            self.get_logger().info('No LiDAR scans received yet')
            return

        mean_interval = sum(self.intervals) / len(self.intervals)
        measured_rate = 1.0 / mean_interval
        self.get_logger().info(
            f'scan_count={self.scan_count} measured_rate_hz='
            f'{measured_rate:.3f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = ScanMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
