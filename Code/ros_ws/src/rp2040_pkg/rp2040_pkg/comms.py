import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import time

class SerialCommunicator(Node):
    def __init__(self):
        # Initialize right encoder publisher
        super().__init__('right_encoder_publisher')
        self.r_encoder_pub = self.create_publisher(String, 'r_encoder', 10)

        # Initialize left encoder publisher
        super().__init__('left_encoder_publisher')
        self.l_encoder_pub = self.create_publisher(String, 'l_encoder', 10)

        # Initialize imu publisher
        super().__init__('imu_publisher')
        self.imu_pub = self.create_publisher(String, 'imu', 10)

        # Initialize the serial port
        # Update the serial port name and baud rate as needed (should add code to search for open ports and trying to connect to them, or dedicate a specific port to the PI)
        self.ser = serial.Serial('/dev/bus/usb/004/008', 115200, timeout=1)
        self.port_open= True

        # Initialize timer
        timer_period = 0.01  # seconds
        self.timer = self.create_timer(timer_period, self.read_serial_data)
        
        self.get_logger().info("Done initializing")

    def read_serial_data(self):
        self.get_logger().info("Trying to read serial")
        try:
            if (self.ser.in_waiting > 0 and self.port_open):
                line = self.ser.readline().decode('utf-8').strip()
                # Split string by ; in case multiple lines merged into one
                data = line.split(";")

                # Iterate through data recieved in the line that was read
                for part in data:
                    if part[0:2] == "S*":
                        # String justification & stripping
                        string_data = part
                        string_data = string_data.lstrip("S*encoder")
                        string_data = string_data.split(",")

                        # Entry of data points into topics
                        for val in string_data:
                            # ROS string
                            trueVal = String()
                            self.get_logger().info('AAAAAAAAAAAAAAAAAAA')
                            if val.strip("1234567890. ") == "r:":
                                trueVal.data = val.strip("r: ")
                                self.r_encoder_pub.publish(trueVal)
                                self.get_logger().info('Publishing: "%s"' % trueVal.data)

                            elif val.strip("1234567890. ") == "l:":
                                trueVal.data = val.strip("l: ")
                                self.l_encoder_pub.publish(trueVal)
                                self.get_logger().info('Publishing: "%s"' % trueVal.data)

                            elif val.strip("1234567890. ") == "imu:":
                                trueVal.data = val.strip("imu: ")
                                self.imu_pub.publish(trueVal)
                                self.get_logger().info('Publishing: "%s"' % trueVal.data)

            time.sleep(0.01)
        except serial.SerialException as e:
            self.get_logger().info("Error: %s" % e)
            self.port_open = False

    def destroy_node(self):
        self.ser.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = SerialCommunicator()
    node.get_logger().info("starting")
    try:
        node.get_logger().info("spinnnnnnn")
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down serial communications.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()