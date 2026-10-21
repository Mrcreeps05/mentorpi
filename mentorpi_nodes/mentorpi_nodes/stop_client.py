import rclpy
from std_srvs.srv import Trigger


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('stop_client')

    client = node.create_client(Trigger, 'stop')
    if not client.wait_for_service(timeout_sec=3.0):
        node.get_logger().error('The /stop service is not available')
    else:
        # TODO 4: send the request.
        # Hint: client.call_async(...) with an empty Trigger.Request()
        future = client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(node, future)
        node.get_logger().info(f'Response: {future.result().message}')

    node.destroy_node()
    rclpy.try_shutdown()