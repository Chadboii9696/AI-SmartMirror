"""
Module for storing the currently recognized user.
This file serves as a global variable repository that other scripts can import.
"""
import os

# Path to the file storing the current user
USER_FILE = os.path.join(os.path.dirname(os.path.abspath(_file_)), "current_user.txt")
'''
Here, we define a constant USER_FILE that points to the file current_user.txt in the 
same directory as this script.
'''

# Initialize with default
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        f.write("unknown")

def update_user(name):
    """Update the current user name by writing to a file"""
    try:
        with open(USER_FILE, "w") as f:
            f.write(name)
    except Exception as e:
        print(f"Error updating current user: {e}")
    
def get_current_user():
    """Get the current user name from file"""
    try:
        with open(USER_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading current user: {e}")
        return "unknown"