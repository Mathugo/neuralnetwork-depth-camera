# -*- coding: utf-8 -*-
"""NiryoOne class

This module demonstrates the niryone class and its methods. 
NiryoOne is destinate to perform diferents moves including grabing objects, 
incrementing axis, rotating.
"""

from niryo_one_tcp_client import *
import math, string, time
from typing import Dict, Tuple

# medium gripper
CONFIG_TOOL_2 = {
    "z_offset_conveyor": 0.055,
    "z_offset_vanilla" : 0.12,
    "x_offset_cam": 0.045,
    "y_offset_cam": 0.008
}
# large gripper
CONFIG_TOOL_3 = {
    "z_offset_conveyor": 0.073,
    "z_offset_vanilla" : 0.12,
    "x_offset_cam": 0.045,
    "y_offset_cam": 0.008
}

class Niryo(NiryoOneClient):
    """Custom Niryo Class herited from NiryoOneClient 
    
    This class implements methods to grab an object using (x,y,z) coordonates, set its position
    or increment specific axis using NiryoOneClient 
    
    Attributes:
        _is_quit         (bool): If we were already disconnected this variable prevent to run into multiple disconnection from the Niryo
        grip        (RobotTool): Tool when the robot is initialized
        initial_pose    (Tuple): Store the initial position to move to it later
        z_offset_conveyor (:obj:`float`, optional): Offset between the conveyor (object origin) and the origin of the axis z from the Niryo
        z_offset_vanilla  (:obj:`float`, optional): Offset between object and the conveyor or the ground (measure the object high)
        x_offset_cam      (:obj:`float`, optional): Offset in x between the depthai camera and the robot's end effector, in meter (useful to precisely calcul object relative position from the Niryo)
        y_offset_cam      (:obj:`float`, optional): Offset in y between the depthai camera and the robot's end effector, in meter (useful to precisely calcul object relative position from the Niryo)    
        _do_roi_counter   (int): Counter for the grabing sequence
        stand_by        (Tuple): Stand by position before starting the grabing sequence
    """

    def __init__(self, 
        ip: string="localhost", 
        grip: RobotTool=RobotTool.GRIPPER_3, 
        arm_velocity: int=30, 
      ) -> None:
        super(Niryo, self).__init__()
        """Initialize the Niryo state

        Niryo will sequentialy set 
            * connect to tcp niryo server 
            * calibrate the robot with selected calibration mode
            * set arm velocity
            * set desired tool
        
        Args:
            ip                     (:str:`str`, optional): Ip address of the niryo server 
            grip       (:RobotTool:`RobotTool`, optional): Selected grip to use with the Niryo
            arm_velocity           (:int:`int`, optional): Arm velocity in %
      """
        self._is_quit = False
        self.grip = grip

        if grip == RobotTool.GRIPPER_2:
            self.config = CONFIG_TOOL_2

        elif grip == RobotTool.GRIPPER_3:
            self.config = CONFIG_TOOL_3

        self.connect(ip)
        self.calibration()
        self.set_arm_max_velocity(arm_velocity)
        self.change_tool(self.grip)
        self._do_roi_counter = 1
        status, data = self.get_pose()
        if status is True:
            self.initial_pose = data
        else:
            print("[NIRYO] Error: " + data)

        self._stand_by = (0.10, 0.0, 0.4, 0., 1.2, 0.0)
        self.position = self.stand_by
        # shift between real object position in z_ia and the ground (otherwise we hit the ground with the niryo)
        self.z_offset_vanilla = self.config["z_offset_vanilla"]
        self.z_offset_conveyor = self.config["z_offset_conveyor"]
        self.x_offset_cam = self.config["x_offset_cam"]
        self.y_offset_cam = self.config["y_offset_cam"]

    def test_vanilla_shift(self):
        """Test if the provided offsets work"""
        # test vanilla shift 
        self.open_gripper(self.grip, 500)
        z = -(self.position.to_list()[2] - self.z_offset_vanilla )
        # substract - self.z_offset_vanilla if u want to test the conveyor shift
        self.increment_pos_z(z)
        print(f"Test shift z calculted {z}")
        self.close_gripper(self.grip, 200)
        self.position = self.stand_by

    @property
    def position(self) -> Tuple:
        """Tuple: Get the current position of the Niryo Robot (6 axis)"""
        status, data = self.get_pose()
        if status is True:
            return data
        else:
            return "Error"
    
    @position.setter
    def position(self, value):
        x, y, z, roll, pitch, yaw = value
        status, data = self.move_pose(x, y, z, roll, pitch, yaw)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Moved successfully")

    @property
    def stand_by(self):
        return self._stand_by

    @property
    def x(self):
        return self.position.to_list()[0]

    @property
    def y(self):
        return self.position.to_list()[1]    

    @property
    def z(self):
        return self.position.to_list()[2]

    def calibration(self, mode: CalibrateMode=CalibrateMode.AUTO) -> None:
        """Calibrate the Niryo using selected mode
        
            Args:
                mode (obj:`CalibrateMode`, optional): Mode of calibration, either AUTO or MANUAL

            Note:
                If MANUAL is set, someone has to manualy reach the joints limit for the robot to detect its internal offset values
        """
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
        """Quit method overloading NiryoOneClient.quit()
        
            We set the boolean variable *_is_quit* to prevent from disconnecting multiple times
        """
        if self._is_quit == False:
            print("[NIRYO] Disconnecting .. ") 
            self._is_quit = True
            super().quit()

    def increment_pos_x(self, value: float=0.10):
        """Increment axis x by float value

            Args:
                value (obj:`float`, optional): Value in meters
        """
        status, data = self.shift_pose(RobotAxis.X, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_y(self, value: float=0.15):
        """Increment axis y by float value

            Args:
                value (obj:`float`, optional): Value in meters
        """
        status, data = self.shift_pose(RobotAxis.Y, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    def increment_pos_z(self, value: float=0.1):
        """Increment axis z by float value

            Args:
                value (obj:`float`, optional): Value in meters
        """
        status, data = self.shift_pose(RobotAxis.Z, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_pitch(self, value: float=0.2):
        """Increment axis pitch by float value

            Args:
                value (obj:`float`, optional): Value in meters
        """
        status, data = self.shift_pose(RobotAxis.PITCH, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_roll(self, value: float=0.3):
        """Increment axis roll by float value

            Args:
                value (obj:`float`, optional): Value in meters
        """
        status, data = self.shift_pose(RobotAxis.ROLL, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_yaw(self, value: float=0.3):
        """Increment axis yaw by float value

            Args:
                value (obj:`float`, optional): Value in meters
        """
        status, data = self.shift_pose(RobotAxis.YAW, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    def increment_pos(self, axis: str, value: float):
        """Increment select axis by float value

            Args:
                axis    (obj:`str`): Axis in string format
                value (obj:`float`): Value in meters
        """
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

    def go_to_initial_pose(self):
        """Go to the initial position setted in the constructor"""
        if self.initial_pose is not None:
            status, data = self.move_pose(*self.pose_to_list(self.initial_pose))
            if status is False:
                print("Error: " + data)
            else:
                print("[*] Moved successfully to initial pose")

    def calc_x_y(self, x_ia: float, y_ia: float, z_ia: float):
        """Calculate the object x and y in niryo base
        
            Return:
                x (int): The x coordinate in meters
                y (int): The y coordinate in meters
        """
        pos = self.position.to_list()
        print(f"[NIRYO] Position before starting the sequence {pos[:3]}")
        z = pos[2]
        try:
            z = z - self.z_offset_vanilla - self.z_offset_conveyor
            z_ia = (z_ia - self.x_offset_cam)
            print(f"Z ia {round(z_ia, 2)} Z calculted {z} z vanilla shift {round(self.z_offset_vanilla, 2)} conveyor z offset {self.z_offset_conveyor}")
            x_roi = round(math.sqrt(z_ia**2 - z**2), 3)
            doMove = True
        except:
            x_roi = None
            doMove = False
            print(f"[NIRYO] Wrong coordinates, impossible to get the sqrt of a negative number : z {z} z_offset_vanilla {self.z_offset_vanilla} z_offset_conveyor {self.z_offset_conveyor} zia {z_ia}")

        return x_roi, y_ia

    def seq_first_move_to_roi(self, x_ia: float, y_ia: float, z_ia: float) -> bool:
        """First move to grab an object based on depthai OAK-D 2.5D camera

            Full sequence :
                * object detection 
                * get first coordinates from camera 
                * Move head | to the ground 
                * Move head until we reach x,y near a provided threshold error in meters
                * Dive in z axis from niryo and pick up the object 
            
            Args:
                x_ia (float): x coordonates from the camera base (meters)
                y_ia (float): y coordonates from the camera base (meters)
                z_ia (float): z coordonates from the camera base (depth in meters)

            Returns:
                True if the sequence has gone ok

        """
        # First we convert to meter and calculate X and Y 
        self.set_arm_max_velocity(100)
        x_ia/=1000
        y_ia/=1000
        z_ia/=1000
        print(f"[FIRST MOVE] x_ia {round(x_ia, 2)}m y_ia {round(y_ia, 2)}m z_ia {round(z_ia, 2)}m")
        # change coordinates, the camera is flipped so y become -y and in niryo base y is - x so y = -- x_ia = x_ia ; 
        # x is calculted using Pytagor Theorem 
        x, _ = self.calc_x_y(x_ia, y_ia, z_ia)
        if x != None:
            # we substract the offset cam so that the cam can see in center the objects
            x = x - self.x_offset_cam
            y = x_ia
            if x != None:
                print(f"X object calculted {x} Y calculated object calculated {y}")
                self.increment_pos_x(x)
                self.increment_pos_y(y)
            # now we turn the head (roll) and we again move until we reach satisfaying position
            pos = self.position.to_list()
            # x y z roll pitch yaw
            pos[4] = 1.5
            self.position = tuple(pos)
            print("[NIRYO] Head turned to the ground")
            return True
        else:
            False
    
    def seq_do_roi_loop(self, x_ia: float, 
        y_ia: float, z_ia: float, 
        absolute_pos_error_x_ia: float=0.02, 
        absolute_pos_error_y_ia: float=0.02, 
        threshold_algo_iteration: int=1,
        alpha: int=2) -> bool:
        """Second move to grab an object based on depthai OAK-D 2.5D camera

            This function is executed in a loop from ObjectDetection class,
            until we are not as close as possible from the detected object we continue aproaching optimal coordinates

            Note:
                To avoid big iteration and slow grabing, we've put an iteration threshold called threshold_algo_iteration
            
            Args:
                x_ia (float): x coordonates from the camera base (meters)
                y_ia (float): y coordonates from the camera base (meters)
                z_ia (float): z coordonates from the camera base (depth in meters)
                absolute_pos_error_x_ia (obj:`float`, optional): Minimal distance to the axis x of the cam and the detected object(in meters)
                absolute_pos_error_y_ia (obj:`float`, optional): Minimal distance to the axis y of the cam and the detected object(in meters)
                threshold_algo_iteration: (obj:`int`, optional): Maximum iteration possible to find the good relative position
                alpha  (int): Iteration coeff decreasing increment of axis when we continue the iteration
            Returns:
                True if we reach object, otherwise False
        """
        self.set_arm_max_velocity(100)
        pos = self.position.to_list()
        x_ia/=1000
        y_ia/=1000
        z_ia/=1000
        print(f"[DO ROI LOOP] x_ia {round(x_ia,3)} y_ia {round(y_ia, 3)} z_niryo {pos[2]} y_niryo {pos[1]} x_niryo {pos[0]}")
        # if x or y ia are not as close as possible to the object coordinates 
        # -> we continue to reach target, otherwise we just grab the object (satisfying position)
        if  abs(x_ia) <= absolute_pos_error_x_ia and abs(y_ia) <= absolute_pos_error_y_ia or self._do_roi_counter > threshold_algo_iteration:
            print("Reach the object destination !")
            self._do_roi_counter=1
            return True
        else:
            print("Didn't reach object position !")
            # we change coordinates 
            y_real = x_ia/(alpha*self._do_roi_counter)
            x_real = -y_ia/(alpha*self._do_roi_counter)

            print(f"\n[NIRYO] X real {round(x_real, 3)}  Y real {round(y_real, 3)} and pos error x {absolute_pos_error_x_ia}m pos error y {absolute_pos_error_y_ia}m Counter {self._do_roi_counter}/{threshold_algo_iteration}")
            if abs(x_ia) <= absolute_pos_error_x_ia and abs(y_ia) > absolute_pos_error_y_ia:
                # dojust y
                print(f"[NIRYO] Finding good y .. incrementing {y_real}\n")
                self.increment_pos_y(y_real)
            elif abs(y_ia) <= absolute_pos_error_y_ia and abs(x_ia) > absolute_pos_error_x_ia:
                # do just x
                print(f"[NIRYO] Finding good x .. incrementing {x_real}\n")
                self.increment_pos_x(x_real)
            else:
                # do both
                print("[NIRYO] Moving both\n")
                self.increment_pos_x(x_real)
                self.increment_pos_y(y_real)
                
            self._do_roi_counter+=1
            return False
            
    def seq_grab_object(self, x_ia: float, y_ia:float, z_ia: float) -> None:
        """Second move to grab an object based on depthai OAK-D 2.5D camera

            We finaly dive in z axis of niryo without forgetting to remove camera x offset,
            z offset and the z of the conveyor

            Args:
                x_ia (float): x coordonates from the camera base (meters)
                y_ia (float): y coordonates from the camera base (meters)
                z_ia (float): z coordonates from the camera base (depth in meters)
         """
        x_ia/=1000
        y_ia/=1000
        z_ia/=1000
        pos = self.position.to_list()
        z_real = - (pos[2] - self.z_offset_vanilla - self.z_offset_conveyor)
        # We use the shift between niryo z pos and the ground (otherwise we hit the ground with the niryo)
        # normaly we just want to use z provided by car but z niryo is also consistent and the same
        # add the cam x offset 
        self.increment_pos_x(self.x_offset_cam+0.02)
        self.increment_pos_y(self.y_offset_cam)
        self.set_arm_max_velocity(100)
        print(f"[DO GRAB] offset_cam {self.x_offset_cam} z_real {round(z_real, 3)} z_ia {round(z_ia, 3)} x_i {round(x_ia,2)} y_ia {round(y_ia, 2)} z_niryo {pos[2]} y_niryo {pos[1]} x_niryo {pos[0]}")
        self.open_gripper(self.grip, 1000)
        # now we can turn the head (roll) to avoid colision with the conveyor equipment
        #pos = self.position.to_list()
        # x y z roll pitch yaw
        #pos[4] = 0.6
        #self.position = tuple(pos)
        """TODO plonger en z en fonction de la profondeur pas du offset conveyor"""

        self.increment_pos_z(z_real)
        self.close_gripper(self.grip, 200)
        self.set_arm_max_velocity(100)
        self.position = self.stand_by
        self.open_gripper(self.grip, 1000)
        time.sleep(0.5)
        self.close_gripper(self.grip, 1000)
        self.set_arm_max_velocity(50)