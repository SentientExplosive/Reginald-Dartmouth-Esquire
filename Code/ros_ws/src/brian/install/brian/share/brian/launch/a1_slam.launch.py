import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    # Path to the package share folder
    pkg_share = get_package_share_directory('your_package')

    # Default path to the YAML file
    default_config_file = os.path.join(
        pkg_share,
        'config',
        'map_params_online_sync.yaml'
    )

    # Declare a launch argument so users can override the config file
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=default_config_file,
        description='Full path to the YAML parameters file'
    )

    node = Node(
        package='your_package',
        executable='your_node',
        name='your_node',
        parameters=[LaunchConfiguration('config_file')]
    )

    return LaunchDescription([
        config_file_arg,
        node
    ])

