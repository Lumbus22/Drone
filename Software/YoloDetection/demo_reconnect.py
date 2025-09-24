#!/usr/bin/env python3
"""
Demo script to test USB camera reconnection behavior
This script helps you test the reconnection functionality by simulating camera disconnections
"""

import cv2
import time
from main import CameraManager
from config import CAMERA_CONFIG


def demo_reconnection():
    """Demonstrate camera reconnection behavior."""
    print("USB Camera Reconnection Demo")
    print("=" * 40)
    print("This demo will help you test the reconnection behavior.")
    print("Instructions:")
    print("1. Make sure your USB camera is connected")
    print("2. The demo will start showing the camera feed")
    print("3. Try unplugging and reconnecting the USB cable")
    print("4. Watch how the program handles disconnections")
    print("5. Press 'q' to quit\n")
    
    input("Press Enter to start the demo...")
    
    # Initialize camera with aggressive reconnection settings for demo
    camera = CameraManager(
        camera_id=0,
        width=640,
        height=480,
        reconnect_attempts=-1,  # Infinite attempts
        reconnect_delay=1.0,    # Fast reconnection for demo
        connection_timeout=3.0,
        frame_timeout=0.5
    )
    
    print("Starting camera...")
    try:
        camera.start_camera()
    except Exception as e:
        print(f"Failed to start camera: {e}")
        print("Make sure your camera is connected and not used by another app")
        return
    
    print("✅ Camera started successfully!")
    print("\nDemo running - try disconnecting and reconnecting your USB camera...")
    print("Watch the console messages to see the reconnection process")
    
    frame_count = 0
    last_connected_time = time.time()
    total_disconnected_time = 0
    disconnection_count = 0
    
    while True:
        frame, status = camera.read_frame()
        
        if status == "success" and frame is not None:
            # Camera is working
            current_time = time.time()
            
            # Add demo info to frame
            cv2.putText(frame, "USB Reconnection Demo", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Status: {camera.get_status()}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Disconnections: {disconnection_count}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Try unplugging USB cable!", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 190), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("USB Reconnection Demo", frame)
            
            # Reset disconnection tracking
            if 'disconnected_start' in locals():
                disconnect_duration = current_time - disconnected_start
                total_disconnected_time += disconnect_duration
                print(f"📊 Disconnection #{disconnection_count} lasted {disconnect_duration:.1f} seconds")
                del disconnected_start
            
            last_connected_time = current_time
            frame_count += 1
            
        elif status in ["disconnected", "connection_lost"]:
            # Camera is disconnected
            if 'disconnected_start' not in locals():
                disconnected_start = time.time()
                disconnection_count += 1
                print(f"\n🔌 Disconnection #{disconnection_count} detected!")
                print("   The program will keep trying to reconnect...")
            
            # Show a black frame with status
            black_frame = cv2.imread("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", cv2.IMREAD_COLOR)
            if black_frame is None:
                black_frame = cv2.zeros((480, 640, 3), dtype=cv2.uint8)
            
            cv2.putText(black_frame, "Camera Disconnected", (150, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            cv2.putText(black_frame, "Waiting for reconnection...", (160, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(black_frame, f"Disconnection #{disconnection_count}", (200, 300), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            cv2.imshow("USB Reconnection Demo", black_frame)
        
        # Handle key presses
        key = cv2.waitKey(100) & 0xFF  # Longer wait when disconnected
        if key == ord('q'):
            break
    
    # Cleanup and show statistics
    camera.release()
    cv2.destroyAllWindows()
    
    print(f"\n📊 Demo Statistics:")
    print(f"   Total disconnections: {disconnection_count}")
    print(f"   Total disconnected time: {total_disconnected_time:.1f} seconds")
    print(f"   Average disconnection duration: {total_disconnected_time/max(disconnection_count,1):.1f} seconds")
    print(f"   Total frames processed: {frame_count}")
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    try:
        demo_reconnection()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        cv2.destroyAllWindows()
