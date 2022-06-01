#from clients.python.niryo_one_tcp_client.enums import RobotAxis
from niryo_one_tcp_client import *

class Niryo:
    def __init__(self, ip: str="10.10.10.10", grip: RobotTool= RobotTool.GRIPPER_2, arm_velocity: int=30):
        self.n = NiryoOneClient()
        self.grip = grip
        print("[!] Connecting to {} ..".format(ip))
        self.n.connect(ip)
        print("[*] Done")
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

    @property
    def position(self):
        status, data = self.n.get_pose()
        if status is True:
            return data
        else:
            return "Error"
    
    @position.setter
    def position(self, value):
        x, y, z, roll, pitch, yaw = value
        status, data = self.n.move_pose(x, y, z, roll, pitch, yaw)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Moved successfully")
    """ TODO setter pitch, roll, yaw, x, y, z"""
    """
        @pitch.setter
        def pitch(self, value):
            self.n.
    """
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

    def increment_pos_x(self, value=0.10):
        status, data = self.n.shift_pose(RobotAxis.X, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_y(self, value=0.15):
        status, data = self.n.shift_pose(RobotAxis.Y, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    def increment_pos_z(self, value=0.1):
        status, data = self.n.shift_pose(RobotAxis.Z, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_pitch(self, value=0.2):
        status, data = self.n.shift_pose(RobotAxis.PITCH, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_roll(self, value=0.3):
        status, data = self.n.shift_pose(RobotAxis.ROLL, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_pos_yaw(self, value=0.3):
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

    def move_to_roi(self, x_,y_,z_, ratio=0.2):
        # move to region of interest ex : x = 22mm y = 33mm z = 650mm
        self.open_gripper()
        self.increment_pos_x(x_)
        self.increment_pos_y(y_)
        self.increment_pos_z(z_)

        

#n = Niryo()
#print(n.position)
# Pick
    
