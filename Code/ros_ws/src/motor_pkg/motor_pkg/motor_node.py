import rclpy
from rclpy.node import Node
from motor_control.msg import MotorCommand  # Import custom message
from gpiozero import PWMOutputDevice, OutputDevice

class DualMotorController(Node):
    def __init__(self):
        super().__init__('dual_motor_controller')

        # Motor 1 GPIO Setup
        self.enable_pin_motor1 = PWMOutputDevice(12)  # PWM pin for motor 1
        self.dir_pin_motor1 = OutputDevice(24)        # Direction pin for motor 1

        # Motor 2 GPIO Setup
        self.enable_pin_motor2 = PWMOutputDevice(17)  # PWM pin for motor 2
        self.dir_pin_motor2 = OutputDevice(27)        # Direction pin for motor 2

        # Subscription to custom motor command topic
        self.subscription = self.create_subscription(
            MotorCommand,
            'motor_commands',
            self.motor_command_callback,
            10
        )

        self.get_logger().info("Dual Motor Controller Node started.")

    def motor_command_callback(self, msg: MotorCommand):
        # Motor 1
        speed_motor1 = msg.motor1_speed
        direction_motor1 = msg.motor1_direction
        self.get_logger().info(f"Motor 1 Command: Speed={speed_motor1}, Direction={'Forward' if direction_motor1 else 'Reverse'}")

        # Clamp motor 1 speed
        speed_motor1 = max(min(speed_motor1, 1.0), -1.0)
        if direction_motor1:
            self.dir_pin_motor1.on()  # Forward
        else:
            self.dir_pin_motor1.off()  # Reverse
        self.enable_pin_motor1.value = abs(speed_motor1)

        # Motor 2
        speed_motor2 = msg.motor2_speed
        direction_motor2 = msg.motor2_direction
        self.get_logger().info(f"Motor 2 Command: Speed={speed_motor2}, Direction={'Forward' if direction_motor2 else 'Reverse'}")

        # Clamp motor 2 speed
        speed_motor2 = max(min(speed_motor2, 1.0), -1.0)
        if direction_motor2:
            self.dir_pin_motor2.on()  # Forward
        else:
            self.dir_pin_motor2.off()  # Reverse
        self.enable_pin_motor2.value = abs(speed_motor2)

    def destroy_node(self):
        self.enable_pin_motor1.close()
        self.dir_pin_motor1.close()
        self.enable_pin_motor2.close()
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

