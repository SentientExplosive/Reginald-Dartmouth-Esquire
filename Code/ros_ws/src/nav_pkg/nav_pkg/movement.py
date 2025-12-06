import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int64
from std_msgs.msg import Float32
from std_msgs.msg import String
# import tf_transformations

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
    
class NaviMovement(Node):
    def __init__(self):
        super().__init__("navi")
        
        # Publisher to Twist
        self.navi_pub_ = self.create_publisher(Twist, "/cmd_vel", 10)

        # Publisher to Path Planning
        self.path_planning_pub = self.create_publisher(String, 'path_planning', 10)
        
        # Subscribe to necessary topics
        self.navi_l_encoder_ = self.create_subscription(Int64, 'l_encoder', self.encoder_left_callback, 10)
        self.navi_r_encoder_ = self.create_subscription(Int64, 'r_encoder', self.encoder_right_callback, 10)
        self.navi_imu_ = self.create_subscription(Float32, 'imu', self.imu_callback, 10)
        self.navi_run_state_ = self.create_subscription(Int64, 'run_state', self.run_state_callback, 10)
        self.navi_instructions_ = self.create_subscription(String, 'instructions', self.instructions_callback, 10)

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
        self.angular_pid = Piddles(0.15, 0.0, 0.02, name='angular', mod = 0.04)
        
        # Initial encoder values when executing an instruction
        self.l_start_encoderval = 0.0
        self.r_start_encoderval = 0.0
        
        # Internal state
        self.encoder_left = 0.0
        self.encoder_right = 0.0
        self.yaw = 0.0
        self.true_yaw = 0.0
        
        # Initial angle to zero off of, taken upon "Restart" state
        self.zero_to_angle = 0.0
        self.temp_turn_to_angle = 0.0

        # Direction that Reginald is facing according to the map (Challenge 2 variable)
        # 0 = East, 1 = North, 2 = West, 3 = South
        self.direc = 0 
        self.east = 0 # the angle representing "east"

        # Instructions
        self.instructions = []
        self.curr_instruction = 0

        # Challenge variables
        self.challenge = 2 # 1 by default, can choose challenge 1-4
        self.run_state = 0

        # State variables for controlling what type of movement is happening
        self.done = False
        self.move_dist = False
        self.turn = False
        self.obstacle_detected = False
        
        self.get_logger().info("Movement Online")
        
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

                # Find temp zeroing angle
                zeroing_angle = self.target_heading - 180
                if (zeroing_angle < 0):
                    zeroing_angle += 360
                self.temp_turn_to_angle = zeroing_angle

                self.turn = True
                self.move_dist = False

                # Challenge 2 self.direc updating
                angle = self.target_heading - self.east
                if (angle % 90 == 0):
                    if (angle == 0): # east
                        self.direc = 0
                    elif (angle == 90): # south
                        self.direc = 3
                    elif (angle == 180): # west
                        self.direc = 2
                    elif (angle == 270): # north
                        self.direc = 1
            elif i[0] == "a": # Heading angle for challenge 2, passed from the path planning file
                self.east= float(i.strip("t"))
                self.done = True

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
        if self.turn:
            angle = msg.data - self.temp_turn_to_angle
        else:
            angle = msg.data - self.zero_to_angle
        if (angle < 0):
            angle += 360

        self.yaw = angle
        self.true_yaw = msg.data
        # self.get_logger().info(f"Angle: {self.yaw} <-- {msg.data}")

    def run_state_callback(self, msg):
        self.run_state = msg.data
        self.get_logger().info(f"State set to: {self.run_state}")

        if self.run_state == 0:
            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.linear.z = 0.0
            self.navi_pub_.publish(cmd)
        
        elif self.run_state == 2:
            # Reset target angle and distance variables
            self.target_distance = 0.0    # meters
            self.target_heading = 0.0     # radians
            
            # Set zero_to_angle to current angle
            self.zero_to_angle = self.true_yaw
            self.get_logger().info(f"Zero To Angle: {self.zero_to_angle}")
                
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
        
        elif self.run_state == 3: # Obstacle detected
            self.obstacle_detected = True

            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.linear.z = 0.0
            self.navi_pub_.publish(cmd)
            
            path_state = String()
            if self.turn:
                traveled_dist = 0
            elif self.move_dist:
                encoder_diff_l = self.encoder_left - self.l_start_encoderval
                encoder_diff_r = self.encoder_right - self.r_start_encoderval
                traveled_dist = int(1000 * ((encoder_diff_l + encoder_diff_r) / 2) / self.ticks_per_meter) # 1000 * average encoder count / ticks_per_meter to get distance traveled in mm
            data = [1, traveled_dist, self.direc] # Sending 1 (obstacle state) and distance traveled to the path planning module
            path_state.data = repr(data)
            self.path_planning_pub.publish(path_state)
        
        elif self.run_state == 4: # Fire detected
            self.done = True
            self.curr_instruction = len(self.instructions) # forces the program to be in a permanent done state (index past end of instruction list)

            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.linear.z = 0.0
            self.navi_pub_.publish(cmd)

            path_state = String()
            if self.turn:
                traveled_dist = 0
            elif self.move_dist:
                encoder_diff_l = self.encoder_left - self.l_start_encoderval
                encoder_diff_r = self.encoder_right - self.r_start_encoderval
                traveled_dist = int(1000 * ((encoder_diff_l + encoder_diff_r) / 2) / self.ticks_per_meter) # 1000 * average encoder count / ticks_per_meter to get distance traveled in mm
            data = [2, traveled_dist, self.direc] # Sending 2 (fire state) and distance traveled to the path planning module
            path_state.data = repr(data)
            self.path_planning_pub.publish(path_state)

    def instructions_callback(self, msg):
        self.instructions = eval(msg.data)
        self.curr_instruction = 0
        self.execute_next_instruction()

    def update_motor_speed(self):
        # Calculate distance error
        l_distance_m = (self.encoder_left-self.l_start_encoderval) #/ self.ticks_per_meter
        r_distance_m = (self.encoder_right-self.r_start_encoderval) #/ self.ticks_per_meter 
        l_distance_error = self.target_distance - l_distance_m
        r_distance_error = self.target_distance - r_distance_m
        
        # Calculate angle error
        if self.turn:
            angle_error = (180 - self.yaw)
        else:
            angle_error = (self.target_heading - self.yaw)
        
        # Output angle and distance error
        self.get_logger().info(f"Angle error: {angle_error}")
        self.get_logger().info(f"L dist error: {l_distance_error}")
        self.get_logger().info(f"R dist error: {r_distance_error}")
        
        # Get motor speeds
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
                motor1_speed = max(min(r_linear_output, 1.0), -1.0) * 0.95 - angular_output * 0.1
                motor2_speed = max(min(l_linear_output, 1.0), -1.0) * 0.95 + angular_output * 0.1
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

    def update_control(self):
        if (self.challenge == 1):
            self.challenge1()
        elif (self.challenge == 2):
            self.challenge2()
        elif (self.challenge == 3):
            self.challenge3()
        elif (self.challenge == 4):
            self.challenge4()

    def challenge1(self):
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
        
        self.update_motor_speed()

    def challenge2(self):
        if self.run_state == 0 or self.yaw is None:
            return
        
        if (self.done):
            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.linear.z = 0.0
            self.navi_pub_.publish(cmd)
            time.sleep(1)
            self.execute_next_instruction()
            time.sleep(2)
        
        if self.obstacle_detected:
            self.obstacle_detected = False
        else:
            self.update_motor_speed()

    def challenge3(self):
        pass

    def challenge4(self):
        pass


def main(args=None):
    rclpy.init(args=args)
    node = NaviMovement()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    
if __name__ == "__main__":
    main()
