# -*- coding: utf-8 -*-
"""NiryoOne class

This module demonstrates the niryone class and its methods. 
NiryoOne is destinate to perform diferents moves including grabing objects, 
incrementing axis, rotating.
"""

from niryo_one_tcp_client import *
import math, string, time

class Niryo(NiryoOneClient):
    """Custom Niryo Class herited from NiryoOneClient 
    
    This class implements methods to grab an object using (x,y,z) coordonates, set its position
    or increment specific axis
    
    Attributes:
        _is_quit         (bool): If we were already disconnected this variable prevent to run into multiple disconnection from the Niryo
        grip        (RobotTool): Tool when the robot is initialized
        initial_pose    (Tuple): Store the initial position to move to it later
        z_offset_conveyor (int): Offset between the conveyor (object origin) and the origin of the axis z from the Niryo
        z_offset_object   (int): Offset between object and the conveyor or the ground (measure the object high)
        x_offset_cam      (int): Offset between the depthai camera and the robot's end effector (usefull to precisely calcul object relative position from the Niryo)
    """

    def __init__(self, 
        ip: string="localhost", 
        grip: RobotTool= RobotTool.GRIPPER_2, 
        arm_velocity: int=30, 
        z_offset_conveyor: float=0, 
        z_offset_object:float=0.12, 
        x_offset_cam: float=0.01) -> None:
        super(Niryo, self).__init__()
        """Initialize the Niryo state

        Niryo will sequentialy set 
            * connect to tcp niryo server 
            * calibrate the robot with selected calibration mode
            * set arm velocity
            * set desired tool to get good grip
        
        Args:
            ip                     (:str:`str`, optional): Ip address of the niryo server 
            grip       (:RobotTool:`RobotTool`, optional): Selected grip to use with the Niryo
            arm_velocity           (:int:`int`, optional): Arm velocity in %
            z_offset_conveyor  (:float:`float`, optional): See Niryo's class Attributes
            z_offset_object    (:float:`float`, optional): See Niryo's class Attributes
            x_offset_cam       (:float:`float`, optional): See Niryo's class Attributes
        """
        self._is_quit = False
        self.grip = grip
        self.connect(ip)
        self.calibration()
        self.set_arm_max_velocity(arm_velocity)
        self.change_tool(self.grip)

        status, data = self.get_pose()
        if status is True:
            self.initial_pose = data
        else:
            print("[NIRYO] Error: " + data)

        self.stand_by = (0.8, 0.0, 0.4, 0., 1.1, 0.0)
        self.position = self.stand_by

        self.z_offset_conveyor = z_offset_conveyor
        self.z_offset_object = z_offset_object
        self.x_offset_cam = x_offset_cam

    @property
    def position(self):
        status, data = self.get_pose()
        if status is True:
            return data
        else:
            return "Error"
    
    @position.setter
    def position(self, value):
        self.x, self.y, self.z, self.roll, self.pitch, self.yaw = value
        status, data = self.move_pose(self.x, self.y, self.z, self.roll, self.pitch, self.yaw)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Moved successfully")

    def calibration(self, mode: CalibrateMode=CalibrateMode.AUTO) -> None:
        if self.need_calibration():
            print("[!] Starting calibration ..")
            status, data = self.calibrate(mode)
            if status:
                print("[*] Calibration done")
            else:
                print("[*] Impossible to calibrate")
        else:
            print("[*] No need to calibrate")
    
    def quit(self) -> None:
        if self._is_quit == False:
            print("[NIRYO] Disconnecting .. ") 
            self._is_quit = True
            super().quit()

    def increment_pos_x(self, value: float=0.10):
        status, data = self.shift_pose(RobotAxis.X, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_y(self, value: float=0.15):
        status, data = self.shift_pose(RobotAxis.Y, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    def increment_pos_z(self, value: float=0.1):
        status, data = self.shift_pose(RobotAxis.Z, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_pitch(self, value: float=0.2):
        status, data = self.shift_pose(RobotAxis.PITCH, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_roll(self, value: float=0.3):
        status, data = self.shift_pose(RobotAxis.ROLL, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_yaw(self, value: float=0.3):
        status, data = self.shift_pose(RobotAxis.YAW, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    def increment_pos(self, axis: str, value: float):
        print("[NIRYO] Incrementing axis {} with value {}".format(axis, value))
        try:
            if axis == "x": self.increment_pos_x(value)
            if axis == "y": self.increment_pos_y(value)
            if axis == "z": self.increment_pos_z(value)
            if axis == "roll": self.increment_pos_roll(value)
            if axis == "yaw": self.increment_pos_yaw(value)
            if axis == "pitch": self.increment_pos_pitch(value)
        except:
            print("[NIRYO] Incorrect value {} or axis {}".format(value, axis))

    # Going back to initial pose
    def go_to_initial_pose(self):
        if self.initial_pose is not None:
            status, data = self.move_pose(*self.pose_to_list(self.initial_pose))
            if status is False:
                print("Error: " + data)
            else:
                print("[*] Moved successfully to initial pose")

    def pick_object(self, x=0.25, y=0.0, z=0.14, roll=0.0, pitch=1.57, yaw=0.0):
        pick_pose = PoseObject(
            x=x, y=y, z=z,
            roll=-roll, pitch=pitch, yaw=yaw,
        )
        self.pick_from_pose(*pick_pose.to_list())

    def place_object(self, x=-0.01, y=0.23, z=0.12, roll=-0., pitch=1.57, yaw=-1.57):
        place_pose = PoseObject(
            x=x, y=y, z=z,
            roll=-roll, pitch=pitch, yaw=yaw,
        )
        self.place_from_pose(*place_pose.to_list())

    def calc_target(self, x_ia: float, y_ia: float, z_ia: float):
        """  calc the coordinates with taking into acount the offset between the end effector and the cam """
        try:
            x_roi = round(math.sqrt(z_ia**2 - (self.z - self.z_offset_conveyor)**2)/2, 3) 
            doMove = True
        except:
            x_roi = None
            doMove = False
            print("[NIRYO] Wrong coordinates, impossible to get the sqrt of a negative number")

        y_roi = x_ia
        z_roi = self.z - self.z_offset_conveyor - self.z_offset_object
        try:
            return doMove, x_roi/1000 - self.x_offset_cam, round(y_roi/1000, 3), round(-z_roi, 3)
        except:
            return False, 0, 0, 0

    def move_to_roi(self, x_ia: int,y_ia: int,z_ia: int, ratio: float=0.2, z_offset_conveyor: float=None):
        """ move to roi based on depthai OAK-D 2.5D camera"""
        if z_offset_conveyor != None:
            self.z_offset_conveyor = z_offset_conveyor
        doMove, x_, y_, z_ = self.calc_target(x_ia, y_ia, z_ia)
        if doMove and 0 < x_ <= 0.38:
            # pos limit x from stand position 
            print("[NIRYO] Estimated position ({},{},{}) m \nwith z_offset_conveyor {} ; z_offset_object {} ; x_offset_cam".format(x_, y_, z_, self.z_offset_conveyor, self.z_offset_object, self.x_offset_cam))
            self.last_grab = (x_, y_, z_)
            # move to region of interest ex : x = 0.022m y = 0.033m z = 0.650m
            self.open_gripper(self.grip, 500)
            self.increment_pos_x(x_)
            self.increment_pos_y(y_)
            self.increment_pos_z(z_)
            self.close_gripper(self.grip, 500)
            self.position = self.stand_by
            self.open_gripper(self.grip, 500)
            time.sleep(0.5)
            self.close_gripper(self.grip, 500)
        elif doMove and x_ >= 0.4:
            print("[NIRYO] Wrong value of x too large for the Robot {},{},{}".format(x_, y_, z_))
        
    
