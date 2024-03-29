#!/usr/bin/env python2

# /* ----------------------------------------------------------------------------
#  * Copyright 2020, Jesus Tordesillas Torres, Aerospace Controls Laboratory
#  * Massachusetts Institute of Technology
#  * All Rights Reserved
#  * Authors: Jesus Tordesillas, et al.
#  * See LICENSE file for the license information
#  * -------------------------------------------------------------------------- */

from rosgraph import ROS_HOSTNAME
import rospy
from faster_msgs.msg import Mode
from snapstack_msgs.msg import Goal, State
from geometry_msgs.msg import Pose, PoseStamped
from nav_msgs.msg import Odometry
from behavior_selector.srv import MissionModeChange
import math

def quat2yaw(q):
    yaw = math.atan2(2 * (q.w * q.z + q.x * q.y),
                     1 - 2 * (q.y * q.y + q.z * q.z))
    return yaw

class Faster_Commands:

    def __init__(self):
        self.mode=Mode();
        self.pose = Pose();
        self.mode.mode=self.mode.ON_GROUND
        self.pubGoal = rospy.Publisher('goal', Goal, queue_size=1)
        self.pubMode = rospy.Publisher("faster/mode",Mode,queue_size=1,latch=True) #TODO Namespace
        self.pubClickedPoint = rospy.Publisher("/move_base_simple/goal",PoseStamped,queue_size=1,latch=True)

        self.is_ground_robot=rospy.get_param('~is_ground_robot', False);

        print("self.is_ground_robot=", self.is_ground_robot)

        self.alt_taken_off = 1.2; #Altitude when hovering after taking off
        self.alt_ground = 0; #Altitude of the ground
        self.initialized=False;

    #In rospy, the callbacks are all of them in separate threads
    def stateCB(self, data):
        self.pose.position.x = data.pose.pose.position.x
        self.pose.position.y = data.pose.pose.position.y
        self.pose.position.z = data.pose.pose.position.z
        self.pose.orientation = data.pose.pose.orientation

        if(self.initialized==False):
            self.pubFirstGoal()
            self.initialized=True

    #Called when buttom pressed in the interface
    def srvCB(self,req):
        if(self.initialized==False):
            print "Not initialized yet"
            return

        if req.mode == req.START and self.mode.mode==self.mode.ON_GROUND:
            print "Taking off"
            self.takeOff()
            print "Take off done"

        if req.mode == req.KILL:
            print "Killing"
            self.kill()

        if req.mode == req.END and self.mode.mode==self.mode.GO:
            print "Landing"
            self.land()
            print "Landing done"


    def sendMode(self):
        self.mode.header.stamp = rospy.get_rostime()
        self.pubMode.publish(self.mode)


    def takeOff(self):
        print "Taking off"
        goal=Goal();
        goal.power=True
        goal.p.x = self.pose.position.x;
        goal.p.y = self.pose.position.y;
        goal.p.z = self.pose.position.z;
        if(self.is_ground_robot==True):
            self.alt_taken_off=self.pose.position.z;
        #Note that self.pose.position is being updated in the parallel callback
        while(  abs(self.pose.position.z-self.alt_taken_off)>0.1  ): 
            goal.p.z = min(goal.p.z+0.0035, self.alt_taken_off);
            #rospy.sleep(0.004) #TODO hard-coded
            self.sendGoal(goal)
        rospy.sleep(1.5) 
        self.mode.mode=self.mode.GO
        self.sendMode()
        print("Take off")


    def land(self):
        goal=Goal();
        goal.p.x = self.pose.position.x;
        goal.p.y = self.pose.position.y;
        goal.p.z = self.pose.position.z;

        #Note that self.pose.position is being updated in the parallel callback
        while(abs(self.pose.position.z-self.alt_ground)>0.1):
            goal.p.z = max(goal.p.z-0.0035, self.alt_ground);
            self.sendGoal(goal)
        #Kill motors once we are on the ground
        self.kill()

    def kill(self):
        goal=Goal();
        goal.power=False
        self.sendGoal(goal)
        self.mode.mode=self.mode.ON_GROUND
        self.sendMode()

    def sendGoal(self, goal):
        goal.yaw = quat2yaw(self.pose.orientation)
        goal.header.stamp = rospy.get_rostime()
        self.pubGoal.publish(goal)

    def pubFirstGoal(self):
        msg=PoseStamped()
        msg.pose.position.x=self.pose.position.x
        msg.pose.position.y=self.pose.position.y
        msg.pose.position.z=1.0
        msg.header.frame_id="world"
        msg.header.stamp = rospy.get_rostime()
        self.pubClickedPoint.publish(msg)

                  
def startNode():
    c = Faster_Commands()
    # s = rospy.Service("/change_mode",MissionModeChange,c.srvCB)
    rospy.Subscriber("/mavros/local_position/odom", Odometry, c.stateCB)
    c.takeOff()
    rospy.spin()

if __name__ == '__main__':
    rospy.init_node('faster_commands')  
    startNode()
    print "Faster Commands started" 