#!/usr/bin/env python

import roslib
import rospy
import smach
import smach_ros
import time
import itertools
import random
import copy
import numpy as np
from armor_msgs.msg import * 
from armor_msgs.srv import * 


# Initialize the game
who_list_full = [ "White", "Green", "Peacock", "Plum", "Scarlet", "Mustard"]
where_list_full = ["Kitchen", "Hall", "Ballroom", "Conservatory", "Dining", "Billiard", "Library", "Lounge", "Study"]
what_list_full = [ "Candlestick", "Revolver", "Knife", "Pipe", "Rope", "Wrench"]

classes = ["PERSON", "PLACE", "WEAPON"]

check_protege = "/root/ros_ws/src/cluedo_exp/ontology/check.owl"
ontology_path ='/root/ros_ws/src/cluedo_exp/ontology/cluedo_ontology.owl'

room_number = 6 

armor_service = None

# Initialize the entity list for ontology definition
who_list = copy.deepcopy(who_list_full) 
where_list = copy.deepcopy(where_list_full) 
what_list = copy.deepcopy(what_list_full)

def solution_creator():
    # Randomly select the solution
    
    who_sol = random.choice(who_list)
    where_sol = random.choice(where_list)
    what_sol = random.choice(what_list)   
    
    solution = [who_sol, where_sol, what_sol]	
	
    return(solution)
    
def solution_upload(list_of_hints):

     who = list_of_hints[0]
     where = list_of_hints[1]
     what = list_of_hints[2]
     
     # Create the individuals
     add_entity(who, classes[0])
     add_entity(where, classes[1])
     add_entity(what, classes[2])
     
     # print("The killer is %s in the %s with the %s" %(who,  where, what))
     
def load_file(ontology_path):

    try:
    
        req = ArmorDirectiveReq()
        req.client_name = 'tutorial'
        req.reference_name = 'ontoTest'
        req.command = 'LOAD'
        req.primary_command_spec = 'FILE'
        req.secondary_command_spec = ''
        req.args = [ontology_path, 'http://www.emarolab.it/cluedo-ontology', 'true', 'PELLET', 'true']
        msg = armor_service(req)
        res = msg.armor_response
        
        print("Ontology loaded!")
    except:    
        raise ValueError('Ontology NOT loaded !')   
     
def add_entity(instance, class_type):

    try:    
        
        req = ArmorDirectiveReq()
        req.client_name = 'tutorial'
        req.reference_name = 'ontoTest'
        req.command = 'ADD'
        req.primary_command_spec = 'IND'
        req.secondary_command_spec = 'CLASS'
        req.args = [instance, class_type]
        msg = armor_service(req)
        res = msg.armor_response
        reasoning()
        disjoint(class_type)
        reasoning()
        #print('%s added to the class %s!' % (instance, class_type))
        
        
    except:    
        raise ValueError('Adding of %s in %s failed!' % (instance, class_type))

def disjoint(class_type):
    try:
    
        req=ArmorDirectiveReq()
        req.client_name= 'tutorial'
        req.reference_name= 'ontoTest'
        req.command= 'DISJOINT'
        req.primary_command_spec= 'IND'
        req.secondary_command_spec= 'CLASS'
        req.args= [class_type]
        msg = armor_service(req)
        		 
    except:    
        raise ValueError('Failed to disjoint entities in %s class!' % (class_type)) 

def hypotesis_generator(hyp_list):

    # Initialize the counter for the hypothesis
    hyp_count = 0
    hyp_string_main = "HP"
    # Generate the hypothesis for all the permutations
    for hyp in hyp_list:
        hyp_string = hyp_string_main + str(hyp_count)
        # Get the class of each element and creat an hypothesis
        for element in hyp:
            print(element)
            if element in who_list_full:
               hyp_classes = 'who'
            elif element in where_list_full:
               hyp_classes = 'where'
            else:
               hyp_classes = 'what'
               
         
            try:    
        
                req = ArmorDirectiveReq()
                req.client_name = 'tutorial'
                req.reference_name = 'ontoTest'
                req.command = 'ADD'
                req.primary_command_spec = 'OBJECTPROP'
                req.secondary_command_spec = 'IND'
                req.args = [hyp_classes, hyp_string, element]
                msg = armor_service(req)
                res = msg.armor_response         
        
                print('%s added to the class %s as %s!' % (element, hyp_string, hyp_classes))
        
            except:    
                raise ValueError('Adding of %s in %s as %s failed!' % (element, hyp_string, hyp_classes))
         
            
        #print(hyp) 
        #print(hyp_classes)           
         
        hyp_count += 1
 
     
 
