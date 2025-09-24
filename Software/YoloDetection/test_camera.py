#!/usr/bin/env python3
"""
Simple camera test script to verify USB camera functionality
"""

import cv2
from utils import get_available_cameras, test_camera


def main():
    print("USB Camera Test")
    print("=" * 40)
    
    # Find available cameras
    print("Scanning for available cameras...")
    cameras = get_available_cameras()
    
    if not cameras:
        print("❌ No cameras found!")
        print("\nTroubleshooting tips:")
        print("1. Make sure your USB camera is connected")
        print("2. Check if camera is being used by another application")
        print("3. Try different USB ports")
        print("4. On Linux, check camera permissions:")
        print("   sudo usermod -a -G video $USER")
        return
    
    print(f"✅ Found {len(cameras)} camera(s): {cameras}")
    
    # Test each camera
    for camera_id in cameras:
        print(f"\nTesting camera {camera_id}...")
        if test_camera(camera_id):
            print(f"✅ Camera {camera_id}: Working")
        else:
            print(f"❌ Camera {camera_id}: Failed")
    
    # Interactive camera test
    if cameras:
        default_camera = cameras[0]
        print(f"\nStarting live test with camera {default_camera}")
        print("Press 'q' to quit, 'c' to switch cameras")
        
        current_camera_idx = 0
        cap = cv2.VideoCapture(cameras[current_camera_idx])
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {cameras[current_camera_idx]}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Add camera info to frame
            camera_text = f"Camera {cameras[current_camera_idx]} - Press 'q' to quit, 'c' to switch"
            cv2.putText(frame, camera_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow("Camera Test", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c') and len(cameras) > 1:
                # Switch to next camera
                current_camera_idx = (current_camera_idx + 1) % len(cameras)
                cap.release()
                cap = cv2.VideoCapture(cameras[current_camera_idx])
                print(f"Switched to camera {cameras[current_camera_idx]}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("Camera test completed!")


if __name__ == "__main__":
    main()
