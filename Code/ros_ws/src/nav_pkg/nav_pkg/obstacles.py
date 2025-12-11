import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64
from std_msgs.msg import String

import math
import time

class NaviAvoidance(Node):
    def __init__(self):
        super().__init__("obbi")

        # Subscribe to necessary topics
        self.navi_dist_ = self.create_subscription(Int64, 'dist', self.dist_callback, 10)
        self.navi_color_ = self.create_subscription(String, 'color', self.color_callback, 10) 
        self.run_state_ = self.create_subscription(Int64, 'run_state', self.run_state_callback, 10)

        # Initialize run state publisher
        self.run_state_pub = self.create_publisher(Int64, 'run_state', 10)

        # Initialize outgoing mail publisher
        self.outgoing_mail_pub = self.create_publisher(Int64, 'outgoing_mail', 10)

        # Variables
        self.curr_stopped = False
        self.fire_detected = False
        self.curr_dist = 0
        self.min_dist = 100
        self.run_state = 0

        # Generate instruction set
#         path_state = Int64()
#         path_state.data = 0
#         self.path_planning_pub.publish(path_state)
        
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.DEBUG)
        self.get_logger().info("Obstacle Avoidance Online")

    def dist_callback(self, msg):
#         self.get_logger().info('Received Message: %s' % msg.data)
        self.curr_dist = msg.data

        if self.curr_dist < self.min_dist and not self.curr_stopped and self.run_state == 1:
            # Stop & recalibrate pathing
            self.curr_stopped = True
            
            state = Int64()
            state.data = 3
            self.run_state_pub.publish(state)

            self.get_logger().info('OBSTACLE DETECTED, STOPPING & RECALIBRATING MAP')
        
        elif self.curr_stopped and self.curr_dist > self.min_dist * 1.4:
            self.curr_stopped = False

    def color_callback(self, msg):
#         self.get_logger().info('Received Message: %s' % msg.data)
        colorlist = eval(msg.data)
        if (colorlist[0] > 2.5*((colorlist[1] + colorlist[2])/2) and not self.fire_detected):
            self.get_logger().info('AAAAAAAAAAAAAAAAAA FIREEEEEEEEEEEEEEE')
            self.fire_detected = True
            
            state = Int64()
            state.data = 4
            self.run_state_pub.publish(state)
            
            mail = Int64()
            mail.data = 1
            self.outgoing_mail_pub.publish(mail)
            
        elif (self.fire_detected and colorlist[0] <= 2*((colorlist[1] + colorlist[2])/2)):
            self.get_logger().info('Oh, the fire\'s gone')
            self.fire_detected = False
#         self.get_logger().info('Received Color: %s' % colorlist)

    def run_state_callback(self, msg):
        self.run_state = msg.data
        self.get_logger().info(f"State set to: {self.run_state}")


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
