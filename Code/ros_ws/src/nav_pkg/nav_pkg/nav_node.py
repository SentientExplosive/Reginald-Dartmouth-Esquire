import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int64
from std_msgs.msg import Float32
import tf_transformations

import math
import time

class Piddles():
    def __init__(self, kp, ki, kd, name='pid', mod = 1, range=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.name = name
        self.error_range = range
        self.modifier = mod
        
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

        output = float((p + i + d)*self.modifier)
        return output
    
class NaviConverter(Node):
    def __init__(self):
        super().__init__("navi")
        
        #Publisher to Twist
        self.navi_pub_ = self.create_publisher(Twist, "/cmd_vel", 10)
        
        #Subscribe to necessary topics
        self.navi_l_encoder_ = self.create_subscription(Int64, 'l_encoder', self.encoder_left_callback, 10)
        self.navi_r_encoder_ = self.create_subscription(Int64, 'r_encoder', self.encoder_right_callback, 10)
        self.navi_imu_ = self.create_subscription(Float32, 'imu', self.imu_callback, 10)
        self.navi_run_state_ = self.create_subscription(Int64, 'run_state', self.run_state_callback, 10)
        self.navi_dist_ = self.create_subscription(Int64, 'dist', self.dist_callback, 10)
        self.run_state = 0
        
        # Timer for updating the control
        self.timer_period = 0.04
        self.timer = self.create_timer(self.timer_period, self.update_control)
        
        # Goal
        self.target_distance = 0.0    # meters
        self.target_heading = 0.0     # radians
        
        self.ticks_per_meter = 23686
        self.error_range = 250
        self.angle_error_range = 0.5
        
        #PID Controllers
        self.l_linear_pid = Piddles(0.25, 0.0, 0.05, name='l_linear', mod = 0.001)
        self.r_linear_pid = Piddles(0.25, 0.0, 0.05, name='r_linear', mod = 0.001)
        self.angular_pid = Piddles(0.1, 0.0, 0.02, name='angular', mod = 0.04)
        
        # Initial encoder values when executing an instruction
        self.l_start_encoderval = 0.0
        self.r_start_encoderval = 0.0
        
        # Internal state
        self.encoder_left = 0.0
        self.encoder_right = 0.0
        self.yaw = 0.0
        
        # Obstacle Detection Stuff (may break off into separate node in future)
        super().__init__('run_state_publisher')
        self.run_state_pub = self.create_publisher(Int64, 'run_state', 10)
        self.curr_dist = 0
        self.min_dist = 50

        # Waypoint format: (heading/angle (degrees), distance (meters)) --> each waypoint is based off of the previous waypoint's position
        self.waypoints = [(352,1.92),(60,0.94)]
        self.instructions = []
        self.curr_instruction = 0
        
        self.done = False
        self.move_dist = False
        self.turn = False
        self.generate_instructions()
        
    def generate_instructions(self):
        # Vector values to find the correct direction and distance required to go back to the start
        vector_vals = []
        
        # Converts the waypoints into a list of instructions
        self.curr_instruction = 0
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
        
        # Load in first instruction
        self.execute_next_instruction()
    
    def execute_next_instruction(self):
        # Gets the next instruction in the list
        if (self.curr_instruction <= len(self.instructions)-1):
            i = self.instructions[self.curr_instruction]
            self.done = False
            
            self.get_logger().info(f"Current Instruction: {i}")
            if i[0] == "d":
                self.target_distance = float(i.strip("d")) * self.ticks_per_meter
                self.move_dist = True
                self.turn = False
            elif i[0] == "t":
                self.target_distance = 0
                self.target_heading = float(i.strip("t"))
                self.turn = True
                self.move_dist = False
            
            # Set starting encoder values
            self.l_start_encoderval = self.encoder_left
            self.r_start_encoderval = self.encoder_right
            
            # Increment instruction counter
            self.curr_instruction += 1
            
            self.get_logger().info(f"Target Encoder Value: {self.target_distance}")#*self.ticks_per_meter}")
            self.get_logger().info(f"Target Angle Value: {self.target_heading}")
        else:
            self.get_logger().info(f"We're done yippeee")
            self.done = True
            self.turn = False
            self.move_dist = False
    
    def encoder_left_callback(self, msg):
        self.encoder_left = msg.data

    def encoder_right_callback(self, msg):
        self.encoder_right = msg.data

    def imu_callback(self, msg):
        self.yaw = msg.data

    def run_state_callback(self, msg):
        self.run_state = msg.data

        if self.run_state == 0:
            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.linear.z = 0.0
            self.navi_pub_.publish(cmd)
        
        if self.run_state == 2:
            # Reset target angle and distance variables
            self.target_distance = 0.0    # meters
            self.target_heading = 0.0     # radians
                
            # Reset encoder variables 
            self.l_start_encoderval = 0.0
            self.r_start_encoderval = 0.0
            self.encoder_left = 0.0
            self.encoder_right = 0.0

            # Reset instruction index
            self.curr_instruction = 0

            # Reset movement states to default values
            self.done = False
            self.move_dist = False
            self.turn = False

            # Set run_state to 0 so the program remains paused
            self.run_state = 0

            # Load first instruction
            self.execute_next_instruction()
        
    def dist_callback(self, msg):
        self.curr_dist = msg

        if self.curr_dist < self.min_dist:
            # Stop & recalibrate pathing
            state = Int64()
            state.data = 0
            self.run_state_pub.publish(state)
            self.get_logger().info('OBSTACLE DETECTED, STOPPING')

    def update_control(self):
        if self.run_state == 0 or self.yaw is None:
            return
        
        # Upon reaching goal, load next instruction
        if (self.done):
            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.linear.z = 0.0
            self.navi_pub_.publish(cmd)
            time.sleep(1)
            self.execute_next_instruction()
            time.sleep(2)
        
        l_distance_m = (self.encoder_left-self.l_start_encoderval) #/ self.ticks_per_meter
        r_distance_m = (self.encoder_right-self.r_start_encoderval) #/ self.ticks_per_meter 
        l_distance_error = self.target_distance - l_distance_m
        r_distance_error = self.target_distance - r_distance_m
#         heading_error = self.normalize_angle(self.target_heading - self.yaw)
        angle_error = (self.target_heading - self.yaw)
        
        self.get_logger().info(f"Angle error: {angle_error}")
        self.get_logger().info(f"L dist error: {l_distance_error}")
        self.get_logger().info(f"R dist error: {r_distance_error}")
        
        motor1_speed = 0.0
        motor2_speed = 0.0

        if (self.move_dist and (abs(l_distance_error) < self.error_range) and (abs(r_distance_error) < self.error_range)):
            motor1_speed = 0.0
            motor2_speed = 0.0
            self.done = True
            self.turn = False
            self.move_dist = False
        elif (self.turn and (abs(angle_error) < self.angle_error_range)):
            motor1_speed = 0.0
            motor2_speed = 0.0
            self.done = True
            self.turn = False
            self.move_dist = False
        else:
            l_linear_output = self.l_linear_pid.compute(l_distance_error)
            r_linear_output = self.r_linear_pid.compute(r_distance_error)
            angular_output = self.angular_pid.compute(angle_error)

            # Convert to left and right motor speeds
            if (self.move_dist):
                motor1_speed = max(min(r_linear_output, 1.0), -1.0) * 0.75 - angular_output * 0.1
                motor2_speed = max(min(l_linear_output, 1.0), -1.0) * 0.75 + angular_output * 0.1
            elif (self.turn):
                motor1_speed = max(min(-angular_output, 1.0), -1.0) * 0.5
                motor2_speed = max(min(angular_output, 1.0), -1.0) * 0.5

        # Clip to [-1, 1]
        motor1_speed = max(min(motor1_speed, 1.0), -1.0)
        motor2_speed = max(min(motor2_speed, 1.0), -1.0)

        # Publish combined Twist message
        cmd = Twist()
        cmd.linear.x = motor1_speed
        cmd.linear.z = motor2_speed
        self.navi_pub_.publish(cmd)

        self.get_logger().info(f"Right: {motor1_speed:.2f} | Left: {motor2_speed:.2f}")
        
#     def quaternion_to_yaw(self, orientation):
#         q = [orientation.x, orientation.y, orientation.z, orientation.w]
#         _, _, yaw = tf_transformations.euler_from_quaternion(q)
#         return yaw
    
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
