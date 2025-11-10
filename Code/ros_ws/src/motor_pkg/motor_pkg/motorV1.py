import rclpy
import RPi.GPIO as GPIO
from rclpy.node import Node

# pins for motors
motor1PWMPin = 12
motor2PWMPin = 13
motor1Dir = 24
motor2Dir = 25
motor1Sleep = 22
motor2Sleep = 23
motor1Fault = 5
motor2Fault = 6

# Setup GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(motor1PWMPin, GPIO.out)
GPIO.setup(motor1Dir, GPIO.out)

GPIO.setup(motor2PWMPin, GPIO.out)
GPIO.setup(motor2Dir, GPIO.out)

motor1PWM = GPIO.PWN(motor1PWMPin, 1000)
motor2PWM = GPIO.PWN(motor2PWMPin, 1000)

motor1PWM.start(0)
motor2PWM.start(0)

# motor control time :D
def setMotor(motor, speed, direction):
	if motor == 1:
		GPIO.output(motor1Dir, direction)
		motor1PWM.ChangeDutyCycle(speed)
	elif motor == 2:
		GPIO.output(motor2Dir, direction)
		motor2PWM.ChangeDutyCycle(speed)
		
def motorCommandCallback(msg):
	speed = msg.data
	if speed > 0:
		setMotor(1, abs(speed), GPIO.HIGH)
		setMotor(2, abs(speed), GPIO.HIGH)
	else:	
		setMotor(1, abs(speed), GPIO.LOW)
		setMotor(2, abs(speed), GPIO.LOW)

class MotorBusiness(Node):
	def __init__(self):
		super().__init__('motor_stuff')
		
def main(args=None):
	rclpy.init(args=args)
	node = MotorBusiness()
	rclpy.spin(node)
	rclpy.shutdown()
	
if __name__ == '__main__':
	main()
