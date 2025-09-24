#!/usr/bin/env python3
"""
YOLO11 Object Detection with USB Camera
Real-time object detection using YOLO11 model and USB camera feed.
"""

import cv2
import numpy as np
from ultralytics import YOLO
import argparse
import time
from config import CAMERA_CONFIG


class YOLODetector:
    def __init__(self, model_path="yolo11n.pt", confidence=0.5, device="cpu"):
        """
        Initialize YOLO detector.
        
        Args:
            model_path (str): Path to YOLO model file
            confidence (float): Confidence threshold for detections
            device (str): Device to run inference on ('cpu' or 'cuda')
        """
        print(f"Loading YOLO11 model: {model_path}")
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.device = device
        
        # Set device
        if device == "cuda" and not cv2.cuda.getCudaEnabledDeviceCount():
            print("CUDA not available, falling back to CPU")
            self.device = "cpu"
    
    def detect_objects(self, frame):
        """
        Perform object detection on a frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            Annotated frame with detections
        """
        # Run inference
        results = self.model(frame, conf=self.confidence, device=self.device)
        
        # Draw results on frame
        annotated_frame = results[0].plot()
        
        return annotated_frame, results[0]


class CameraManager:
    def __init__(self, camera_id=0, width=640, height=480, reconnect_attempts=-1, 
                 reconnect_delay=2.0, connection_timeout=5.0, frame_timeout=1.0):
        """
        Initialize camera manager with USB reconnection support.
        
        Args:
            camera_id (int): Camera device ID
            width (int): Frame width
            height (int): Frame height
            reconnect_attempts (int): Max reconnection attempts (-1 = infinite)
            reconnect_delay (float): Delay between reconnection attempts
            connection_timeout (float): Timeout for initial connection
            frame_timeout (float): Timeout for frame reading
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.connection_timeout = connection_timeout
        self.frame_timeout = frame_timeout
        self.cap = None
        self.is_connected = False
        self.failed_frames = 0
        self.max_failed_frames = 5  # Reconnect after 5 failed frames
        self.last_reconnect_time = 0
        
    def _connect_camera(self):
        """Internal method to connect to camera."""
        try:
            if self.cap is not None:
                self.cap.release()
            
            print(f"Connecting to camera {self.camera_id}...")
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for real-time
            
            # Test if we can read a frame
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.cap.release()
                return False
            
            self.is_connected = True
            self.failed_frames = 0
            print(f"✅ Camera {self.camera_id} connected: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            print(f"❌ Camera connection error: {e}")
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            return False
    
    def start_camera(self):
        """Start camera capture with reconnection support."""
        attempt = 0
        
        while True:
            if self._connect_camera():
                return True
            
            attempt += 1
            
            # Check if we've exceeded max attempts
            if self.reconnect_attempts > 0 and attempt >= self.reconnect_attempts:
                raise RuntimeError(f"Failed to connect to camera {self.camera_id} after {attempt} attempts")
            
            print(f"🔄 Camera connection failed (attempt {attempt})")
            print(f"   Retrying in {self.reconnect_delay} seconds...")
            print("   Check USB connection and make sure camera isn't used by another app")
            
            time.sleep(self.reconnect_delay)
    
    def _reconnect_if_needed(self):
        """Check if reconnection is needed and attempt it."""
        current_time = time.time()
        
        # Avoid rapid reconnection attempts
        if current_time - self.last_reconnect_time < self.reconnect_delay:
            return False
        
        print(f"🔄 Camera disconnected, attempting to reconnect...")
        self.is_connected = False
        self.last_reconnect_time = current_time
        
        return self._connect_camera()
    
    def read_frame(self):
        """Read a frame from camera with automatic reconnection."""
        if not self.is_connected or self.cap is None:
            if not self._reconnect_if_needed():
                return None, "disconnected"
        
        try:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                self.failed_frames += 1
                print(f"⚠️  Frame read failed ({self.failed_frames}/{self.max_failed_frames})")
                
                if self.failed_frames >= self.max_failed_frames:
                    print(f"📱 Too many failed frames, marking camera as disconnected")
                    self.is_connected = False
                    return None, "connection_lost"
                
                return None, "frame_failed"
            
            # Success - reset failed frame counter
            self.failed_frames = 0
            return frame, "success"
            
        except Exception as e:
            print(f"❌ Camera read error: {e}")
            self.is_connected = False
            return None, "error"
    
    def is_camera_connected(self):
        """Check if camera is currently connected."""
        return self.is_connected and self.cap is not None and self.cap.isOpened()
    
    def get_status(self):
        """Get current camera status."""
        if self.is_connected:
            return "connected"
        else:
            return "disconnected"
    
    def release(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_connected = False
        print("📷 Camera released")


def main():
    parser = argparse.ArgumentParser(description="YOLO11 Object Detection with USB Camera")
    parser.add_argument("--model", default="yolo11n.pt", help="Path to YOLO model")
    parser.add_argument("--camera", type=int, default=0, help="Camera device ID")
    parser.add_argument("--confidence", type=float, default=0.5, help="Confidence threshold")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Device for inference")
    parser.add_argument("--width", type=int, default=640, help="Camera width")
    parser.add_argument("--height", type=int, default=480, help="Camera height")
    parser.add_argument("--no-display", action="store_true", help="Don't display video feed")
    parser.add_argument("--max-reconnect", type=int, default=-1, help="Max reconnection attempts (-1 = infinite)")
    parser.add_argument("--reconnect-delay", type=float, default=2.0, help="Delay between reconnection attempts")
    
    args = parser.parse_args()
    
    try:
        # Initialize detector
        detector = YOLODetector(
            model_path=args.model,
            confidence=args.confidence,
            device=args.device
        )
        
        # Initialize camera with reconnection support
        camera = CameraManager(
            camera_id=args.camera,
            width=args.width,
            height=args.height,
            reconnect_attempts=args.max_reconnect if args.max_reconnect != -1 else CAMERA_CONFIG.get("reconnect_attempts", -1),
            reconnect_delay=args.reconnect_delay if args.reconnect_delay != 2.0 else CAMERA_CONFIG.get("reconnect_delay", 2.0),
            connection_timeout=CAMERA_CONFIG.get("connection_timeout", 5.0),
            frame_timeout=CAMERA_CONFIG.get("frame_timeout", 1.0)
        )
        camera.start_camera()
        
        print("Starting object detection...")
        print("Press 'q' to quit, 's' to save current frame")
        print("Camera will automatically reconnect if USB connection is lost")
        
        frame_count = 0
        fps_counter = time.time()
        last_status_update = time.time()
        disconnected_start_time = None
        
        while True:
            # Read frame with status
            frame, status = camera.read_frame()
            
            # Handle different camera statuses
            if status == "disconnected":
                if disconnected_start_time is None:
                    disconnected_start_time = time.time()
                    print("📱 Camera disconnected - waiting for reconnection...")
                
                # Show waiting message periodically
                current_time = time.time()
                if current_time - last_status_update > 5.0:  # Every 5 seconds
                    elapsed = current_time - disconnected_start_time
                    print(f"⏱️  Still waiting for camera reconnection... ({elapsed:.0f}s)")
                    last_status_update = current_time
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                continue
                
            elif status == "connection_lost":
                print("📱 Camera connection lost - attempting automatic reconnection...")
                continue
                
            elif status == "frame_failed":
                continue  # Skip this frame but keep trying
                
            elif status == "error":
                print("❌ Camera error occurred - trying to recover...")
                time.sleep(1.0)
                continue
            
            # If we get here, we have a successful frame
            if disconnected_start_time is not None:
                reconnect_time = time.time() - disconnected_start_time
                print(f"✅ Camera reconnected after {reconnect_time:.1f} seconds!")
                disconnected_start_time = None
            
            if frame is None:
                continue
            
            # Perform detection
            annotated_frame, results = detector.detect_objects(frame)
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                current_time = time.time()
                fps = 30 / (current_time - fps_counter)
                fps_counter = current_time
                print(f"FPS: {fps:.1f}")
            
            # Display frame
            if not args.no_display:
                # Add FPS and camera status to frame
                cv2.putText(annotated_frame, f"FPS: {fps if 'fps' in locals() else 0:.1f}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Add camera status
                status_text = f"Camera: {camera.get_status()}"
                status_color = (0, 255, 0) if camera.is_camera_connected() else (0, 0, 255)
                cv2.putText(annotated_frame, status_text, 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                
                cv2.imshow("YOLO11 Object Detection", annotated_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    filename = f"detection_frame_{int(time.time())}.jpg"
                    cv2.imwrite(filename, annotated_frame)
                    print(f"Saved frame: {filename}")
            
            # Print detections
            if len(results.boxes) > 0:
                detections = []
                for box in results.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = detector.model.names[class_id]
                    detections.append(f"{class_name}: {confidence:.2f}")
                
                if frame_count % 30 == 0:  # Print every 30 frames
                    print(f"Detections: {', '.join(detections)}")
    
    except KeyboardInterrupt:
        print("\nStopping detection...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        camera.release()
        cv2.destroyAllWindows()
        print("Cleanup complete")


if __name__ == "__main__":
    main()
