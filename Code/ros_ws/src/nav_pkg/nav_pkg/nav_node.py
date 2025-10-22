import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int64
from tf2 import tf_transformations

import math
import time

class Piddles():
    def __init__(self, kp, ki, kd, name='pid', range=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.name = name
        self.error_range = range
        
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
        
        if (error < self.error_range and error > -self.error_range):
            p = 0
            i = 0
            d = 0
        
        else:
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
        
        # Goal
        self.target_distance = 0.0    # meters
        self.target_heading = 0.0     # radians
        
        self.ticks_per_meter = 12022
        self.error_range = 25/self.ticks_per_meter
        
        #PID Controllers
        self.linear_pid = Piddles(0.5, 0.0, 0.1, name='linear', range=0)
        self.angular_pid = Piddles(1.0, 0.0, 0.2, name='angular')
        
        # Initial encoder values when executing an instruction
        self.l_start_encoderval = 0.0
        self.r_start_encoderval = 0.0
        
        # Internal state
        self.encoder_left = 0.0
        self.encoder_right = 0.0
        self.yaw = 0.0
        
        # Waypoint format: (heading/angle (degrees), distance (meters)) --> each waypoint is based off of the previous waypoint's position
        self.waypoints = [(50,1),(270,2.5),(45,-0.5)]
        self.instructions = []
        self.curr_instruction = 0
        
        self.done = False
        self.move_dist = False
        self.turn = False
        self.generate_instructions()
        
        self.get_logger().info(f"Target Encoder Value: {self.target_distance*self.ticks_per_meter}")
    
    def generate_instructions(self):
        # Converts the waypoints into a list of instructions
        self.curr_instruction = 0
        for waypoint in self.waypoints:
            self.instructions.append(f"t{waypoint[0]}")
            self.instructions.append(f"d{waypoint[1]}")
        
        self.get_logger().info(f"Instructions: {self.instructions}")
        
        # Load in first instruction
        self.execute_next_instruction()
    
    def execute_next_instruction(self):
        # Gets the next instruction in the list
        i = self.instructions[self.curr_instruction]
        self.get_logger().info(f"Current Instruction: {i}")
        if i[0] == "d":
            self.target_distance = float(i.strip("d"))
        elif i[0] == "t":
            self.target_distance = 0
            self.target_heading = float(i.strip("t"))
        
        # Set starting encoder values
        self.l_start_encoderval = self.encoder_left
        self.r_start_encoderval = self.encoder_right
        
        # Increment instruction counter
        self.curr_instruction += 1
    
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
        
        # Upon reaching goal, load next instruction
        if (self.done):
            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.linear.z = 0.0
            self.navi_pub_.publish(cmd)
            self.execute_next_instruction()
            self.done = False
        
        avg_ticks = ((self.encoder_left-self.l_start_encoderval) + (self.encoder_right-self.r_start_encoderval)) / 2.0
        distance_m = avg_ticks / self.ticks_per_meter
        distance_error = self.target_distance - distance_m
        heading_error = self.normalize_angle(self.target_heading - self.yaw)

        if abs(distance_error) < self.error_range:
            motor1_speed = 0
            motor2_speed = 0
            self.done = True
        else:
            linear_output = self.linear_pid.compute(distance_error)
            angular_output = self.angular_pid.compute(heading_error)

            # Convert to left and right motor speeds
            if (self.move_dist):
                motor1_speed = linear_output - angular_output
                motor2_speed = linear_output + angular_output
            elif (self.turn):
                motor1_speed = -angular_output
                motor2_speed = angular_output 

        # Clip to [-1, 1]
        motor1_speed = max(min(motor1_speed, 1.0), -1.0)
        motor2_speed = max(min(motor2_speed, 1.0), -1.0)

        # Publish combined Twist message
        cmd = Twist()
        cmd.linear.x = motor1_speed
        cmd.linear.z = motor2_speed
        self.navi_pub_.publish(cmd)

        self.get_logger().info(f"Right: {motor1_speed:.2f} | Left: {motor2_speed:.2f}")
        
    def quaternion_to_yaw(self, orientation):
        q = [orientation.x, orientation.y, orientation.z, orientation.w]
        _, _, yaw = tf_transformations.euler_from_quaternion(q)
        return yaw
    
    def normalize_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

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
