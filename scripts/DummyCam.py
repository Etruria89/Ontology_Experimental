#!/usr/bin/env python

import rospy
from cluedo_exp.msg import Dummy_Cam
 
def dummycam():
   
    pub = rospy.Publisher('dummy_image', Dummy_Cam, queue_size=5)
   
    r = rospy.Rate(10) #10hz
    
    
    msg = Dummy_Cam()
    
    msg.img = [1, 1, 1, 1, 0, 1, 1, 1, 1]

    while not rospy.is_shutdown():
        
        pub.publish(msg)
        r.sleep()
 
if __name__ == '__main__':
 
    rospy.init_node('dummy_image', anonymous=True)
  
    try:
        dummycam()
    except rospy.ROSInterruptException: pass
