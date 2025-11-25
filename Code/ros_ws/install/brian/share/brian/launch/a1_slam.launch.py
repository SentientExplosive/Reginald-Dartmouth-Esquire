from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution, ThisLaunchFileDir

def generate_launch_description():
    
    slam_params = PathJoinSubstitution([
        ThisLaunchFileDir(),
        '..',
        'config',
        'mapper_params_online_sync.yaml'
    ])
    
    return LaunchDescription([
        
        # A1 SLIDAR driver
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'serial_baudrate': 115200,
                'frame_id': 'laser_frame'
            }],
            output='screen'
        ),

        # slam_toolbox
        Node(
            package='slam_toolbox',
            executable='sync_slam_toolbox_node',
            name='slam_toolbox',
            parameters=[slam_params, {'mode': 'mapping'}],
            remappings=[
                ('scan','/scan')
                ],
            output='screen'
        )
    ])
