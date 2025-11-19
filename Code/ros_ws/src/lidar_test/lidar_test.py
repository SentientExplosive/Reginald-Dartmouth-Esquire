# Make sure you installed it first:  pip install rplidar

from rplidar import RPLidar, RPLidarException
import time

# ---- SETTINGS ----
PORT_NAME = '/dev/ttyUSB0'      # Change this to match your Device Manager port (e.g., 'COM4')
BAUDRATE = 115200        # Default baud rate for RPLIDAR A1

def main():
    print("Connecting to RPLIDAR on", PORT_NAME)
    lidar = None
    try:
        # Create lidar instance
        lidar = RPLidar(PORT_NAME, baudrate=BAUDRATE, timeout=3)
        time.sleep(1)

        # Start motor
        print("Starting motor...")
        lidar.start_motor()

        # Get health info
        info = lidar.get_info()
        health = lidar.get_health()
        print("Lidar info:", info)
        print("Lidar health:", health)

        # Start scanning quality only
        print("\nStarting scan... (Press Ctrl+C to stop)")

        quality_sum = 0
        '''
        for i, scan in enumerate(lidar.iter_scans(max_buf_meas=500)):
            lidar_tuple = scan[0]
            quality = lidar_tuple[0]
            # print(f"Scan {i} - First tuple: {lidar_tuple}")
            print(f"Scan {i} - Quality value: {quality}")
            time.sleep(0.1)

            quality_sum += quality
            
            if i >= 999:  # limit to n scans to test
                average = quality_sum / 1000
                print(f"Average quality: {average}")
                break
            '''

        
        # Start scanning
        print("\nStarting scan... (Press Ctrl+C to stop)")
        for i, scan in enumerate(lidar.iter_scans(max_buf_meas=500)):
            print(f"Scan {i} — {len(scan)} points")
            # Print first few sample points
            if len(scan) > 0:
                print("  Sample:", scan[:5])
            time.sleep(0.1)
            if i >= 10:  # limit to n scans to test
                break
        
    except RPLidarException as e:
        print("RPLidar error:", e)
        # if error is wrong body type, check that baud rate is 115200

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        if lidar:
            print("Stopping and disconnecting...")
            try:
                lidar.stop()
                lidar.stop_motor()
            except Exception:
                pass
            lidar.disconnect()
        print("Done.")

if __name__ == "__main__":
    main()
