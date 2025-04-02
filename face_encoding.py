import face_recognition
import pickle
import cv2
import os
import time

# Check for Raspberry Pi resource limitations
try:
    # Check available memory on Raspberry Pi
    with open('/proc/meminfo', 'r') as f:
        meminfo = f.read()
    
    free_mem = 0
    for line in meminfo.split('\n'):
        if 'MemAvailable' in line:
            free_mem = int(line.split()[1])
            break
    
    # Convert to MB for easier reading
    free_mem_mb = free_mem / 1024
    print(f"[INFO] Available memory: {free_mem_mb:.1f} MB")
    
    # Warn if memory is low
    if free_mem_mb < 200:  # Less than 200MB available
        print("[WARNING] Low memory may affect performance or cause failures")
except Exception:
    # Skip if not on Linux or can't read memory info
    pass

# Use absolute paths for better compatibility on Raspberry Pi
current_dir = os.path.dirname(os.path.abspath(__file__))

# Paths
dataset_path = os.path.join(current_dir, "dataset")  # Your dataset directory
encodings_output = os.path.join(current_dir, "encodings.pickle")  # Output file

# Initialize lists
known_encodings = []
known_names = []

print("[INFO] Processing dataset...")

# Count total images for progress tracking (helpful on slower Raspberry Pi)
total_images = 0
total_people = 0
for person_name in os.listdir(dataset_path):
    person_dir = os.path.join(dataset_path, person_name)
    if os.path.isdir(person_dir):
        total_people += 1
        for img_file in os.listdir(person_dir):
            if img_file.endswith(".jpg") or img_file.endswith(".png"):
                total_images += 1

print(f"[INFO] Found {total_images} images across {total_people} people")
processed_images = 0

# Start timing for performance monitoring
start_time = time.time()

# Loop over all person folders in the dataset
for person_name in os.listdir(dataset_path):
    person_dir = os.path.join(dataset_path, person_name)
    
    # Skip if not a directory
    if not os.path.isdir(person_dir):
        continue
        
    print(f"[INFO] Processing images for: {person_name}")
    
    # Loop over all images for this person
    person_images = [f for f in os.listdir(person_dir) if f.endswith(".jpg") or f.endswith(".png")]
    
    for img_file in person_images:
        img_path = os.path.join(person_dir, img_file)
        processed_images += 1
        
        # Show progress
        progress = (processed_images / total_images) * 100
        print(f"  Processing {img_path} ({processed_images}/{total_images}, {progress:.1f}%)")
        
        try:
            # Load image and convert to RGB
            image = cv2.imread(img_path)
            
            if image is None:
                print(f"  [WARNING] Could not load {img_path}, skipping")
                continue
                
            # Resize image for faster processing on Raspberry Pi
            # Scale factor can be adjusted based on your Pi's performance
            scale_factor = 0.5  # Reduce size to 50%
            if image.shape[0] > 800 or image.shape[1] > 800:
                width = int(image.shape[1] * scale_factor)
                height = int(image.shape[0] * scale_factor)
                image = cv2.resize(image, (width, height))
                print(f"  [INFO] Resized large image to {width}x{height} for better performance")
            
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces in the image
            boxes = face_recognition.face_locations(rgb, model="hog")
            
            if len(boxes) == 0:
                print(f"  [WARNING] No faces detected in {img_path}")
                continue
            
            # Compute facial embeddings for each face
            encodings = face_recognition.face_encodings(rgb, boxes)
            
            # Add each encoding to our lists
            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(person_name)
                
            # Occasionally force garbage collection to reduce memory usage
            if processed_images % 50 == 0:
                import gc
                gc.collect()
                
        except Exception as e:
            print(f"  [ERROR] Error processing {img_path}: {e}")
            continue
        
        # Check for memory pressure on Raspberry Pi
        if processed_images % 25 == 0:
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                for line in meminfo.split('\n'):
                    if 'MemAvailable' in line:
                        free_mem_mb = int(line.split()[1]) / 1024
                        if free_mem_mb < 100:  # Critical memory level
                            print(f"[WARNING] Low memory detected: {free_mem_mb:.1f} MB. Consider restarting.")
                        break
            except:
                pass

# Save the facial encodings + names to disk
print("[INFO] Serializing encodings...")
data = {"encodings": known_encodings, "names": known_names}

try:
    with open(encodings_output, "wb") as f:
        f.write(pickle.dumps(data))
    print(f"[INFO] Encodings saved to {encodings_output}")
except Exception as e:
    print(f"[ERROR] Failed to save encodings: {e}")
    # Try saving to home directory as fallback on Raspberry Pi
    fallback_path = os.path.join(os.path.expanduser("~"), "encodings.pickle")
    try:
        with open(fallback_path, "wb") as f:
            f.write(pickle.dumps(data))
        print(f"[INFO] Encodings saved to fallback location: {fallback_path}")
    except:
        print("[ERROR] Could not save encodings to any location")

# Report statistics
end_time = time.time()
total_time = end_time - start_time
print(f"[INFO] Processed {len(known_names)} face images across {len(set(known_names))} people")
print(f"[INFO] Processing completed in {total_time:.2f} seconds")
