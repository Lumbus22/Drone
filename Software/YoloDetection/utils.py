"""
Utility functions for YOLO11 Object Detection
"""

import cv2
import numpy as np
import time
from typing import List, Tuple, Optional
from config import CLASS_COLORS, DISPLAY_CONFIG


def get_available_cameras(max_cameras: int = 10) -> List[int]:
    """
    Find all available camera devices.
    
    Args:
        max_cameras (int): Maximum number of cameras to check
        
    Returns:
        List of available camera indices
    """
    available_cameras = []
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()
    
    return available_cameras


def test_camera(camera_id: int = 0) -> bool:
    """
    Test if a camera is working properly.
    
    Args:
        camera_id (int): Camera device ID
        
    Returns:
        True if camera is working, False otherwise
    """
    try:
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        return ret and frame is not None
    except Exception:
        return False


def draw_fps(frame: np.ndarray, fps: float, position: Tuple[int, int] = (10, 30)) -> np.ndarray:
    """
    Draw FPS counter on frame.
    
    Args:
        frame: Input frame
        fps: Current FPS value
        position: Text position (x, y)
        
    Returns:
        Frame with FPS text
    """
    text = f"FPS: {fps:.1f}"
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                DISPLAY_CONFIG["font_scale"], (0, 255, 0), DISPLAY_CONFIG["font_thickness"])
    return frame


def draw_detection_info(frame: np.ndarray, detections: List[dict], 
                       position: Tuple[int, int] = (10, 60)) -> np.ndarray:
    """
    Draw detection information on frame.
    
    Args:
        frame: Input frame
        detections: List of detection dictionaries
        position: Starting text position (x, y)
        
    Returns:
        Frame with detection info
    """
    y_offset = position[1]
    
    for i, detection in enumerate(detections):
        if i >= 5:  # Limit to 5 detections to avoid cluttering
            break
            
        text = f"{detection['class']}: {detection['confidence']:.2f}"
        cv2.putText(frame, text, (position[0], y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                   DISPLAY_CONFIG["font_scale"] * 0.8, (255, 255, 255), 
                   DISPLAY_CONFIG["font_thickness"])
        y_offset += 25
    
    return frame


def draw_custom_boxes(frame: np.ndarray, boxes: np.ndarray, class_ids: np.ndarray,
                     confidences: np.ndarray, class_names: List[str]) -> np.ndarray:
    """
    Draw custom bounding boxes with enhanced visualization.
    
    Args:
        frame: Input frame
        boxes: Bounding boxes array
        class_ids: Class IDs array
        confidences: Confidence scores array
        class_names: List of class names
        
    Returns:
        Frame with custom boxes
    """
    height, width = frame.shape[:2]
    
    for i, box in enumerate(boxes):
        # Get box coordinates
        x1, y1, x2, y2 = box.astype(int)
        
        # Get class info
        class_id = int(class_ids[i])
        confidence = float(confidences[i])
        class_name = class_names[class_id] if class_id < len(class_names) else "Unknown"
        
        # Get color for this class
        color = CLASS_COLORS[class_id % len(CLASS_COLORS)]
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, DISPLAY_CONFIG["bbox_thickness"])
        
        # Prepare label text
        if DISPLAY_CONFIG["show_confidence"]:
            label = f"{class_name}: {confidence:.2f}"
        else:
            label = class_name
        
        # Calculate label size
        (label_width, label_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["font_scale"], 
            DISPLAY_CONFIG["font_thickness"]
        )
        
        # Draw label background
        label_y = max(y1, label_height + 10)
        cv2.rectangle(frame, (x1, label_y - label_height - 10), 
                     (x1 + label_width, label_y + baseline - 10), color, -1)
        
        # Draw label text
        if DISPLAY_CONFIG["show_labels"]:
            cv2.putText(frame, label, (x1, label_y - 7), cv2.FONT_HERSHEY_SIMPLEX,
                       DISPLAY_CONFIG["font_scale"], (255, 255, 255), 
                       DISPLAY_CONFIG["font_thickness"])
    
    return frame


class FPSCalculator:
    """Simple FPS calculator."""
    
    def __init__(self, buffer_size: int = 30):
        self.buffer_size = buffer_size
        self.frame_times = []
        self.start_time = time.time()
    
    def update(self) -> float:
        """Update FPS calculation and return current FPS."""
        current_time = time.time()
        self.frame_times.append(current_time)
        
        # Keep only recent frames
        if len(self.frame_times) > self.buffer_size:
            self.frame_times.pop(0)
        
        # Calculate FPS
        if len(self.frame_times) < 2:
            return 0.0
        
        time_diff = self.frame_times[-1] - self.frame_times[0]
        if time_diff == 0:
            return 0.0
        
        return (len(self.frame_times) - 1) / time_diff


def save_detection_results(detections: List[dict], filename: str = None) -> str:
    """
    Save detection results to a text file.
    
    Args:
        detections: List of detection dictionaries
        filename: Output filename (optional)
        
    Returns:
        Path to saved file
    """
    if filename is None:
        filename = f"detections_{int(time.time())}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Detection Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        
        for i, detection in enumerate(detections):
            f.write(f"Detection {i+1}:\n")
            f.write(f"  Class: {detection['class']}\n")
            f.write(f"  Confidence: {detection['confidence']:.3f}\n")
            f.write(f"  Bounding Box: {detection['bbox']}\n")
            f.write("\n")
    
    return filename


def resize_frame(frame: np.ndarray, max_width: int = 1280, max_height: int = 720) -> np.ndarray:
    """
    Resize frame while maintaining aspect ratio.
    
    Args:
        frame: Input frame
        max_width: Maximum width
        max_height: Maximum height
        
    Returns:
        Resized frame
    """
    height, width = frame.shape[:2]
    
    # Calculate scaling factor
    scale_w = max_width / width
    scale_h = max_height / height
    scale = min(scale_w, scale_h, 1.0)  # Don't upscale
    
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return frame


def create_mosaic_view(frames: List[np.ndarray], grid_size: Tuple[int, int] = None) -> np.ndarray:
    """
    Create a mosaic view from multiple frames.
    
    Args:
        frames: List of frames
        grid_size: Grid dimensions (rows, cols). Auto-calculated if None.
        
    Returns:
        Mosaic frame
    """
    if not frames:
        return np.zeros((480, 640, 3), dtype=np.uint8)
    
    num_frames = len(frames)
    
    if grid_size is None:
        # Auto-calculate grid size
        cols = int(np.ceil(np.sqrt(num_frames)))
        rows = int(np.ceil(num_frames / cols))
        grid_size = (rows, cols)
    
    rows, cols = grid_size
    
    # Resize all frames to same size
    target_height = frames[0].shape[0] // rows
    target_width = frames[0].shape[1] // cols
    
    resized_frames = []
    for frame in frames:
        resized = cv2.resize(frame, (target_width, target_height))
        resized_frames.append(resized)
    
    # Fill empty slots with black frames
    while len(resized_frames) < rows * cols:
        black_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        resized_frames.append(black_frame)
    
    # Create mosaic
    mosaic_rows = []
    for row in range(rows):
        row_frames = resized_frames[row * cols:(row + 1) * cols]
        mosaic_row = np.hstack(row_frames)
        mosaic_rows.append(mosaic_row)
    
    mosaic = np.vstack(mosaic_rows)
    return mosaic
