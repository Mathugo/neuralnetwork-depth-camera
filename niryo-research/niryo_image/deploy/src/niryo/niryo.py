#from clients.python.niryo_one_tcp_client.enums import RobotAxis
#from niryo_one_python_api.niryo_one_api import *
import math, string, sys
sys.path.append("/app/build/python_tcp_client")
from niryo_one_tcp_client import *

class Niryo:
    def __init__(self, ip: string="localhost", grip: RobotTool= RobotTool.GRIPPER_2, arm_velocity: int=30, z_offset_conveyor: float=0, z_offset_object:float=0.105):
        self.n = NiryoOneClient()
        self.grip = grip
        self.n.connect(ip)
        print("[*] Calibrating the robot ..")
        status, data = self.n.calibrate(CalibrateMode.AUTO)
        if status:
            print("[*] Calibration done")
        else:
            print("[*] Impossible to calibrate")
        self.set_arm_max_velocity(arm_velocity)
        self.change_tool(self.grip)
        status, data = self.n.get_pose()
        if status is True:
            self.initial_pose = data
        else:
            print("Error: " + data)
            self.pose = None
        self.stand_by = (0.11, 0.0, 0.4, 0., 1., 0.0)
        self.grab_mode = (0.11, 0.0, 0.4, 0., 1.35, 0.0)
        self.position = self.stand_by
        self.z_offset_conveyor = z_offset_conveyor
        self.z_offset_object = z_offset_object

    @property
    def position(self):
        status, data = self.n.get_pose()
        if status is True:
            return data
        else:
            return "Error"
    
    @position.setter
    def position(self, value):
        self.x, self.y, self.z, self.roll, self.pitch, self.yaw = value
        status, data = self.n.move_pose(self.x, self.y, self.z, self.roll, self.pitch, self.yaw)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Moved successfully")

    def calibration(self) -> None:
        if self.n.need_calibration():
            print("[!] Starting calibration ..")
            status, data = self.n.calibrate(CalibrateMode.AUTO)
            if status:
                print("[*] Calibration done")
            else:
                print("[*] Impossible to calibrate")
        else:
            print("[*] No need to calibrate")
    
    def quit(self) -> None:
        self.n.quit()

    def set_arm_max_velocity(self, percentage: int) -> None:
        print("[!] Setting {}% arm velocity".format(percentage))
        if percentage > 100 or percentage < 0:
            raise ValueError("Wrong percentage for velocity")  
        else:
            self.n.set_arm_max_velocity(percentage)
            print("[*]  Done")

    def change_tool(self, tool: RobotTool) -> None:
        print("[*] Changing tool ..")
        self.n.change_tool(tool)
        print("[*] Done")

    def increment_pos_x(self, value: float=0.10):
        status, data = self.n.shift_pose(RobotAxis.X, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_y(self, value: float=0.15):
        status, data = self.n.shift_pose(RobotAxis.Y, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    def increment_pos_z(self, value: float=0.1):
        status, data = self.n.shift_pose(RobotAxis.Z, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_pitch(self, value: float=0.2):
        status, data = self.n.shift_pose(RobotAxis.PITCH, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_roll(self, value: float=0.3):
        status, data = self.n.shift_pose(RobotAxis.ROLL, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_yaw(self, value: float=0.3):
        status, data = self.n.shift_pose(RobotAxis.YAW, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    # Going back to initial pose
    def go_to_initial_pose(self):
        if self.initial_pose is not None:
            status, data = self.n.move_pose(*self.n.pose_to_list(self.initial_pose))
            if status is False:
                print("Error: " + data)
            else:
                print("[*] Moved successfully to initial pose")

    def pick_object(self, x=0.25, y=0.0, z=0.14, roll=0.0, pitch=1.57, yaw=0.0):
        pick_pose = PoseObject(
            x=x, y=y, z=z,
            roll=-roll, pitch=pitch, yaw=yaw,
        )
        self.n.pick_from_pose(*pick_pose.to_list())

    def place_object(self, x=-0.01, y=0.23, z=0.12, roll=-0., pitch=1.57, yaw=-1.57):
        place_pose = PoseObject(
            x=x, y=y, z=z,
            roll=-roll, pitch=pitch, yaw=yaw,
        )
        self.n.place_from_pose(*place_pose.to_list())

    def open_gripper(self, grip_speed=400):
        self.n.open_gripper(self.grip, grip_speed)

    def close_gripper(self, grip_speed=400):
        self.n.close_gripper(self.grip, grip_speed)

    def calc_target(self, x_ia: float, y_ia: float, z_ia: float):
        """  calc the coordinates with taking into acount the offset between the end effector and the cam """
        x_roi = math.sqrt(z_ia**2 - (self.z - self.z_offset_conveyor)**2)
        y_roi = x_ia
        z_roi = self.z - self.z_offset_conveyor - self.z_offset_object
        return x_roi, y_roi, -z_roi

    def move_to_roi(self, x_ia: int,y_ia: int,z_ia: int, ratio: float=0.2, z_offset_conveyor: float=None):
        """ move to roi based on depthai OAK-D 2.5D camera"""
        if z_offset_conveyor != None:
            self.z_offset_conveyor = z_offset_conveyor
        x_, y_, z_ = self.calc_target(x_ia, y_ia, z_ia)
        print("[*] Estimated position ({},{},{}) m \nwith z_offset_conveyor {}, and z_offset_object {}".format(x_, y_, z_, self.z_offset_conveyor, self.z_offset_object))
        self.last_grab = (x_, y_, z_)
        # move to region of interest ex : x = 0.022m y = 0.033m z = 0.650m
        self.open_gripper()
        self.increment_pos_x(x_)
        self.increment_pos_y(y_)
        self.increment_pos_z(z_)
        self.close_gripper()
        self.position = self.stand_by
    
        
#467 -25 3
#n = Niryo()
#print(n.position)
# Pick
    
