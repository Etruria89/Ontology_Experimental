#!/usr/bin/env python

import rospy
import time
from cluedo_exp.srv import OracleCall, OracleCallResponse

"""
This script creates a service node for the generation of 
the new targets for the robot
 
...
    
Function
-----------
target_rand(req): fills the server placeholders x_target and y_target
    with a random number between -6.0 and 6.0
"""


def oracle_call(req):

    """
    Parameters:
    ----------
    req : is called with Target request (empty)
          and return instances of Target response
    see Target srv:
    ---
    float32 x_target
    float32 y_target
    when called fills the server placeholders x_target and y_target
    with a random number between -6.0 and 6.0 
    """

    who = req.who
    what = req.what
    where = req.where    
    id_str = req.id_str
    
    solution_id = rospy.get_param('solution_ID')    

    time.sleep(5)
    
    if id_str == solution_id:
        print("The killer is %s with the %s in the %s" %(who[2:-2], what[2:-2], where[2:-2])) 
        Result = 1
    else:
        print("Look for other hints, the solution is not correct.")
        Result = 0
        
    return OracleCallResponse(Result)


def main():

    # Consistency check Service Server
    rospy.init_node('Oracle_Query')

    #Server istance
    rospy.Service('Oracle_Query', OracleCall, oracle_call)
    while not rospy.is_shutdown():
        rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException: pass  
