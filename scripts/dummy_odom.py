#!/usr/bin/env python

import rospy
from cluedo_exp.msg import Dummy_Odom

def dummy_odom():


    # pub = rospy.Publisher('dummy_odometry', Dummy_Odom, queue_size=3)
   
    r = rospy.Rate(10) #10hz
    
    
    # msg = Dummy_Odom()

    while not rospy.is_shutdown():     
        r.sleep()
 
if __name__ == '__main__':
 
    rospy.init_node('dummy_odometry', anonymous=True)
    
    try:
        dummy_odom()
    except rospy.ROSInterruptException: pass  
