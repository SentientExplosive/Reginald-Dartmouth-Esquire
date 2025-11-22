import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64
from std_msgs.msg import String

import math
import time

class NaviPathPlanning(Node):
    def __init__(self):
        super().__init__("pathi")

        # Initialize path planning publisher
        self.instructions_pub = self.create_publisher(String, 'instructions', 10)

        # Initialize subscriptions
        self.path_planning_ = self.create_subscription(Int64, 'path_planning', self.path_planning_callback, 10)
        
        # Waypoint format: (heading/angle (degrees), distance (meters)) --> each waypoint is based off of the previous waypoint's position
        self.waypoints = [(352,1.92),(60,0.94)]

        # Path Planning Variables
        self.instructions = []
        
        self.get_logger().info("Path Planning Online")

    def path_planning_callback(self, msg):
        state = msg.data
        if (state == 0): # Create initial instruction set & map
            self.generate_instructions()
        elif (state == 1): # Update map & instructions for instances where an obstacle is detected
            self.update_instructions()
    
    def generate_instructions(self):
        # Vector values to find the correct direction and distance required to go back to the start
        vector_vals = []
        
        # Converts the waypoints into a list of instructions
        for waypoint in self.waypoints:
            self.instructions.append(f"t{waypoint[0]}")
            self.instructions.append(f"d{waypoint[1]}")
            x = waypoint[1] * math.cos((waypoint[0])*math.pi/180)
            y = waypoint[1] * math.sin(waypoint[0]*math.pi/180)
            self.get_logger().info(f"y: {y}")
            self.get_logger().info(f"x: {x}")
            vector_vals.append((x,y))
        
        # Calculate resultant vector
        total_x = 0
        total_y = 0
        for vec in vector_vals:
            total_x += vec[0]
            total_y += vec[1]
        self.get_logger().info(f"total_y: {total_y}")
        self.get_logger().info(f"total_x: {total_x}")
        angle = math.atan2(-total_y, -total_x) * (180 / math.pi)
        if (angle < 0):
            angle += 360
        dist = math.sqrt((total_x)**2 + (total_y)**2)
        self.instructions.append(f"t{angle}")
        self.instructions.append(f"d{dist}")

        self.get_logger().info(f"Instructions: {self.instructions}")
        
        # Publish instruction Set
        instructions = String()
        instructions.data = repr(self.instructions)
        self.instructions_pub.publish(instructions)
        # self.execute_next_instruction()
    
    def update_instructions(self):
        pass

def main(args=None):
    rclpy.init(args=args)
    node = NaviPathPlanning()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    
if __name__ == "__main__":
    main()