def reasoning():

    try:
        req = ArmorDirectiveReq()
        req.client_name = 'tutorial'
        req.reference_name = 'ontoTest'
        req.command = 'REASON'
        req.primary_command_spec = ''
        req.secondary_command_spec = ''
        req.args= []
        msg = armor_service(req)
        res = msg.armor_response
        
    except:    
        raise ValueError('Reasoning failed!')	   


def save_owl():

    try:
        req = ArmorDirectiveReq()
        req.client_name = 'tutorial'
        req.reference_name = 'ontoTest'
        req.command = 'SAVE'
        req.primary_command_spec = ''
        req.secondary_command_spec = ''
        req.args= [check_protege]
        msg = armor_service(req)
        res = msg.armor_response
        
    except:    
        raise ValueError('Saving ontology failed!')	

def main():

    global  armor_service

    # Initialize the node
    rospy.init_node('armor_init')  
    
    armor_service = rospy.ServiceProxy('armor_interface_srv', ArmorDirective)
    
    rospy.wait_for_service('armor_interface_srv') 
    
    # Load the ontology
    load_file(ontology_path)
    
    if room_number < 3:
        raise ValueError('Not enough rooms to find a correct hypothesis.')
        
    elif room_number == 3:
    	print("Too easy you have only to collect the hints...")
    	solution = solution_creator()
    	
    	solution_upload(solution)   
    		
    elif room_number > 9:   
    	raise ValueError('Too many rooms in this game!!!')    
    		
    else:
    
        # Generate a solution and add the entity in the ontology
        solution = solution_creator()
        solution_upload(solution) 
        
        # Initialize the solution space
        solution_space = copy.deepcopy(solution)
        
        print(solution_space)
        
        # Remove the solution elements from their list
        who_list.remove(solution[0])
        where_list.remove(solution[1])
        what_list.remove(solution[2])          
        
        
        # Roll a dice with 3 faces for each remaining rooms and randomly pick elements from the list
        for i in range(3, room_number):
        
            list_id = random.randint(0, 2) 
            
            print(list_id)
            if list_id == 0:
                # Extract a new "who"
                new_entity = random.choice(who_list)
                class_type = classes[0]
                who_list.remove(new_entity)
            elif list_id == 1:
                # Extract a new "where"
                new_entity = random.choice(where_list)
                class_type = classes[1]
                where_list.remove(new_entity)
            elif list_id == 2:
                # Extract a new "what"
                new_entity = random.choice(what_list)
                class_type = classes[2]
                what_list.remove(new_entity) 
               
            add_entity(new_entity, class_type)    
            
            solution_space.append(new_entity)
              
            print(solution_space) 
            
            
        # Create all the permutations with the obtained list of entity
        # set and sort are used to remove duplicates
        hypothesis_with_duplicates = itertools.permutations(solution_space, 3)
        sorted_hypothesis = []
        for x in hypothesis_with_duplicates:
            sorted_hypothesis.extend([sorted(list(x))])
        
        hypothesis = list(set(tuple(x) for x in sorted_hypothesis))
                
        # Generate all the hypothesis (INCONSISTENT or CONSISTENT)
        hypotesis_generator(hypothesis)
        
        # Find solution ID
        for ID in range(0, len(hypothesis)):
             if list(hypothesis[ID]) == sorted(solution):  
             	sol_ID = ID          	  
        print(sol_ID) 
        rospy.set_param('solution_ID', sol_ID) 
    	
    	
    # Make knowledge explicit
    reasoning()		
   
    #Save the model to inspect it
    save_owl()    

    # Wait for ctrl-c to stop the application
    rospy.spin()


if __name__ == '__main__':
    main()
