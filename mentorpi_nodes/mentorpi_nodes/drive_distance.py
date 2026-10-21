import math
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from nav2_msgs.action import DriveOnHeading


class DriveDistance(Node):

    def __init__(self):
        super().__init__('drive_distance')

        # Where the robot is, from /odom. None means "no message yet"
        self.x = None
        self.y = None

        # One group that lets callbacks run at the same time
        group = ReentrantCallbackGroup()

        self.create_subscription(
            Odometry, 'odom', self.on_odom, 10, callback_group=group)

        # We publish to cmd_vel_raw so the safety_gate sees our commands
        self.pub = self.create_publisher(TwistStamped, 'cmd_vel_raw', 10)

        self.action_server = ActionServer(
            self,
            DriveOnHeading,
            'drive_distance',
            execute_callback=self.execute,
            goal_callback=self.on_goal,
            cancel_callback=self.on_cancel,
            callback_group=group)

        self.get_logger().info('drive_distance action server is ready')

    def on_odom(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    def on_goal(self, goal_request):
        if goal_request.target.x <= 0.0 or goal_request.speed <= 0.0:
            self.get_logger().warn('Rejected: distance and speed must be positive')
            return GoalResponse.REJECT

        if self.x is None:
            self.get_logger().warn('Rejected: no odometry yet')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT


    def on_cancel(self, goal_handle):
        self.get_logger().info('Cancel requested')
        return CancelResponse.ACCEPT

    def send_speed(self, speed):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = speed
        self.pub.publish(msg)

    def execute(self, goal_handle):
        goal = goal_handle.request
        target = goal.target.x
        speed = goal.speed

        # time_allowance is a Duration: seconds plus nanoseconds
        allowance = goal.time_allowance.sec + goal.time_allowance.nanosec * 1e-9
        if allowance <= 0.0:
            allowance = 10.0

        start_x = self.x
        start_y = self.y
        start_time = self.get_clock().now()

        feedback = DriveOnHeading.Feedback()
        result = DriveOnHeading.Result()

        self.get_logger().info(f'Driving {target:.2f} m at {speed:.2f} m/s')

        while rclpy.ok():
            elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
            traveled = math.hypot(self.x - start_x, self.y - start_y)

            # Worked example: the cancel branch is done for you
            if goal_handle.is_cancel_requested:
                self.send_speed(0.0)
                goal_handle.canceled()
                result.error_code = DriveOnHeading.Result.NONE
                result.error_msg = 'Canceled'
                break

            # TODO 2: out of time.
            # If elapsed is more than allowance: stop the robot, abort the goal,
            # set error_code to DriveOnHeading.Result.TIMEOUT,
            # set error_msg to 'Ran out of time', and break.
            if elapsed > allowance:
                self.send_speed(0.0)
                goal_handle.abort()
                result.error_code = DriveOnHeading.Result.TIMEOUT
                result.error_msg = 'Ran out of time'
                break

            # TODO 3: arrived.
            # If traveled has reached target: stop the robot, succeed the goal,
            # set error_code to DriveOnHeading.Result.NONE,
            # set error_msg to an empty string '', and break.
            if traveled >= target:
                self.send_speed(0.0)
                goal_handle.succeed()
                result.error_code = DriveOnHeading.Result.NONE
                result.error_msg = ''
                break            

            # TODO 4: still driving.
            # Send the speed, put traveled in feedback.distance_traveled
            # (as a float), publish the feedback, then sleep 0.1 seconds.
            self.send_speed(speed)
                feedback.distance_traveled = float(traveled)
                goal_handle.publish_feedback(feedback)
                time.sleep(0.1)

        elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
        result.total_elapsed_time.sec = int(elapsed)
        result.total_elapsed_time.nanosec = int((elapsed % 1.0) * 1e9)
        return result


def main(args=None):
    rclpy.init(args=args)
    node = DriveDistance()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()