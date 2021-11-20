#! /usr/bin/env python

import rospy
import time
import random
import copy
import itertools
from std_srvs.srv import *
from cluedo_exp.msg  import Dummy_Odom
from actionlib_msgs.msg import GoalID
from cluedo_exp.srv import IPU
from cluedo_exp.srv import Get_ID
from cluedo_exp.srv import Consistency
from cluedo_exp.srv import OracleCall
import math
import actionlib
import cluedo_exp.msg._MoveAction
from cluedo_exp.msg import Dummy_Odom

global status, game_location, block_note, hyp_dict
global discovered_hyp_space, requested_hyp, comp_con_discovered_hyp_space

#Can be modified in a disctionary
all_dummy_locations = {"Kitchen" :[-1, -1], 
	"Hall": [0, -1], 
	"Ballroom": [1, -1], 
	"Conservatory": [-1, 0],
	"Billiard": [-1, -0.25], 
	"Dining":  [-1, 0.25], 
	"Library": [-1, 1], 
	"Lounge": [0, 1], 
	"Study": [1, 1]}
		       

# Oracle location
oracle_location = [0, 0]

# Define the initial system status
state_ = 0

# Blocke notes where the robot record the hints it has found
block_note = []

# List of discovered consistent hypothesis
discovered_hyp_space = []
comp_con_discovered_hyp_space = []
inconsisitent_hyp = []
# List of hypothesis requested to the oracle
requested_hyp = []

# Hypothesis dictionary
hyp_dict = {}


# Evaluate the  active rooms only
room_number = rospy.get_param('room_number')

game_location = random.sample(list(all_dummy_locations.keys()), room_number) 


def clbk_odom(msg):

    global start_position  
    
    start_position = [msg.x_pos, msg.y_pos]

