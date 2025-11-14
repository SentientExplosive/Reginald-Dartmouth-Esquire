import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64

import math
import time

class NaviAvoidance(Node):
    def __init__(self):
        super().__init__("obbi")

        # Subscribe to necessary topics
        self.navi_dist_ = self.create_subscription(Int64, 'dist', self.dist_callback, 10)

        # Initialize run state publisher
        super().__init__('run_state_publisher')
        self.run_state_pub = self.create_publisher(Int64, 'run_state', 10)

        # Initialize path planning publisher
        super().__init__('path_planning_publisher')
        self.path_planning_pub = self.create_publisher(Int64, 'path_planning', 10)

        # Variables
        self.curr_dist = 0
        self.min_dist = 0

        # Generate instruction set
        path_state = Int64()
        path_state.data = 0
        self.path_planning_pub.publish(path_state)
        
        self.get_logger().info("Obstacle Avoidance Online")

    def dist_callback(self, msg):
        self.curr_dist = msg.data

        if self.curr_dist < self.min_dist:
            # Stop & recalibrate pathing
            state = Int64()
            state.data = 0
            self.run_state_pub.publish(state)

            path_state = Int64()
            path_state.data = 1
            self.path_planning_pub.publish(path_state)

            self.get_logger().info('OBSTACLE DETECTED, STOPPING & RECALIBRATING MAP')


def main(args=None):
    rclpy.init(args=args)
    node = NaviAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    
if __name__ == "__main__":
    main()
