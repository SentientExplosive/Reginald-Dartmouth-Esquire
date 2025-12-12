# run "ros2 launch slam_toolbox online_async_launch.py" in a separate terminal

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
import math
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    #Setup RViz2 directory
    rviz_config_dir = os.path.join(
        get_package_share_directory('brian'),
        'rviz',
        'slam_sim.rviz')
    print(f"RViz file found: {rviz_config_dir}")
        
        
    return LaunchDescription([
        #Sllidar 
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            parameters=[{
                'channel_type': 'serial',
                'serial_port': '/dev/ttyUSB0',
                'serial_baudrate': 115200,
                'frame_id': 'laser',
                'inverted': False,
                'angle_compensate': True,
                'scan_mode': 'Sensitivity'
            }],
            output='screen'
        ),
        
        # Static Transforms for odom -> base_footprint -> laser
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='odom_to_base_footprint',
            arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_footprint']
        ),
        
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_footprint_to_laser',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'laser']
        ), 
        
        #RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            output='screen'
        ),
    ])