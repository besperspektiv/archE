#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState

class TankDriveController:
    def __init__(self):
        rospy.init_node('tank_drive_controller')
        # Publisher for joint states
        self.joint_pub = rospy.Publisher('/joint_states', JointState, queue_size=10)

        # Subscriber to the cmd_vel topic
        rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback)

        self.wheel_radius = 0.09       # Radius of each wheel (meters)

        rospy.spin()

    def cmd_vel_callback(self, msg):
        # Get the linear and angular velocities from the Twist message
        linear_velocity = msg.linear.x
        angular_velocity = msg.angular.z    

        # Calculate the wheel velocities
        left_velocity = linear_velocity - (angular_velocity * self.wheel_separation / 2)
        right_velocity = linear_velocity + (angular_velocity * self.wheel_separation / 2)

        # Convert linear velocity to angular velocity (rad/s)
        left_wheel_speed = left_velocity / self.wheel_radius
        right_wheel_speed = right_velocity / self.wheel_radius

        # Create and publish the JointState message with velocities
        joint_state = JointState()
        joint_state.header.stamp = rospy.Time.now() 
        joint_state.name = ['wheel_1_joint', 'wheel_2_joint', 'wheel_3_joint', 'wheel_4_joint']
        joint_state.velocity = [left_wheel_speed, right_wheel_speed, left_wheel_speed, right_wheel_speed]
        joint_state.position = []
        joint_state.effort = []
        self.joint_pub.publish(joint_state)
            
if __name__ == '__main__':
    try:
        TankDriveController()
    except rospy.ROSInterruptException:
        pass
