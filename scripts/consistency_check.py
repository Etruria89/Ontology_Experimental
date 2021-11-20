#!/usr/bin/env python

import rospy
import time
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
    
    # print("Here")

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
        try:
            rospy.wait_for_service('armor_interface_srv', timeout = 5)
        except:
            # The service is not avaialble, trigger the exception
            rospy.signal_shutdown('timeout has reachede; shutting down the armor_interface_srv cluient')
            sys.exit(1) 
        msg = armor_service(req)
        res = msg.armor_response.queried_objects
        res_final = clean_result(res)
        time.sleep(1)
        if hyp_id in res_final:
            print('%s is complete' %(hyp_id))
      
            # Consistency check    
            req_cons = ArmorDirectiveReq()
            req_cons.client_name = 'tutorial'
            req_cons.reference_name = 'ontoTest'
            req_cons.command= 'QUERY'
            req_cons.primary_command_spec = 'IND'
            req_cons.secondary_command_spec = 'CLASS'
            req_cons.args = ['INCONSISTENT']
            try:
                rospy.wait_for_service('armor_interface_srv', timeout = 5)
            except:
            # The service is not avaialble, trigger the exception
                rospy.signal_shutdown('timeout has reachede; shutting down the armor_interface_srv cluient')
                sys.exit(1) 
            msg_cons = armor_service(req_cons)
            res_incons = msg_cons.armor_response.queried_objects
            res_final_incons = clean_result(res_incons)
            time.sleep(1)
            if hyp_id in res_final_incons:
                print('%s is inconsistent' %(hyp_id))
                
                return ConsistencyResponse(0, 'N.A', 'N.A', 'N.A')
            else:
                print('%s is consistent' %(hyp_id))
                
                www = []
                for  w in ['who', 'what', 'where']:
                    # Completeness check
                    req_2 = ArmorDirectiveReq()
                    req_2.client_name = 'tutorial'
                    req_2.reference_name = 'ontoTest'
                    req_2.command = 'QUERY'
                    req_2.primary_command_spec = 'OBJECTPROP'
                    req_2.secondary_command_spec = 'IND'
                    req_2.args = [w, hyp_id]
                    try:
                        rospy.wait_for_service('armor_interface_srv', timeout = 5)
                    except:
                        # The service is not avaialble, trigger the exception
                        rosply.logerr('%s', e)
                        rospy.signal_shutdown('timeout has reachede; shutting down the armor_interface_srv cluient')
                        sys.exit(1) 
                    
                    
                    msg = armor_service(req_2)
                    res_2 = msg.armor_response.queried_objects
                    clean_res_2 = clean_result(res_2)
		          
                    www.append(clean_res_2)
                                
                return ConsistencyResponse(1, str(www[0]), str(www[1]), str(www[2]))
                
                print("Go to oracle room")           	
        
        else:
           print("Incomplete solution, ignore it!")
           print("Call move to next room action service")
            
    except:   
        raise ValueError('Consistency check failed!')
    
    return ConsistencyResponse(Result, 'N.A', 'N.A', 'N.A')


def main():

    global  armor_service

    # Consistency check Service Server
    rospy.init_node('Consistency_check_srv')

    # Armor client
    armor_service = rospy.ServiceProxy('armor_interface_srv', ArmorDirective)

    #Server istance
    rospy.Service('Consistency_check_srv', Consistency, armor_consistency)
    
    
    while not rospy.is_shutdown():
        rospy.spin()

if __name__ == '__main__':

    try:
        main()
    except rospy.ROSInterruptException: pass  
