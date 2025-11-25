import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class ScanSub(Node):
    def __init__(self):
        super().__init__('scan_subscriber')
        self.subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.subscription
        self.get_logger().info("Scan sub started")
        
    def scan_callback(self, msg: LaserScan):
        '''Stuff that this thing can subscribe to:
            num_ranges
            min_dist
            angle_min
            angle_max
            range_min
            range_max'''
        num_ranges = len(msg.ranges)
        min_dist = min(msg.ranges) if msg.ranges else float('nan')
        angle_max = msg.angle_max
        
        self.get_logger().info(
            f"Received LaserScan: {num_ranges} = num_ranges.\n min distance = {min_dist:.2f} m.\n {angle_max} = angle_max.\n "
            )
def main(args = None):
    rclpy.init(args=args)
    node = ScanSub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
