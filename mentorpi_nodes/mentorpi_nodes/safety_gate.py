import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_srvs.srv import Trigger, SetBool


def clamp(value, low, high):
    """Keep value between low and high."""
    # TODO 1: return value, but never below low and never above high.
    # Hint: combine max() and min(), like Monday's lecture.
    return max(low, min(value, high))


class SafetyGate(Node):

    def __init__(self):
        super().__init__('safety_gate')

        # A ROS parameter: the speed limit, with a default value
        self.declare_parameter('max_speed', 0.3)

        # The node's on/off state, stored on self so callbacks can read it
        self.enabled = True

        # Listen for raw commands, and publish the limited ones
        self.sub = self.create_subscription(
            TwistStamped, 'cmd_vel_raw', self.on_cmd_vel_raw, 10)
        self.pub = self.create_publisher(TwistStamped, 'cmd_vel', 10)

        # Offer two services
        self.create_service(Trigger, 'stop', self.on_stop)
        self.create_service(SetBool, 'enable_motion', self.on_enable_motion)

        self.get_logger().info('safety_gate is ready')

    def on_cmd_vel_raw(self, msg):
        # Motion off: send zeros and stop here
        if not self.enabled:
            self.publish_zero()
            return

        # Read the speed limit fresh each time, so 'ros2 param set' works right away
        limit = self.get_parameter('max_speed').value

        out = TwistStamped()
        out.header = msg.header
        out.twist.linear.x = clamp(msg.twist.linear.x, -limit, limit)
        out.twist.linear.y = clamp(msg.twist.linear.y, -limit, limit)
        out.twist.angular.z = msg.twist.angular.z
        self.pub.publish(out)

    def publish_zero(self):
        # A new TwistStamped is all zeros, so publishing one is a stop command
        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(out)

    def on_stop(self, request, response):
        # TODO 2: send one zero command, then fill in the response.
        # Hint: self.publish_zero(), response.success (True), response.message ("On_stop command")
        self.publish_zero()
        response.success (True)
        response.message ("On_stop command")
        return response

    def on_enable_motion(self, request, response):
        # TODO 3: store request.data in self.enabled.
        self.enable = request.data
        # If motion was just turned OFF, also send one zero command.
        if response.success:
            response.message = "Motion enabled"
        else:
            response.message = "Motion disabled"
            self.publish_zero()
        # Then fill in response.success and response.message
        # (for example 'Motion enabled' or 'Motion disabled').
        return response


def main(args=None):
    rclpy.init(args=args)
    node = SafetyGate()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()