def change_state(state):

    """
    This function is responsible for specifyng the behaviour of the robot by defining its state.
    It is called the by the main node after that a target is reached and the input parameters have been
    set in the user intrface.
    This function depending on the specific state reaad from the server parameter the list the 
    settings of each desired state and it forwards them to teh main function to 
    publish the information in teh specific topic.
    This function is also called with state == 2 when an action has been sucessfully accomplished to request a new input and it cancels the target of the /move_base
	node by publishing in the node /move_base/cancel.
    Alternatively it can be triggered when the 'Bug_0' algorithm is active but the robot has not been able to reach the target
    after a specified amount of time set to 120 seconds
    """
    global state_, state_desc_, start, bug_trigger
    global game_location, block_note, hyp_dict
    global discovered_hyp_space, requested_hyp, tobe_query, comp_con_discovered_hyp_space
    global who, what, where
    global srv_client_IPU_, srv_client_go_to_point, srv_client_consistency_, srv_client_query_
    global action_client
    global odom_pub


    state_ = state
    # log = "state changed: %s" %(state_) # state_desc_[state]
    # rospy.loginfo(log)   

    if state_ == 1:     
          	
        	
        target_name = random.choice(game_location)
        target_pos = all_dummy_locations[target_name]
        x_pos = target_pos[0]
        y_pos = target_pos[1]
    	# Remove the location from the location to explore
        print("Going to the %s" %(target_name))  
        print(game_location)
    	
        #Send goal to action server
        #!!!!!!!!!!!!!!!!!!!!!!!!!!
        action_client.wait_for_server()
    	
    	
        # Creates a goal to send to the action server.
        goal = cluedo_exp.msg.MoveGoal()
        goal.target_x = x_pos
        goal.target_y = y_pos
        # Sends the goal to the action server.
        action_client.send_goal(goal)
    	# Waits for the server to finish performing the action.
        action_client.wait_for_result()
        
           	
    	# Prints out the result of executing the action
        result = action_client.get_result()
    	
        if result.reached:
        
    	    print("%s reached" %(target_name))    	
    	    state_ = 2	
    	    msg_odom = Dummy_Odom()
    	    msg_odom.x_pos = goal.target_x
    	    msg_odom.y_pos = goal.target_y
    	    odom_pub.publish(msg_odom)
    	    game_location.remove(target_name)
    	    # Comment this line to come back to the same room
        else:
            state_ = 1
    	    
         
    elif state_ == 2:
        
        print("Looking for hints!")
        time.sleep(2)
        
        command = 1
        rospy.wait_for_service('IPU')        
        hint = srv_client_IPU_(command)
        print("%s found" %hint)
        
        while hint.output in block_note:
            print("Ask for new hint!")
            try:
                rospy.wait_for_service('IPU', timeout = 1)
            except:
                # The service is not avaialble, trigger the exception
                rosply.logerr('%s', e)
                rospy.signal_shutdown('timeout has reachede; shutting down the IPU cluient')
                sys.exit(1)
            hint = srv_client_IPU_(command)
       
        print("New hint received!")
        block_note.append(hint.output)
        print("This is your block notes:")
        print(block_note) 
        
        # TOO SLOW VERSION
        #if hint.output in block_note:
         #   print("This is not your lucky day!")
          #  print("%s is already in your block note!" % hint.output)
        #else:
         #   block_note.append(hint.output)
          #  print("This is your block note:")
          #  print(block_note)
        
        print("Reasoning on the next action")
        print(block_note)
        state_ = 3

        
    elif state_ == 3:
    
        # Create all the permutations with the hints present in the block-note
        hypothesis_with_duplicates = itertools.permutations(block_note, 3)
        sorted_hypothesis = []
        for x in hypothesis_with_duplicates:
            sorted_hypothesis.extend([sorted(list(x))])
        
        hypothesis = list(set(tuple(x) for x in sorted_hypothesis))
        
        
        print("HYPOTHESIS FROM REASONER")
        print(hypothesis)
        
        
        for hyp in hypothesis:    
          
            dic_vals = hyp_dict.values() 
            
            if list(hyp) in dic_vals:
               print(hyp)
               print("Alrady checked!!!!!!!!!!!!!!!!!!")
               time.sleep(2)
            else:
            
                print("Checking ...")
                print(hyp)
                time.sleep(2)
            
                try:
                    rospy.wait_for_service('Get_ID_srv', timeout = 5)
                except:
                    # The service is not avaialble, trigger the exception
                    rosply.logerr('%s', e)
                    rospy.signal_shutdown('timeout has reachede; shutting down the Get_ID_srv cluient')
                    sys.exit(1)              
              
                res_hyp_id = srv_client_getHyp_(hyp[0], hyp[1], hyp[2])
                print("Answer from hypothesis checker")
                hyp_id = res_hyp_id.id_number
                ordered_hyp = [hyp[0], hyp[1], hyp[2]]
                
                print("ORDERED HYP. added to dictionary")
                print(ordered_hyp)
                hyp_dict[hyp_id] = ordered_hyp  
                
                
                # Verify hypothesis consistency and completeness
            
                if hyp_id not in discovered_hyp_space:
                    print('%s not in discovered space list' %hyp_id)
                    try:
                        rospy.wait_for_service('Consistency_check_srv', timeout = 5)
                    except:
                        # The service is not avaialble, trigger the exception
                        rosply.logerr('%s', e)
                        rospy.signal_shutdown('timeout has reachede; shutting down the Consistency check cluient')
                        sys.exit(1)              
              
                    res_check = srv_client_consistency_(hyp_id)
                    print("REULTS PRINTED")
                    print(res_check)
                    check = res_check.consistent
                    print(check)
                    time.sleep(5)
                    print(hyp_id)
                    print(discovered_hyp_space)
                    if (hyp_id not in discovered_hyp_space) and check and (hyp_id not in requested_hyp) and (hyp_id not in inconsisitent_hyp):           
                        comp_con_discovered_hyp_space.append(hyp_id)
                        print(discovered_hyp_space)
                        who = res_check.who
                        what = res_check.what
                        where = res_check.where
  
                    elif not check:
                        inconsisitent_hyp.append(hyp_id)	
                    discovered_hyp_space.append(hyp_id)  
                    print("APPENDING HIP")  
                  
                else:
                    print('%s in hyphotesis list' %hyp_id) 
        
        tobe_query = list(set(comp_con_discovered_hyp_space) - set(requested_hyp))      
        
        print('Resume:')  
        print('Discovered hypotheses:')
        print(discovered_hyp_space)   
        print('Complete and consistent hypoteses:')
        print(comp_con_discovered_hyp_space)  
        print('To be asked:')
        print(tobe_query)
        
        #print('Dictionary:')
        #print(hyp_dict)          
        
        # If you have not to query keep on looking for hints
        if not tobe_query:
            state_ = 1
        # If you have something to query try the solution   
        else:
            state_ = 4
             


    elif state_ == 4:
    
        oracle_reached = False
        
        x_pos = 0.0
        y_pos = 0.0
        print("Going to the oracle")
    	
        #Send goal to action server
        #!!!!!!!!!!!!!!!!!!!!!!!!!!
        action_client.wait_for_server()
    	
    	
        # Creates a goal to send to the action server.
        goal = cluedo_exp.msg.MoveGoal()
        goal.target_x = x_pos
        goal.target_y = y_pos
        # Sends the goal to the action server.
        action_client.send_goal(goal)
    	# Waits for the server to finish performing the action.
        action_client.wait_for_result()
        
           	
    	# Prints out the result of executing the action
        result = action_client.get_result()
    	
        if result.reached:
            oracle_reached = True
            print("Oracle reached") 
            msg_odom = Dummy_Odom()
            msg_odom.x_pos = goal.target_x
            msg_odom.y_pos = goal.target_y
            odom_pub.publish(msg_odom)
	

            print("Tento la fortuna!!!")
        
            # Query the oracle with all the possible hypothesis that are fine
            for query in tobe_query:
        
                print(query)
                print(tobe_query)
                time.sleep(5)
            
                hyp_data = hyp_dict[query]            
                  
              
                try:
                    rospy.wait_for_service('Oracle_Query', timeout = 3)
                except:
                    # The service is not avaialble, trigger the exception
                    rosply.logerr('%s', e)
                    rospy.signal_shutdown('timeout has reachede; shutting down the Oracle Query cluient')
                    sys.exit(1)  
                res = srv_client_query_(query, who, what, where)	
            
                if res.response:
                    print("You win!!!!")
                    state_ = 100
                    break
                
                else:
            	    # Add the hypothesis in the list of the one non correcy
            	    requested_hyp.append(query)
            	    # Start looking for new hints
            	    state_ = 1
        else:
            state_ = 4
                

    elif state_ == 100:
    
        print("Rest, enjoy your glory!")
        state_ = 999

