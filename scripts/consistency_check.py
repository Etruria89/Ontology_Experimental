#!/usr/bin/env python

import rospy
from cluedo_exp.srv import Consistency, ConsistencyResponse
from armor_msgs.msg import * 
from armor_msgs.srv import * 

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

def armor_consistency(req):

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

    Complete_query = []
    Result =  0
    hyp_id = req.id_number
    
    print("Here")

    # Get ID of all Complete hypothesis
    try:
        # Completeness check
        req = ArmorDirectiveReq()
        req.client_name = 'tutorial'
        req.reference_name = 'ontoTest'
        req.command = 'QUERY'
        req.primary_command_spec = 'IND'
        req.secondary_command_spec = 'CLASS'
        req.args = ['COMPLETED']
        msg = armor_service(req)
        res = msg.armor_response.queried_objects
        res_final = clean_result(res)
        
        if hyp_id in res_final:
            print('%s is complete' %(hyp_id))
      
            # Consistency check    
            req = ArmorDirectiveReq()
            req.client_name = 'tutorial'
            req.reference_name = 'ontoTest'
            req.command= 'QUERY'
            req.primary_command_spec = 'IND'
            req.secondary_command_spec = 'CLASS'
            req.args = ['INCONSISTENT']
            msg = armor_service(req)
            res_cons = msg.armor_response.queried_objects
            print("Consistency check")
            print(res_cons)
            res_final_cons = clean_result(res_cons)
            print(res_final_cons)
            
            if hyp_id in res_final_cons:
                print('%s is inconsistent' %(hyp_id))
                print("Call move to next room action service")
            else:
                print('%s is consistent' %(hyp_id))
                print("Go to oracle room")           	
        
        else:
           print("Incomplete solution, ignore it!")
           print("Call move to next room action service")
            
    except:   
        raise ValueError('Consistency check failed!')
    
   
    
    return ConsistencyResponse(Result)


def main():

    global  armor_service

    # Consistency check Service Server
    rospy.init_node('Consistency_check_srv')

    # Armor client
    armor_service = rospy.ServiceProxy('armor_interface_srv', ArmorDirective)

    #Server istance
    rospy.Service('Consistency_check_srv', Consistency, armor_consistency)
    rospy.spin()

if __name__ == '__main__':
    main()
