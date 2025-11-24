import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int64
from std_msgs.msg import Float32
import serial
import time

class SerialCommunicator(Node):
    def __init__(self):
        super().__init__('Comms')
        # Initialize right encoder publisher
        self.r_encoder_pub = self.create_publisher(Int64, 'r_encoder', 10)

        # Initialize left encoder publisher
        self.l_encoder_pub = self.create_publisher(Int64, 'l_encoder', 10)

        # Initialize imu publisher
        self.imu_pub = self.create_publisher(Float32, 'imu', 10)
        
        # Initialize run_state publisher
        self.run_state_pub = self.create_publisher(Int64, 'run_state', 10)
        
        # Initialize color publisher
        self.color_pub = self.create_publisher(String, 'color', 10)

        # Initialize dist publisher
        self.dist_pub = self.create_publisher(Int64, 'dist', 10)
        
        # Initialize subscriptions
        self.outgoing_mail_ = self.create_subscription(Int64, 'outgoing_mail', self.send_serial_data, 10)
        
        # Send default state value (0) to the topic
        stateVal = Int64()
        stateVal.data = 0
        self.run_state_pub.publish(stateVal)

        # Initialize the serial port
        # Update the serial port name and baud rate as needed (should add code to search for open ports and trying to connect to them, or dedicate a specific port to the PI)
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        self.port_open= True

        # Initialize timer to call the read_serial_data function every 'timer_period' seconds (0.01)
        timer_period = 0.01  # seconds
        self.timer = self.create_timer(timer_period, self.read_serial_data)
        
        self.get_logger().info("Done initializing")

    def read_serial_data(self):
        # Attempt to read data from the serial port
        try:
            if (self.ser.in_waiting > 0 and self.port_open):
                # Read line in from serial port
                line = self.ser.readline().decode('utf-8').strip()
                
                # Split string by ; in case multiple lines merged into one
                data = line.split(";")

                # Iterate through data recieved in the line that was read
                for part in data:
                    if part[0:2] == "S*": # Checks if the beginning of the data segment is the start code S*
                        # String justification & stripping
                        string_data = part
                        string_data = string_data.lstrip("S")
                        string_data = string_data.lstrip("*")
                        self.get_logger().info(string_data)
                        
                        string_data = string_data.split(",")

                        # Entry of data points into topics
                        for val in string_data:
                            # ROS data variables
                            trueVal = Int64()
                            trueValF = Float32()
                            stateVal = Int64()
                            if val.strip("-1234567890. ") == "r:": # Right encoder data
                                try:
                                    trueVal.data = int(val.strip("r: "))
                                    self.r_encoder_pub.publish(trueVal)
#                                     self.get_logger().info('Publishing: "%s" to r_encoder' % trueVal.data)
                                except:
                                    self.get_logger().info('Value Issue: "%s" not int' % val.strip("r: "))

                            elif val.strip("-1234567890. ") == "l:": # Left encoder data
                                try:
                                    trueVal.data = int(val.strip("l: "))
                                    self.l_encoder_pub.publish(trueVal)
#                                     self.get_logger().info('Publishing: "%s" to l_encoder' % trueVal.data)
                                except:
                                    self.get_logger().info('Value Issue: "%s" not int' % val.strip("l: "))
                                    
                            elif val.strip("-1234567890. ") == "imu:": # IMU data
                                try:
                                    trueValF.data = float(val.strip("imu: "))
                                    self.imu_pub.publish(trueValF)
#                                     self.get_logger().info('Publishing: "%s" to imu' % trueValF.data)
                                except:
                                    self.get_logger().info('Value Issue: "%s" not float' % val.strip("imu: "))
                            
                            elif val.strip("-1234567890. ") == "dist:": # Distance data
                                try:
                                    trueVal.data = int(val.strip("dist: "))
                                    self.dist_pub.publish(trueVal)
#                                     self.get_logger().info('Publishing: "%s" to dist' % trueVal.data)
                                except:
                                    self.get_logger().info('Value Issue: "%s" not int' % val.strip("dist: "))
                            
                            elif val.strip("-1234567890. ") == "Restart":  # Restart command from button
                                stateVal.data = 2
                                self.run_state_pub.publish(stateVal)
                                self.get_logger().info('Run_State: RESTARTING')

                            elif val.strip("-1234567890. ") == "Start": # Start command from button
                                stateVal.data = 1
                                self.run_state_pub.publish(stateVal)
                                self.get_logger().info('Run_State: STARTING')
                                
                            elif val.strip("-1234567890. ") == "Stop": # Stop command from button
                                stateVal.data = 0
                                self.run_state_pub.publish(stateVal)
                                self.get_logger().info('Run_State: STOPPING')
                            
                            elif val.strip("-1234567890.: ") == "color": # Color Data
                                color = String()
                                datastring = val.strip("color: ")
                                datalist = datastring.split(":")
                                colorlist = []
                                for val in datalist:
                                    try:
                                        colorlist.append(int(val))
                                    except:
                                        self.get_logger().info('Failed to add "%s" to colorlist' % val)
                                        colorlist.append(-1)
                                color.data = repr(colorlist)
                                self.color_pub.publish(color)
                                self.get_logger().info('Publishing: "%s" to color' % color.data)
            
            # Short time delay (realized this isn't necessary when commenting)
            #time.sleep(0.01)
        
        # In the case of an error, close the port and output the error
        except serial.SerialException as e:
            self.get_logger().info("Error: %s" % e)
            self.port_open = False

    def send_serial_data(self, msg):
        # Sends serial data to the rp2040 based on the data in the msg variable passed to the function
        mailval = msg.data
        message = "ping;"

        # Decided to have preset data values correspond to certain commands instead of sending a specific string through the function
        # In this case, 1 indicates a fire has been detected and sends the 'fire;' command to the 2040
        if (mailval == 1): # Fire Detected, send message to flash blue on the 2040
            message = "fire;"
            try:
                self.ser.write(message.encode('utf-8'))
            except:
                self.get_logger().info("Error when trying to send message: %s" % message)
        else: # If no specific message given, send default message 'ping;'
            try:
                self.ser.write(message.encode('utf-8'))
            except:
                self.get_logger().info("Error when trying to send message: %s" % message)

    def destroy_node(self): # Destroys the node at end of program execution
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