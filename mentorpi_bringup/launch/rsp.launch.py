import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    os.environ.setdefault('MACHINE_TYPE', 'MentorPi_Mecanum')

    use_sim_time = LaunchConfiguration('use_sim_time')
    sim_mode = LaunchConfiguration('sim_mode')
    xacro_file = os.path.join(
        get_package_share_directory('mentorpi_bringup'),
        'urdf', 'robot.urdf.xacro')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' sim_mode:=', sim_mode]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('sim_mode', default_value='false'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description,
                         'use_sim_time': use_sim_time}],
        ),
    ])