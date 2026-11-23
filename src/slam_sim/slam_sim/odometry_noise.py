import copy
import math
import random

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage


def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_from_quaternion(quaternion):
    return math.atan2(
        2.0 * (quaternion.w * quaternion.z +
               quaternion.x * quaternion.y),
        1.0 - 2.0 * (quaternion.y ** 2 + quaternion.z ** 2),
    )


class DifferentialDriveNoiseModel:

    def __init__(self, translation_stddev, yaw_stddev, seed):
        if not math.isfinite(translation_stddev) or translation_stddev < 0:
            raise ValueError('translation_stddev must be finite and non-negative')
        if not math.isfinite(yaw_stddev) or yaw_stddev < 0:
            raise ValueError('yaw_stddev must be finite and non-negative')

        self.translation_stddev = translation_stddev
        self.yaw_stddev = yaw_stddev
        self.random = random.Random(seed)
        self.previous_true_pose = None
        self.noisy_pose = None
        self.translation_variance = 0.0
        self.yaw_variance = 0.0
        self.last_update_moved = False

    def update(self, x, y, yaw):
        true_pose = (x, y, normalize_angle(yaw))
        if self.previous_true_pose is None:
            self.previous_true_pose = true_pose
            self.noisy_pose = true_pose
            return self.noisy_pose

        previous_x, previous_y, previous_yaw = self.previous_true_pose
        noisy_x, noisy_y, noisy_yaw = self.noisy_pose
        dx = x - previous_x
        dy = y - previous_y
        forward = math.cos(previous_yaw) * dx + math.sin(previous_yaw) * dy
        lateral = -math.sin(previous_yaw) * dx + math.cos(previous_yaw) * dy
        yaw_delta = normalize_angle(true_pose[2] - previous_yaw)
        self.last_update_moved = (
            abs(forward) + abs(lateral) + abs(yaw_delta) > 1e-12
        )

        if self.last_update_moved:
            forward += self.random.gauss(0.0, self.translation_stddev)
            yaw_delta += self.random.gauss(0.0, self.yaw_stddev)
            self.translation_variance += self.translation_stddev ** 2
            self.yaw_variance += self.yaw_stddev ** 2

            noisy_x += math.cos(noisy_yaw) * forward - math.sin(noisy_yaw) * lateral
            noisy_y += math.sin(noisy_yaw) * forward + math.cos(noisy_yaw) * lateral
            noisy_yaw = normalize_angle(noisy_yaw + yaw_delta)

        self.previous_true_pose = true_pose
        self.noisy_pose = (noisy_x, noisy_y, noisy_yaw)
        return self.noisy_pose


class OdometryNoiseNode(Node):

    def __init__(self):
        super().__init__('odometry_noise')
        self.declare_parameter('translation_noise_stddev', 0.0)
        self.declare_parameter('yaw_noise_stddev', 0.0)
        self.declare_parameter('noise_seed', 42)

        translation_stddev = float(
            self.get_parameter('translation_noise_stddev').value
        )
        yaw_stddev = float(self.get_parameter('yaw_noise_stddev').value)
        noise_seed = int(self.get_parameter('noise_seed').value)
        self.noise_model = DifferentialDriveNoiseModel(
            translation_stddev,
            yaw_stddev,
            noise_seed,
        )

        self.odom_publisher = self.create_publisher(Odometry, '/odom', 20)
        self.tf_publisher = self.create_publisher(TFMessage, '/tf', 20)
        self.subscription = self.create_subscription(
            Odometry,
            '/odom_raw',
            self.odom_callback,
            20,
        )

    def odom_callback(self, msg):
        noisy_msg = copy.deepcopy(msg)
        position = msg.pose.pose.position
        yaw = yaw_from_quaternion(msg.pose.pose.orientation)
        noisy_x, noisy_y, noisy_yaw = self.noise_model.update(
            position.x,
            position.y,
            yaw,
        )

        noisy_msg.pose.pose.position.x = noisy_x
        noisy_msg.pose.pose.position.y = noisy_y
        noisy_msg.pose.pose.orientation.x = 0.0
        noisy_msg.pose.pose.orientation.y = 0.0
        noisy_msg.pose.pose.orientation.z = math.sin(noisy_yaw / 2.0)
        noisy_msg.pose.pose.orientation.w = math.cos(noisy_yaw / 2.0)
        noisy_msg.pose.covariance[0] += self.noise_model.translation_variance
        noisy_msg.pose.covariance[7] += self.noise_model.translation_variance
        noisy_msg.pose.covariance[35] += self.noise_model.yaw_variance
        self.odom_publisher.publish(noisy_msg)

        transform = TransformStamped()
        transform.header = msg.header
        transform.child_frame_id = msg.child_frame_id
        transform.transform.translation.x = noisy_x
        transform.transform.translation.y = noisy_y
        transform.transform.translation.z = position.z
        transform.transform.rotation = noisy_msg.pose.pose.orientation
        self.tf_publisher.publish(TFMessage(transforms=[transform]))


def main(args=None):
    rclpy.init(args=args)
    node = OdometryNoiseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
