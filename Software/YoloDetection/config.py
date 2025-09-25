"""
Configuration settings for YOLO11 Object Detection
"""

# Model Configuration
MODEL_CONFIG = {
    "model_path": "yolo11n.pt",  # Options: yolo11n.pt, yolo11s.pt, yolo11m.pt, yolo11l.pt, yolo11x.pt
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "device": "cuda",  # Options: "cpu", "cuda", "mps"
}

# Camera Configuration
CAMERA_CONFIG = {
    "camera_id": 0,  # USB camera device ID (usually 0 for first camera)
    "width": 640,
    "height": 480,
    "fps": 30,
    "buffer_size": 1,  # Reduce buffer to minimize latency
    "reconnect_attempts": -1,  # Max reconnection attempts (-1 = infinite)
    "reconnect_delay": 2.0,  # Delay between reconnection attempts (seconds)
    "connection_timeout": 5.0,  # Timeout for initial connection (seconds)
    "frame_timeout": 1.0,  # Timeout for frame reading (seconds)
}

# Display Configuration
DISPLAY_CONFIG = {
    "show_fps": True,
    "show_labels": True,
    "show_confidence": True,
    "font_scale": 0.7,
    "font_thickness": 2,
    "bbox_thickness": 2,
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "max_det": 300,  # Maximum number of detections per image
    "half_precision": False,  # Use FP16 for faster inference (requires CUDA)
    "verbose": False,  # Verbose output from YOLO
}

# Class names that YOLO11 can detect (COCO dataset classes)
COCO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
    'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
    'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
    'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
    'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
    'toothbrush'
]

# Face Recognition Configuration
FACE_RECOGNITION_CONFIG = {
    "enabled": True,  # Enable/disable face recognition
    "database_path": "faces_database",  # Directory to store face encodings
    "recognition_threshold": 0.6,  # Lower = more strict matching
    "face_detection_model": "hog",  # "hog" (faster) or "cnn" (more accurate, requires GPU)
    "num_jitters": 1,  # Number of times to re-sample face for encoding (higher = more accurate, slower)
    "show_confidence": True,  # Show recognition confidence scores
    "min_face_size": 50,  # Minimum face size in pixels
    "recognition_interval": 5,  # Frames between face recognition attempts (for performance)
    "save_unknown_faces": True,  # Save unknown faces for later review
    "unknown_faces_path": "unknown_faces",  # Directory for unknown faces
}

# Colors for different classes (BGR format for OpenCV)
CLASS_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
    (0, 255, 255), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0),
    (128, 0, 128), (0, 128, 128), (192, 192, 192), (128, 128, 128), (255, 165, 0),
    (255, 20, 147), (0, 191, 255), (255, 69, 0), (255, 140, 0), (75, 0, 130),
]

# Face recognition colors (BGR format)
FACE_COLORS = {
    "known": (0, 255, 0),      # Green for known faces
    "unknown": (0, 0, 255),    # Red for unknown faces
    "processing": (0, 255, 255), # Yellow for faces being processed
}
