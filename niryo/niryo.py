#from clients.python.niryo_one_tcp_client.enums import RobotAxis
from niryo_one_tcp_client import *

class Niryo:
    def __init__(self, ip: str="10.10.10.10", grip: RobotTool= RobotTool.GRIPPER_2):
        self.n = NiryoOneClient()
        self.grip = grip
        print("[!] Connecting to {}".format(ip))
        self.n.connect(ip)  # =< Replace by robot ip address
        print("[*] Done, starting auto calibration ..")
        status, data = self.n.calibrate(CalibrateMode.AUTO)
        if status:
            print("[*] Calibration done")
        else:
            print("[*] Impossible to calibrate")

        status, data = self.n.get_pose()
        if status is True:
            self.initial_pose = data
        else:
            print("Error: " + data)
            self.pose = None

    @property
    def position(self):
        status, data = self.n.get_pose()
        if status is True:
            return data
        else:
            return "Error"
    
    @position.setter
    def position(self, x, y, z, roll, pitch, yaw):
        status, data = self.n.move_joints(x, y, z, roll, pitch, yaw)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Moved successfully")

    def increment_axis_x(self, value=0.10):
        status, data = self.n.shift_pose(RobotAxis.X, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_axis_y(self, value=0.15):
        status, data = self.n.shift_pose(RobotAxis.Y, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    def increment_axis_z(self, value=0.1):
        status, data = self.n.shift_pose(RobotAxis.Z, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_axis_pitch(self, value=0.2):
        status, data = self.n.shift_pose(RobotAxis.PITCH, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_axis_roll(self, value=0.3):
        status, data = self.n.shift_pose(RobotAxis.ROLL, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")

    def increment_axis_yaw(self, value=0.3):
        status, data = self.n.shift_pose(RobotAxis.YAW, value)
        if status is False:
            print("Error: " + data)
        else:
            print("[*] Shifted correctly")
    
    # Going back to initial pose
    def go_initial_pose(self):
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

    def place_object(self, x=0.25, y=0.0, z=0.14, roll=0.0, pitch=1.57, yaw=0.0):
        place_pose = PoseObject(
            x=x, y=y, z=z,
            roll=-roll, pitch=pitch, yaw=yaw,
        )
        self.n.place_from_pose(*place_pose.to_list())

    def open_grippper(self, grip_speed=400):
        self.n.open_gripper(self.grip, grip_speed)

    def close_grippper(self, grip_speed=400):
        self.n.close_gripper(self.grip, grip_speed)


#n = Niryo()
#print(n.position)
# Pick
    
