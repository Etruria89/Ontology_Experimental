#!/usr/bin/env python

import rospy
import time
import random
from cluedo_exp.srv import IPU, IPUResponse
from cluedo_exp.msg import Dummy_Cam

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

def clbk_img(msg):
    
    global image
    
    image = msg.img
    
def clean_result(query):
    for i in range(len(query)):
        temp=query[i]
        temp=temp.split('#')
        index=len(temp)
        temp=temp[index-1]
        query[i]=temp[:-1]
    return query
    
def armor_get_all():

    class_list = ["PERSON", "PLACE", "WEAPON"]
   
    all_hints = []

    for cls in class_list:
   
        # Completeness check
        req = ArmorDirectiveReq()
        req.client_name = 'tutorial'
        req.reference_name = 'ontoTest'
        req.command = 'QUERY'
        req.primary_command_spec = 'IND'
        req.secondary_command_spec = 'CLASS'
        req.args = [cls]
        msg = armor_service(req)
        res = msg.armor_response.queried_objects
        res_final = clean_result(res)       
   
        all_hints = all_hints + res_final
        
    return all_hints


def IPU_call(req):

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

    request_ID = req.command    
    
    # Print the image
    # In this section t he image is processed
    # print(image)
    
    
    # The call comes during the investigation and we look for a hint
    if request_ID == 1:
    
        print("Hint search.")    
        
        # Get all the infividuals from armor and remove the hypothesis
        all_individuals = armor_get_all()
        
        print(all_individuals)
        
        # Waiting befor having the hint 
        sleep_time = rospy.get_param('invest_time')  
        time.sleep(2)
        Result = random.choice(all_individuals)
        
    # The call comes during the localization and we want to know where we are
    elif request_ID == 2:
    
        print("Localization ongoing.")
        time.sleep(2)
        Result = 'room'
          
    return IPUResponse(Result)

def main():


    global  armor_service
    # Armor client
    armor_service = rospy.ServiceProxy('armor_interface_srv', ArmorDirective)

    # IPU service
    rospy.init_node('IPU')   
    
    #Subscribe to the cam
    cam_sub = rospy.Subscriber('/dummy_image', Dummy_Cam, clbk_img)

    #Server istance
    rospy.Service('IPU', IPU, IPU_call)
    rospy.spin()
    

if __name__ == '__main__':
    main()
