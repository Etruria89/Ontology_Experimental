#!/usr/bin/env python

import rospy
from cluedo_exp.srv import Get_ID, Get_IDResponse
from armor_msgs.msg import * 
from armor_msgs.srv import * 
import time

"""
This script creates a service node for the generation of 
the new targets for the robot
 
...
    
Function
-----------
target_rand(req): fills the server placeholders x_target and y_target
    with a random number between -6.0 and 6.0
"""

armor_service = None


def clean_result(query):
    for i in range(len(query)):
        temp=query[i]
        temp=temp.split('#')
        index=len(temp)
        temp=temp[index-1]
        query[i]=temp[:-1]
    return query
    

def armor_gethyp_ID(req):

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

    hint1 = req.hint1
    hint2 = req.hint2
    hint3 = req.hint3
    
    print(hint1, hint2, hint3)
    
    hint_list = sorted([hint1, hint2, hint3])
    
    prop_list = ['who', 'where', 'what']
    
    # Dummy response
    correct_Hyp_Str = "HP999"
    correct_Hyp_Id = -1 
    
    #print(hint_list)

    # Get ID of the hypothesis associated with the provided hints
    try:
       
        hyp_count = 0   
               
        while correct_Hyp_Id < 0 :
       
            Hyp_Id = 'HP' + str(hyp_count)
            
            hyp_hints = []
            
            for prop in prop_list:
            	
                req_ID = []
                time.sleep(1)
                req_ID = ArmorDirectiveReq()
                req_ID.client_name = 'tutorial'
                req_ID.reference_name = 'ontoTest'
                req_ID.command = 'QUERY'
                req_ID.primary_command_spec = 'OBJECTPROP'
                req_ID.secondary_command_spec = 'IND'
                req_ID.args = [prop, Hyp_Id]     
                                
                try:
                    rospy.wait_for_service('armor_interface_srv', timeout = 5)
                except:
                    # The service is not avaialble, trigger the exception
                    rosply.logerr('%s', e)
                    rospy.signal_shutdown('timeout has reachede; shutting down the armor_interface_srv cluient')
                    sys.exit(1)  
                                
                           
                msg_ID = armor_service(req_ID)
                
                
                
                res_ID = msg_ID.armor_response.queried_objects
                res_ID_final = clean_result(res_ID)
                
                hyp_hints += res_ID_final
                
                # print(Hyp_Id)
                # print(hyp_hints)
                
            if hint_list ==  sorted(hyp_hints): 
                correct_Hyp_Id = 1
                correct_Hyp_Str = Hyp_Id
                # print(Hyp_Id)
                
            hyp_count += 1
    
               
    except:   
        raise ValueError('Error while looking for the hypothesis ID!')
    
    Result = correct_Hyp_Str
    
    return Get_IDResponse(Result)


def main():

    global  armor_service

    # Consistency check Service Server
    rospy.init_node('Get_ID_srv')

    # Armor client
    armor_service = rospy.ServiceProxy('armor_interface_srv', ArmorDirective)

    #Server istance
    rospy.Service('Get_ID_srv', Get_ID, armor_gethyp_ID)
    while not rospy.is_shutdown():
        rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException: pass  
