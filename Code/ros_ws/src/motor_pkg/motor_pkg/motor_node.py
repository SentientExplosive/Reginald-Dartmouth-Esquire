import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from gpiozero import PWMOutputDevice, OutputDevice
import time

class DualMotorController(Node):
    def __init__(self):
        super().__init__('dual_motor_controller')

        # Motor 1 GPIO Setup
        self.pwm_pin_motor1 = PWMOutputDevice(12)  # PWM pin for motor 1
        self.dir_pin_motor1 = OutputDevice(24)        # Direction pin for motor 1
        self.motor1slp = OutputDevice(22) # You snooze you lose

        # Motor 2 GPIO Setup
        self.pwm_pin_motor2 = PWMOutputDevice(13)  # PWM pin for motor 2
        self.dir_pin_motor2 = OutputDevice(25)        # Direction pin for motor 2
        self.motor2slp = OutputDevice(23) # You snooze you lose

        # Subscription to custom motor command topic
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.motor_command_callback,
            10
        )
        
        # Subscription to run_state
        self.motor_run_state_ = self.create_subscription(Bool, 'run_state', self.run_state_callback, 10)
        

        self.get_logger().info("Dual Motor Controller Node started.")

    def run_state_callback(self, msg):
        if not msg.data:
            self.pwm_pin_motor1.value = 1.0
            self.pwm_pin_motor2.value = 1.0
            self.dir_pin_motor1.toggle()
            self.dir_pin_motor2.toggle()
            self.pwm_pin_motor1.on()
            self.motor1slp.on()
            self.pwm_pin_motor2.on()
            self.motor2slp.on()
            
            time.sleep(0.08)
            self.pwm_pin_motor1.off()
            self.motor1slp.off()
            self.pwm_pin_motor2.off()
            self.motor2slp.off()
  
    def motor_command_callback(self, msg):
        # Motor 1
        self.pwm_pin_motor1.value = abs(msg.linear.x)

        # direction_motor1 = msg.motor1_direction
        self.get_logger().info(f"Speed_a={self.pwm_pin_motor1.value}")
        

        # Clamp motor 1 speed
        self.pwm_pin_motor1.value = max(min(self.pwm_pin_motor1.value, 1.0), -1.0)
        self.get_logger().info(f"Speed_b={self.pwm_pin_motor1.value}")
        # Turn the damn thing on
        if self.pwm_pin_motor1.value == 0:
            self.pwm_pin_motor1.off()
            self.motor1slp.off()
        else:
            self.pwm_pin_motor1.on()
            self.motor1slp.on()
        
        if msg.linear.x > 0:
            self.dir_pin_motor1.on()  # Forward
        else:
            self.dir_pin_motor1.off()  # Reverse

        # Motor 2
        self.pwm_pin_motor2.value = abs(msg.linear.z)

        # Clamp motor 2 speed
        self.pwm_pin_motor2.value = max(min(self.pwm_pin_motor2.value, 1.0), -1.0)
        # Turn the damn thing on
        if self.pwm_pin_motor2.value == 0:
            self.pwm_pin_motor2.off()
            self.motor2slp.off()
        else:
            self.pwm_pin_motor2.on()
            self.motor2slp.on()
        
        if msg.linear.z > 0:
            self.dir_pin_motor2.on()  # Forward
        else:
            self.dir_pin_motor2.off()  # Reverse

        self.get_logger().info(f"\nMotor 1 Command: Speed={self.pwm_pin_motor1.value}\nMotor 2 Command: Speed={self.pwm_pin_motor2.value}")
        

    def destroy_node(self):
        self.pwm_pin_motor1.close()
        self.dir_pin_motor1.close()
        self.pwm_pin_motor2.close()
        self.dir_pin_motor2.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DualMotorController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down dual motor controller.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