def main():

    # Global variables for investigation 
    global status, game_location, block_note, hyp_dict
    global discovered_hyp_space, requested_hyp, tobe_query
    global who, what, where
    # Global proxy server
    global srv_client_go_to_point_, srv_client_IPU_, srv_client_getHyp_, srv_client_consistency_, srv_client_query_
    global action_client
    global odom_pub, odom_sub
    
    # Controller node
    rospy.init_node('Controller')
        
    # Publisher on dummy_odom msg
    odom_pub = rospy.Publisher('dummy_odometry', Dummy_Odom, queue_size=3)
    
    # Client services
    srv_client_IPU_ = rospy.ServiceProxy('IPU', IPU) 					    # Image processing unit client
    srv_client_getHyp_ = rospy.ServiceProxy('Get_ID_srv', Get_ID) 			    # Get hypotheses ID
    srv_client_consistency_ = rospy.ServiceProxy('Consistency_check_srv', Consistency)    # Get hypotheses completeness and consistency
    srv_client_query_ = rospy.ServiceProxy('Oracle_Query', OracleCall)    		    # Query hypothesis
    
    # Action client
    action_client = actionlib.SimpleActionClient('move_to', cluedo_exp.msg.MoveAction)
    
    
    time.sleep(10)
    rate = rospy.Rate(20)
    
    while not rospy.is_shutdown():

	# Initialization state
        if state_ == 0:
            
            print("Game started!")            
            print("I start exploring")         
            odom_sub = rospy.Subscriber('dummy_odometry', Dummy_Odom, clbk_odom)
            change_state(1)
            
        elif state_ == 1:


            print("Exploring!")
            time.sleep(2)
            change_state(1)
            
        elif state_ == 2:


            print("Look for hint called!")
            time.sleep(2)
            change_state(2)
            
        elif state_ == 3:
	    
            print("!!! REASONING !!!")
            print(block_note)
	    
            # If we do not have enough of hints it is better we go to another location
            if len(block_note) < 3:	
                print("Looking for more hints!!!")        
                change_state(1)
            # We have enugh of hints and we want to see which hypoyhesis we can formulate    
            else:    
                print("Formulate hypothesis")                   
                change_state(3)  
                                      	   
        elif state_ == 4:

            #print("Game started!")
            print("I am going to the oracle!!! :)")           
            change_state(4)

                
        elif state_ == 100:
            
            change_state(100)    
            
        elif state_ == 999:
            
            pass
   
        rate.sleep()
                   
if __name__ == '__main__':



    try:
        main()
    except rospy.ROSInterruptException: pass  
