#! /usr/bin/env python


import rospy
#from geometry_msgs.msg import Twist, Point
#from nav_msgs.msg import Odometry
#from tf import transformations
#import math
import actionlib
import actionlib.msg
import cluedo_exp.msg #this package



def change_state(state):
    """
    Update the current global state
    Args: state (int):  new state
    """
    global state_
    state_ = state
    print ('State changed to [%s]' % state_)

def done():
    """
    Stop the robot
    Set the robot velocities to 0.
    """
    
    print("Target reached!")
    
    print("Parameter server uopdated!")
    #twist_msg = Twist()
    #twist_msg.linear.x = 0
    #twist_msg.angular.z = 0
    #pub_.publish(twist_msg)
    
def stop_and_restart():

    """
    Stop the robot
    Set the robot velocities to 0.
    """
    
    print("Target not reached, Teleported to the old position!")
    #twist_msg = Twist()
    #twist_msg.linear.x = 0
    #twist_msg.angular.z = 0
    #pub_.publish(twist_msg)

    
def move_to(goal):

    """
    Set the appropriate behaviour depending
    on the current robot state, in orderd
    to reach the goal.
    The state machine keeps running until
    the goal is reached or the action is
    preempted (the goal gets cancelled).
    Args:
      goal (PoseActionGoal): (x,y,theta) goal pose
    """
    global act_s
    
    # get the current DUMMY position from the parameter server
    old_x = rospy.get_param('robot_x')
    old_y = rospy.get_param('robot_y')
    old_theta = rospy.param('robot_theta')
    
    rate = rospy.Rate(20)
    mission_complete = True
    change_state(0)

    feedback = cluedo_exp.msg.MoveFeedback()
    result = cluedo_exp.msg.MoveResult()
    
    target_reached = False
    
    while not rospy.is_shutdown() and not reached:
    
        if act_s.is_preempt_requested():
        
            feedback.status = 'Goal was preempted'
            act_s.set_preempted() # if we received the cancel we interrupt
            mission_complete = False
            stop_and_restart()
            
        else:
            feedback.status = "Goal pose reached!"
            done()
            # Update parameter server with new DUMMY pose
            rospy.set_param('robot_x', goal.x )
            rospy.set_param('robot_y', goal.y)
            rospy.set_param('robot_theta', goal.theta)
            mission_complete = True
                
        #act_s.publish_feedback(feedback) # feedback published at every step

        rate.sleep()
        
    if mission_complete:
        result.reached = success
        rospy.loginfo('Mission Complete!')
        act_s.set_succeeded(result)


def main():

    """
    Main function to manage 
    the robot behaviour
    """
    
    global pub_, act_s
    rospy.init_node('move_to')
    #pub_ = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    #sub_odom = rospy.Subscriber('/odom', Odometry, clbk_odom)
    act_s = actionlib.SimpleActionServer(
        '/move_to', cluedo_exp.msg.Move, move_to, auto_start=False) 
    act_s.start()
    
    rospy.spin()

if __name__ == '__main__':
    main()
