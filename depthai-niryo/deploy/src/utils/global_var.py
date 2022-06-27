import os

# Global variables
def init_var():
    os.environ["MustStop"] = "False"
    global APP 
    global app_thread
    global NIRYO
    global API_PORT

    APP = None
    app_thread = None
    NIRYO = None
    API_PORT = 4000
