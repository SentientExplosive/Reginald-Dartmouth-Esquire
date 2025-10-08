import serial
import time

# Update the serial port name and baud rate
ser = serial.Serial('COM4', 115200, timeout=1)

def read_serial_data():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            # print(line[0:2])
            # Split string by ; in case multiple lines merged into one
            data = line.split(";")

            # Iterate through data recieved in the line that was read
            for part in data:
                if part[0:2] == "S*":
                    # String justification & stripping
                    string_data = part
                    string_data = string_data.lstrip("S*encoder")
                    string_data = string_data.split(",")
                    # print(string_data)

                    # Entry of data points into topics
                    for val in string_data:
                        # print(val.strip())
                        if val.strip("1234567890. ") == "r:":
                            trueVal = val.strip("r: ")
                            # print(trueVal)
                        elif val.strip("1234567890. ") == "l:":
                            trueVal = val.strip("l: ")
                            # print(trueVal)
                        elif val.strip("1234567890. ") == "imu:":
                            trueVal = val.strip("imu: ")
                            # print(trueVal)
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        print(f"Reading from serial port {ser.port}...")
        read_serial_data()
    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        ser.close()
        print("Serial port closed.")