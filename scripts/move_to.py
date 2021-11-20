#! /usr/bin/env python


"""
 go_to_point is a python script which provides the navigation part of the 
 robot. 
 
 """

import rospy
import actionlib
from cluedo_exp.msg import Dummy_Odom
import cluedo_exp.msg
import time
import random


global start_position


action=None


def clbk_odom(msg):

    global start_position  
    
    start_position = [msg.x_pos, msg.y_pos]

   
def go_to_point(goal):

    global action, start_position
    
    # Initialize feedback
    feedback = cluedo_exp.msg.MoveFeedback() 
    action_results = cluedo_exp.msg.MoveResult()   
    # Initilize the success
    success = False


    desired_position = [goal.target_x, goal.target_y]
    
    try:
        print("This is my starting position")
        print(start_position)
    except: 	
        pass   
    print("I am going to:")
    print(desired_position)
    
    time.sleep(10)
    
    # Publish on the dummy odometry message
    msg_odom = Dummy_Odom()
    
    msg_odom.x_pos = goal.target_x
    msg_odom.y_pos = goal.target_y
    
    #Roll a dice to simulate a preemt request
    rand_max = 50
    preemp_probability =random.randint(1, rand_max)
    
    if preemp_probability == rand_max: 
    	# Preempt the action
        action.is_preempt_requested()
        feedback.status = 'Goal was preempted'
        action.set_preempted() 
        success = False
        print("PREEMPTED!!!!!!!!!!!!!!!")
    else: 
        # Check the position and go on
        if (msg_odom.x_pos == goal.target_x) and (msg_odom.y_pos == goal.target_y):      
        
            print("Arrived!")
            success = True            
            feedback.status = 'Goal reached'
            
            
    # Check that the new position coincides with the goal
    print("Final position check") 
    print(msg_odom.x_pos, msg_odom.y_pos)
    print(goal.target_x, goal.target_y)    
  
    # Publish feedback and results   
    action.publish_feedback(feedback)
    action_results.reached = success
    print("Success status")
    print(success)
    
    if success:
        print("Setting success")
        action.set_succeeded(action_results)                      
    
    return

def main():

    global action
    
    #Subscribe to the dummy odometry msg
    odom_sub = rospy.Subscriber('dummy_odometry', Dummy_Odom, clbk_odom)
    
    # Action server
    rospy.init_node('move_to')
    action = actionlib.SimpleActionServer('/move_to', cluedo_exp.msg.MoveAction, execute_cb = go_to_point, auto_start=False)
            
    action.start()
    
    rospy.spin()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException: pass  
