from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
	ld = LaunchDescription()

	motor_node = Node(package='motor_pkg',executable='motor_node')
	comms_node = Node(package='rp2040_pkg',executable='comms')
	navi_node = Node(package='nav_pkg',executable='navi')
	
	ld.add_action(motor_node)
	ld.add_action(comms_node)
	ld.add_action(navi_node)
	
	return ld
	
	
