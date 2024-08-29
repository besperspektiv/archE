#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
import sys, select, termios, tty
import signal
# Define key mappings for skid-steer control
MOVE_BINDINGS = {
    'w': (-1, 0),  # Move backward
    's': (1, 0),   # Move forward
    'a': (0, -1),  # Turn left
    'd': (0, 1),   # Turn right
}

# Define key mappings for speed adjustments
SPEED_BINDINGS = {
    'q': (0.1, 0),   # Increase linear speed
    'z': (-0.1, 0),  # Decrease linear speed
    'e': (0, 0.1),   # Increase angular speed
    'c': (0, -0.1),  # Decrease angular speed
}

# Initial speeds
LINEAR_SPEED = 1.0  # m/s
ANGULAR_SPEED = 1.0  # rad/s

# Speed increments
LINEAR_INCREMENT = 0.5
ANGULAR_INCREMENT = 0.5

# Global variables
pub = None
twist = None

def signal_handler(sig, frame):
    """Handle exit signal (Ctrl+C)."""
    global pub, twist
    print("\nExiting...")
    if pub is not None and twist is not None:
        # Stop the robot
        twist.linear.x = 0
        twist.angular.z = 0
        pub.publish(twist)
    sys.exit(0)

def get_key():
    """Capture key press from keyboard."""
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main():
    global pub, twist

    rospy.init_node('keyboard_controll_node')  # Initialize ROS node
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)  # Publisher to the robot's command velocity topic
    twist = Twist()  # Create Twist message object

    # Register signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)

    global LINEAR_SPEED, ANGULAR_SPEED

    print("Control Your Robot!")
    print("Use WASD keys to move. Press 'i/k' to increase/decrease linear speed and 'j/l' to increase/decrease angular speed. Press 'q' to quit.")
    print(f"Current Linear Speed: {LINEAR_SPEED} | Angular Speed: {ANGULAR_SPEED}")

    while not rospy.is_shutdown():
        key = get_key()
        if key in MOVE_BINDINGS.keys():
            # Get the movement direction based on the key pressed
            angular, linear = MOVE_BINDINGS[key]

            # Set linear and angular velocities
            twist.linear.x = linear * ANGULAR_SPEED
            twist.angular.z = angular * LINEAR_SPEED

            pub.publish(twist)  # Publish the Twist message

        elif key in SPEED_BINDINGS.keys():
            # Get the speed change direction
            linear_change, angular_change = SPEED_BINDINGS[key]

            # Adjust linear and angular speeds separately
            LINEAR_SPEED = max(0, LINEAR_SPEED + linear_change * LINEAR_INCREMENT)
            ANGULAR_SPEED = max(0, ANGULAR_SPEED + angular_change * ANGULAR_INCREMENT)

            print(f"Updated Linear Speed: {LINEAR_SPEED:.2f} | Angular Speed: {ANGULAR_SPEED:.2f}")

        elif key == 'x':
            # Stop the robot when quitting
            twist.linear.x = 0
            twist.angular.z = 0
            pub.publish(twist)  

        else:
            # If no recognized key is pressed, stop the robot
            twist.linear.x = 0
            twist.angular.z = 0
            pub.publish(twist)
            break  
        
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

if __name__ == '__main__':
    settings = termios.tcgetattr(sys.stdin)  # Save terminal settings
    try:
        main()
    except rospy.ROSInterruptException:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
