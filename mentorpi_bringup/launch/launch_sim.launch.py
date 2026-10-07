import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('mentorpi_bringup')
    gz_pkg = get_package_share_directory('ros_gz_sim')

    world = LaunchConfiguration('world')

    # Gazebo turns package:// mesh paths into model:// paths and looks for them
    # in GZ_SIM_RESOURCE_PATH. Point it at the folder that contains our package.
    desc_share = os.path.dirname(get_package_share_directory('mentorpi_description'))
    gz_resources = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', desc_share)

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', 'rsp.launch.py')),
        launch_arguments={'use_sim_time': 'true',
                          'sim_mode': 'true'}.items())

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gz_pkg, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r -v4 ', world],
                          'on_exit_shutdown': 'true'}.items())

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'mentorpi', '-z', '0.05'],
        output='screen')

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': os.path.join(pkg, 'config', 'gz_bridge.yaml'),
                     'use_sim_time': True}],
        output='screen')

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='empty.sdf'),
        gz_resources,
        rsp,
        gazebo,
        spawn,
        bridge,
    ])