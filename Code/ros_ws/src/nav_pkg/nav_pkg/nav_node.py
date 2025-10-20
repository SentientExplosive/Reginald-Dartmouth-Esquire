import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int64

import math
import time

class Piddles():
    def __init__(self, kp, ki, kd, name='pid'):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.name = name
        
        self.prev_error = 0.0
        self.integral = 0.0
        self.last_time = None
        
    def reset(self):
        self.prev_error = 0.0
        self.integral = 0.0
        self.last_time = None
        
    def compute(self, error):
        current_time = time.time()
        delta_time = 0.0
        if self.last_time is not None:
            delta_time = current_time - self.last_time

        self.last_time = current_time

        # Proportional
        p = self.kp * error

        # Integral
        self.integral += error * delta_time
        i = self.ki * self.integral

        # Derivative
        derivative = (error - self.prev_error) / delta_time if delta_time > 0 else 0.0
        d = self.kd * derivative

        self.prev_error = error

        output = p + i + d
        return output
    
class NaviConverter(Node):
    def __init__(self):
        super().__init__("navi")
        
        #Publisher to Twist
        self.navi_pub_ = self.create_publisher(Twist, "/cmd_vel", 10)
        
        #Subscriber to encoders + IMU
        self.navi_l_encoder_ = self.create_subscription(Int64, 'l_encoder', self.encoder_left_callback, 10)
        self.navi_r_encoder_ = self.create_subscription(Int64, 'r_encoder', self.encoder_right_callback, 10)
        self.navi_imu_ = self.create_subscription(Int64, 'imu', self.imu_callback, 10)
        
        #PID Controllers
        self.linear_pid = Piddles(0.5, 0.0, 0.1, name='linear')
        self.angular_pid = Piddles(1.0, 0.0, 0.2, name='angular')
        
        # Internal state
        self.encoder_left = 0.0
        self.encoder_right = 0.0
        self.yaw = 0.0
        
        # Goal
        self.target_distance = 2.0    # meters
        self.target_heading = 0.0     # radians
        
        self.ticks_per_meter = 1000.0
        
    def encoder_left_callback(self, msg):
        self.encoder_left = msg.data
        self.update_control()

    def encoder_right_callback(self, msg):
        self.encoder_right = msg.data
        self.update_control()

    def imu_callback(self, msg):
        self.yaw = self.quaternion_to_yaw(msg.orientation)
        self.update_control()

    def update_control(self):
        if self.yaw is None:
            return
        
        avg_ticks = (self.encoder_left + self.encoder_right) / 2.0
        distance_m = avg_ticks / self.ticks_per_meter
        distance_error = self.target_distance - distance_m
        heading_error = self.normalize_angle(self.target_heading - self.yaw)

        linear_output = self.linear_pid.compute(distance_error)
        angular_output = self.angular_pid.compute(heading_error)

        # Convert to left and right motor speeds
        motor1_speed = linear_output - angular_output
        motor2_speed = linear_output + angular_output

        # Clip to [-1, 1]
        motor1_speed = max(min(motor1_speed, 1.0), -1.0)
        motor2_speed = max(min(motor2_speed, 1.0), -1.0)

        # Publish combined Twist message
        cmd = Twist()
        cmd.linear.x = motor1_speed
        cmd.linear.z = motor2_speed
        self.motor_pub.publish(cmd)

        self.get_logger().info(f"Right: {motor1_speed:.2f} | Left: {motor2_speed:.2f}")

def main(args=None):
    rclpy.init(args=args)
    node = NaviConverter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    
if __name__ == "__main__":
    main()
