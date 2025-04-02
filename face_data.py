import cv2
import os
import time
import json
import subprocess
import sys
from picamera2 import Picamera2

# Function to get the most recently added person's name from people.json
def get_latest_name():
    try:
        # Read the people.json file
        with open(os.path.join(os.path.dirname(__file__), 'people.json'), 'r') as f:
            people_data = json.load(f)
        
        if not people_data:
            print("No user data found in people.json")
            return None
        
        # Get the name of the most recently added person (last in the list)
        latest_person = people_data[-1]
        name = latest_person.get("name")
        
        if not name:
            print("No name found in the latest user data")
            return None
            
        return name
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading people.json: {e}")
        return None

# Get the name from the most recently added user
name = get_latest_name()

# Exit if no valid name was found
if not name:
    print("Could not get a valid name from people.json. Exiting.")
    exit(1)

print(f"Starting face data collection for user: {name}")

# Create the directory if it doesn't exist
output_dir = f"dataset/{name}/"
os.makedirs(output_dir, exist_ok=True)

# Initialize the Raspberry Pi camera using Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Add a slightly longer warmup time for Raspberry Pi stability
time.sleep(2.0)  # Give camera time to stabilize

# Window setup for Raspberry Pi OS
cv2.namedWindow("Automatic photo capture (press ESC to exit)", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Automatic photo capture (press ESC to exit)", 500, 300)

# Position the window for Raspberry Pi desktop environment
# Adjust these values based on your screen resolution
cv2.moveWindow("Automatic photo capture (press ESC to exit)", 50, 50)

# Check available memory before starting capture
try:
    # Simple check for available memory on Raspberry Pi
    with open('/proc/meminfo', 'r') as f:
        meminfo = f.read()
    
    free_mem = 0
    for line in meminfo.split('\n'):
        if 'MemAvailable' in line:
            free_mem = int(line.split()[1])
            break
    
    # Convert to MB for easier reading
    free_mem_mb = free_mem / 1024
    print(f"Available memory: {free_mem_mb:.1f} MB")
    
    # Warn if memory is low
    if free_mem_mb < 200:  # Less than 200MB available
        print("WARNING: Low memory may affect performance")
except:
    # Skip if not on Linux
    pass

# Parameters for automatic capture
img_counter = 0
total_images = 250  # Set how many images you want to capture
capture_delay = 0.4  # Time between captures in seconds

print(f"Will automatically capture {total_images} images with {capture_delay} second delay between them.")
print("Press ESC at any time to stop the capture process.")

# Countdown before starting
for i in range(3, 0, -1):
    print(f"Starting in {i} seconds...")
    time.sleep(1)

start_time = time.time()

while img_counter < total_images:
    # Capture frame from the Raspberry Pi camera
    frame = picam2.capture_array()
    
    # Display the frame
    cv2.imshow("Automatic photo capture (press ESC to exit)", frame)
    
    # Check for ESC key to exit early
    k = cv2.waitKey(1)
    if k % 256 == 27:  # ESC pressed
        print("Escape hit, closing...")
        break
    
    # Capture an image automatically after delay
    current_time = time.time()
    if current_time - start_time >= capture_delay:
        img_name = f"{output_dir}/image_{img_counter}.jpg"
        cv2.imwrite(img_name, frame)
        print(f"{img_name} written! ({img_counter+1}/{total_images})")
        img_counter += 1
        start_time = current_time  # Reset the timer
    
    # Small sleep to reduce CPU usage
    time.sleep(0.01)

# Release resources explicitly
try:
    cv2.destroyAllWindows()
    picam2.stop()
    print("Camera resources released")
except Exception as e:
    print(f"Error releasing camera resources: {e}")

print(f"Captured {img_counter} images for the dataset.")

if img_counter == total_images:
    print(f"Face data collection completed for {name}.")
    print("Running face encoding process...")
    
    # Run face_encoding.py
    try:
        # For Raspberry Pi OS compatibility
        pythonpath = "python3"  # Raspberry Pi OS uses python3 command
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "face_encoding.py")
        
        subprocess.run([pythonpath, script_path])
        print("Face encoding completed successfully.")
    except Exception as e:
        print(f"Error running face_encoding.py: {e}")
else:
    print(f"Face data collection interrupted after {img_counter} images.")
    print("Face encoding will not run as collection was incomplete.")
