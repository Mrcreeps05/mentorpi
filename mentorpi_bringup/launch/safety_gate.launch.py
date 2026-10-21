from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    safety_gate = Node(
        package='mentorpi_nodes',
        executable='safety_gate',
        name='safety_gate',
        output='screen',
        parameters=[{'use_sim_time': True, 'max_speed': 0.3}],
    )

    return LaunchDescription([safety_gate])