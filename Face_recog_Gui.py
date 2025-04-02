from picamera2 import Picamera2
import face_recognition
import pickle
import cv2
import time
import numpy as np
from ultralytics import YOLO
import os
import current_user

# Configuration parameters - easier to adjust
CONFIG = {
    "recognition_threshold": 0.55,  # Face recognition confidence threshold
    "detection_confidence": 0.5,    # YOLO detection confidence threshold
    "face_model_path": "/home/tusharg/yolov8n-face.pt",
    "encodings_file": "encodings.pickle",
    "camera_resolution": (640, 480),
    "display_confidence": True,     # Show confidence scores on screen
    "enable_logging": True,         # Log recognitions to file
    "log_file": "face_recognition_log.txt",
    "fps_update_interval": 10       # Update FPS counter every N frames
}

class FaceRecognitionSystem:
    def __init__(self, config):
        self.config = config
        self.currentname = "unknown"
        self.frame_count = 0
        self.start_time = time.time()
        
        # Initialize logging
        if self.config["enable_logging"]:
            self.setup_logging()
        
        # Load face encodings
        self.load_encodings()
        
        # Load YOLOv8 model
        self.load_model()
        
        # Initialize camera
        self.setup_camera()
    
    def setup_logging(self):
        """Setup logging to file with timestamps"""
        self.log(f"===== Face Recognition Session Started at {time.strftime('%Y-%m-%d %H:%M:%S')} =====")
    
    def log(self, message):
        """Log message to console and file"""
        print(message)
        if self.config["enable_logging"]:
            with open(self.config["log_file"], "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    
    def load_encodings(self):
        """Load known face encodings from pickle file"""
        self.log("[INFO] Loading encodings...")
        
        try:
            with open(self.config["encodings_file"], "rb") as f:
                self.data = pickle.load(f)
            
            # Verify encodings data
            unique_names = set(self.data["names"])
            self.log(f"[INFO] Loaded {len(self.data['encodings'])} encodings for {len(unique_names)} unique persons")
            self.log(f"[INFO] People in dataset: {', '.join(unique_names)}")
        except Exception as e:
            self.log(f"[ERROR] Failed to load encodings: {e}")
            exit(1)
    
    def load_model(self):
        """Load YOLO model for face detection"""
        try:
            self.log("[INFO] Loading YOLO face detection model...")
            self.model = YOLO(self.config["face_model_path"])
        except Exception as e:
            self.log(f"[ERROR] Failed to load YOLO model: {e}")
            exit(1)
    
    def setup_camera(self):
        """Initialize and configure the Raspberry Pi camera"""
        try:
            self.log("[INFO] Initializing camera...")
            self.picam2 = Picamera2()
            self.picam2.configure(self.picam2.create_preview_configuration(
                main={"format": 'XRGB8888', "size": self.config["camera_resolution"]}
            ))
            self.picam2.start()
            self.log("[INFO] Warming up camera...")
            time.sleep(2.0)
        except Exception as e:
            self.log(f"[ERROR] Camera initialization failed: {e}")
            exit(1)
    
    def process_frame(self, frame):
        """Process a single frame for face detection and recognition"""
        # Convert frame to RGB for processing
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        display_frame = frame_rgb.copy()
        
        # Detect faces using YOLO
        results = self.model(frame_rgb)
        boxes = results[0].boxes
        
        recognized_faces = []
        
        # Process each detected face
        for box in boxes:
            # Extract coordinates
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            
            if conf > self.config["detection_confidence"]:
                # Convert to integers for drawing
                left, top, right, bottom = int(x1), int(y1), int(x2), int(y2)
                
                # Format for face_recognition
                face_locations = [(top, right, bottom, left)]
                
                try:
                    # Get face encodings
                    encodings = face_recognition.face_encodings(frame_rgb, face_locations)
                    
                    name = "Unknown"
                    confidence = 0.0
                    
                    if len(encodings) > 0:
                        encoding = encodings[0]
                        
                        # Calculate face distances and find matches
                        face_distances = face_recognition.face_distance(self.data["encodings"], encoding)
                        
                        if len(face_distances) > 0:
                            # Find best match
                            best_match_index = np.argmin(face_distances)
                            best_match_distance = face_distances[best_match_index]
                            matches = face_recognition.compare_faces(self.data["encodings"], encoding)
                            
                            # Check if match is good enough
                            if matches[best_match_index] and best_match_distance < self.config["recognition_threshold"]:
                                name = self.data["names"][best_match_index]
                                confidence = 1 - best_match_distance
                                
                                # Log new person detections
                                if self.currentname != name:
                                    self.currentname = name
                                    self.log(f"[DETECTED] {name} with confidence: {confidence:.2f}")
                                    current_user.update_user(name)
                                    
                                    # Launch display_info.py when a face is recognized
                                    try:
                                        import subprocess
                                        import sys
                                        import os

                                        # Check if display_info.py is already running
                                        display_info_running = False
                                        if os.name == 'posix':  # Linux/Raspberry Pi OS
                                            try:
                                                check_process = subprocess.run(
                                                    ["pgrep", "-f", "python.*display_info.py"], 
                                                    capture_output=True, 
                                                    text=True,
                                                    shell=True  # Use shell on Raspberry Pi for better pattern matching
                                                )
                                                display_info_running = check_process.returncode == 0
                                            except Exception as e:
                                                self.log(f"[WARNING] Process check error: {e}")
                                        else:  # Windows
                                            try:
                                                check_process = subprocess.run(
                                                    ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"], 
                                                    capture_output=True, 
                                                    text=True
                                                )
                                                display_info_running = "display_info.py" in check_process.stdout
                                            except:
                                                pass
                                        
                                        # Only launch if not already running
                                        if not display_info_running:
                                            # Get absolute path to script directory
                                            script_dir = os.path.dirname(os.path.abspath(__file__))
                                            script_path = os.path.join(script_dir, "display_info.py")
                                            
                                            # On Raspberry Pi, use python3 explicitly
                                            if os.name == 'posix':
                                                self.log("[INFO] Starting display_info.py with python3...")
                                                subprocess.Popen(["python3", script_path])
                                            else:
                                                # On Windows, use sys.executable
                                                self.log("[INFO] Starting display_info.py...")
                                                subprocess.Popen([sys.executable, script_path])
                                            
                                            # Stop running this script after launching display_info.py
                                            self.log("[INFO] Exiting smoothrecog.py after launching display_info.py")
                                            exit()
                                    except Exception as e:
                                        self.log(f"[ERROR] Failed to launch display_info.py: {e}")
                    
                    # Store recognition results for display
                    recognized_faces.append({
                        "name": name,
                        "confidence": confidence,
                        "box": (left, top, right, bottom)
                    })
                    
                except Exception as e:
                    self.log(f"[ERROR] Face recognition error: {e}")
        
        # Draw results on frame
        for face in recognized_faces:
            left, top, right, bottom = face["box"]
            
            # Draw rectangle
            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Prepare display text
            if self.config["display_confidence"] and face["name"] != "Unknown":
                display_text = f"{face['name']} ({face['confidence']:.2f})"
            else:
                display_text = face["name"]
            
            # Draw name
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(display_frame, display_text, (left, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Calculate and display FPS
        self.frame_count += 1
        if self.frame_count % self.config["fps_update_interval"] == 0:
            elapsed_time = time.time() - self.start_time
            fps = self.frame_count / elapsed_time
            fps_text = f"FPS: {fps:.2f}"
            cv2.putText(display_frame, fps_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return display_frame, recognized_faces
    
    def run(self):
        """Run the face recognition loop"""
        self.log("[INFO] Starting face recognition...")
        
        # Create window with normal flags for resizing
        cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
        
        # Set window properties to make it minimized/smaller
        cv2.resizeWindow("Face Recognition", 320, 240)  # Small window size
        
        # Move window to the corner (this positioning varies by OS)
        cv2.moveWindow("Face Recognition", 50, 50)
        
        try:
            while True:
                # Capture frame
                frame = self.picam2.capture_array()
                
                # Process the frame
                display_frame, faces = self.process_frame(frame)
                
                # Display the frame
                cv2.imshow("Face Recognition", display_frame)
                
                # Check for exit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                
        except KeyboardInterrupt:
            self.log("[INFO] Interrupted by user")
        except Exception as e:
            self.log(f"[ERROR] Runtime error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        cv2.destroyAllWindows()
        self.picam2.stop()
        self.log("[INFO] Face recognition system stopped")
        if self.config["enable_logging"]:
            self.log(f"===== Session Ended at {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n")

# Run the application
if __name__ == "__main__":
    system = FaceRecognitionSystem(CONFIG)
    system.run()
