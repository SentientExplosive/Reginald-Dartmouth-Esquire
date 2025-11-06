import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int64
from std_msgs.msg import Float32
import serial
import time

class SerialCommunicator(Node):
    def __init__(self):
        # Initialize right encoder publisher
        super().__init__('right_encoder_publisher')
        self.r_encoder_pub = self.create_publisher(Int64, 'r_encoder', 10)

        # Initialize left encoder publisher
        super().__init__('left_encoder_publisher')
        self.l_encoder_pub = self.create_publisher(Int64, 'l_encoder', 10)

        # Initialize imu publisher
        super().__init__('imu_publisher')
        self.imu_pub = self.create_publisher(Float32, 'imu', 10)
        
        # Initialize run_state publisher
        super().__init__('run_state_publisher')
        self.run_state_pub = self.create_publisher(Int64, 'run_state', 10)
        
        # Send default state value (0) to the topic
        stateVal = Int64()
        stateVal.data = 0
        self.run_state_pub.publish(stateVal)

        # Initialize dist publisher
        super().__init__('dist_publisher')
        self.dist_pub = self.create_publisher(Int64, 'dist', 10)

        # Initialize the serial port
        # Update the serial port name and baud rate as needed (should add code to search for open ports and trying to connect to them, or dedicate a specific port to the PI)
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        self.port_open= True

        # Initialize timer
        timer_period = 0.01  # seconds
        self.timer = self.create_timer(timer_period, self.read_serial_data)
        
        self.get_logger().info("Done initializing")

    def read_serial_data(self):
#         self.get_logger().info("Trying to read serial")
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
                        string_data = string_data.lstrip("S")
                        string_data = string_data.lstrip("*")
                        self.get_logger().info(string_data)
                        
                        string_data = string_data.split(",")

                        # Entry of data points into topics
                        for val in string_data:
                            # ROS string
                            trueVal = Int64()
                            trueValF = Float32()
                            stateVal = Int64()
#                             self.get_logger().info('AAAAAAAAAAAAAAAAAAA')
                            if val.strip("-1234567890. ") == "r:":
                                try:
                                    trueVal.data = int(val.strip("r: "))
                                    self.r_encoder_pub.publish(trueVal)
                                    self.get_logger().info('Publishing: "%s" to r_encoder' % trueVal.data)
                                except:
                                    self.get_logger().info('Value Issue: "%s" not int' % val.strip("r: "))

                            elif val.strip("-1234567890. ") == "l:":
                                try:
                                    trueVal.data = int(val.strip("l: "))
                                    self.l_encoder_pub.publish(trueVal)
                                    self.get_logger().info('Publishing: "%s" to l_encoder' % trueVal.data)
                                except:
                                    self.get_logger().info('Value Issue: "%s" not int' % val.strip("l: "))
                                    
                            elif val.strip("-1234567890. ") == "imu:":
                                try:
                                    trueValF.data = float(val.strip("imu: "))
                                    self.imu_pub.publish(trueValF)
                                    self.get_logger().info('Publishing: "%s" to imu' % trueValF.data)
                                except:
                                    self.get_logger().info('Value Issue: "%s" not float' % val.strip("imu: "))
                            
                            elif val.strip("-1234567890. ") == "dist:":
                                try:
                                    trueVal.data = int(val.strip("dist: "))
                                    self.dist_pub.publish(trueVal)
                                    self.get_logger().info('Publishing: "%s" to dist' % trueVal.data)
                                except:
                                    self.get_logger().info('Value Issue: "%s" not int' % val.strip("dist: "))
                            
                            elif val.strip("-1234567890. ") == "Restart":
                                stateVal.data = 2
                                self.run_state_pub.publish(stateVal)
                                self.get_logger().info('Run_State: RESTARTING')

                            elif val.strip("-1234567890. ") == "Start":
                                stateVal.data = 1
                                self.run_state_pub.publish(stateVal)
                                self.get_logger().info('Run_State: STARTING')
                                
                            elif val.strip("-1234567890. ") == "Stop":
                                stateVal.data = 0
                                self.run_state_pub.publish(stateVal)
                                self.get_logger().info('Run_State: STOPPING')

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
#     node.get_logger().info("starting")
    try:
#         node.get_logger().info("spinnnnnnn")
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down serial communications.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()