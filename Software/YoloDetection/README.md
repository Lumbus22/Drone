# YOLO11 USB Camera Object Detection

Real-time object detection using YOLO11 model with USB camera integration. This project provides a simple and efficient way to perform object detection on live camera feeds.

## Features

- 🎯 Real-time object detection using YOLO11
- 📷 USB camera integration with auto-detection
- 🔄 **Robust USB reconnection** - automatically handles unstable connections
- 👤 **Person recognition** - identify yourself and your team members
- ⚡ GPU acceleration support (CUDA)
- 🎨 Customizable visualization options
- 📊 FPS monitoring and performance metrics
- 💾 Frame saving and detection logging
- ⚙️ Easy configuration management
- 🛡️ Error recovery and connection monitoring
- 🎯 **Smart face database** - persistent face storage and management

## Requirements

- Python 3.8 or higher
- USB camera
- Windows/Linux/macOS

## Installation

1. **Clone or download this project**:
   ```bash
   cd YoloDetection
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install face recognition (optional)**:
   ```bash
   python install_face_recognition.py
   ```

4. **The YOLO11 model will be automatically downloaded** on first run. The default model (`yolo11n.pt`) is lightweight and fast.

## Quick Start

### Basic Usage

Run object detection with your default USB camera:

```bash
python main.py
```

### Advanced Usage

```bash
# Use a specific camera (camera ID 1)
python main.py --camera 1

# Use a larger model for better accuracy
python main.py --model yolo11s.pt

# Set custom confidence threshold
python main.py --confidence 0.7

# Use GPU acceleration (if CUDA is available)
python main.py --device cuda

# Custom resolution
python main.py --width 1280 --height 720

# Run without display (for headless systems)
python main.py --no-display

# Control USB reconnection behavior
python main.py --max-reconnect 10 --reconnect-delay 3.0

# Test reconnection with demo
python demo_reconnect.py

# Enable face recognition
python main.py --face-recognition

# Register your team
python register_faces.py --team
```

## Person Recognition Setup

### Quick Team Registration

The easiest way to set up person recognition for your team:

```bash
# 1. Register your team members
python register_faces.py --team

# 2. Run detection with face recognition
python main.py --face-recognition
```

### Individual Registration

Register people one by one:

```bash
# Register from camera
python register_faces.py --name "John" --camera --description "Team lead"

# Register from image files
python register_faces.py --name "Jane" --images photo1.jpg photo2.jpg

# Interactive registration
python register_faces.py --interactive
```

### During Detection

While running the main program:
- Press **'r'** to register a new person from the current camera view
- Face recognition runs automatically if enabled
- Green boxes = recognized team members
- Red boxes = unknown people

### Find Available Cameras

Use this simple script to find your camera IDs:

```python
from utils import get_available_cameras
cameras = get_available_cameras()
print(f"Available cameras: {cameras}")
```

## Controls

While the detection window is active:

- **`q`**: Quit the application
- **`s`**: Save current frame with detections
- **`ESC`**: Alternative quit key

## Model Options

YOLO11 offers different model sizes for different performance needs:

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `yolo11n.pt` | 6.2MB | Fastest | Good | Real-time applications |
| `yolo11s.pt` | 21.5MB | Fast | Better | Balanced performance |
| `yolo11m.pt` | 49.7MB | Medium | High | Higher accuracy needed |
| `yolo11l.pt` | 86.9MB | Slow | Higher | Best accuracy |
| `yolo11x.pt` | 155.0MB | Slowest | Highest | Maximum accuracy |

## Configuration

Edit `config.py` to customize:

### Model Settings
```python
MODEL_CONFIG = {
    "model_path": "yolo11n.pt",
    "confidence_threshold": 0.5,
    "device": "cpu",  # or "cuda" for GPU
}
```

### Camera Settings
```python
CAMERA_CONFIG = {
    "camera_id": 0,
    "width": 640,
    "height": 480,
    "fps": 30,
    "reconnect_attempts": -1,  # -1 = infinite attempts
    "reconnect_delay": 2.0,    # seconds between attempts
    "connection_timeout": 5.0, # connection timeout
    "frame_timeout": 1.0,      # frame read timeout
}
```

### Face Recognition Settings
```python
FACE_RECOGNITION_CONFIG = {
    "enabled": True,  # Enable/disable face recognition
    "database_path": "faces_database",  # Face database directory
    "recognition_threshold": 0.6,  # Lower = more strict matching
    "face_detection_model": "hog",  # "hog" (faster) or "cnn" (more accurate)
    "min_face_size": 50,  # Minimum face size in pixels
    "save_unknown_faces": True,  # Save unknown faces for review
}
```

### Display Settings
```python
DISPLAY_CONFIG = {
    "show_fps": True,
    "show_labels": True,
    "show_confidence": True,
    "font_scale": 0.7,
}
```

## Detectable Objects

YOLO11 can detect 80 different object classes from the COCO dataset, including:

**People & Animals**: person, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, bird
**Vehicles**: car, motorcycle, airplane, bus, train, truck, boat, bicycle
**Electronics**: laptop, mouse, remote, keyboard, cell phone, tv
**Furniture**: chair, couch, bed, dining table, toilet
**Food**: banana, apple, sandwich, orange, pizza, donut, cake
**And many more...**

See `config.py` for the complete list.

## Face Recognition

The system can recognize **unlimited people** that you register in the face database. Recognition works by:

1. **Detecting faces** in the camera feed using advanced algorithms
2. **Encoding facial features** into mathematical representations
3. **Comparing** with stored encodings of known people
4. **Identifying** matches above the confidence threshold

### Recognition Features:
- **Multiple faces** - can recognize several people simultaneously
- **High accuracy** - adjustable confidence threshold
- **Fast processing** - optimized for real-time performance
- **Persistent storage** - face database survives program restarts
- **Unknown face capture** - automatically saves unrecognized faces for review

## Troubleshooting

### USB Connection Issues

**Unstable USB connection**:
The program now automatically handles USB disconnections! Features include:
- ✅ Automatic reconnection when USB is plugged back in
- ✅ Configurable retry attempts and delays
- ✅ Real-time connection status display
- ✅ No crashes when camera disconnects

**Test reconnection behavior**:
```bash
python demo_reconnect.py
```

### Camera Issues

**Camera not found**:
```python
# Test camera availability
from utils import get_available_cameras, test_camera
print("Available cameras:", get_available_cameras())
print("Camera 0 working:", test_camera(0))
```

**Permission denied (Linux)**:
```bash
sudo usermod -a -G video $USER
# Then logout and login again
```

### Performance Issues

**Low FPS**:
- Use a smaller model (`yolo11n.pt`)
- Reduce camera resolution
- Enable GPU acceleration
- Close other applications

**High CPU usage**:
```python
# In config.py, reduce camera buffer
CAMERA_CONFIG = {
    "buffer_size": 1,  # Minimize latency
}
```

### GPU Acceleration

**CUDA Setup** (Windows):
1. Install CUDA toolkit from NVIDIA
2. Install PyTorch with CUDA support:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
3. Run with: `python main.py --device cuda`

## Project Structure

```
YoloDetection/
├── main.py              # Main detection script
├── config.py            # Configuration settings
├── utils.py             # Utility functions
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Performance Tips

1. **Choose the right model**: Start with `yolo11n.pt` for real-time performance
2. **Optimize camera settings**: Lower resolution = higher FPS
3. **Use GPU**: Significant speedup with CUDA-capable graphics cards
4. **Reduce confidence threshold**: Fewer detections = better performance
5. **Close unnecessary applications**: Free up system resources

## Common Use Cases

### Security Camera
```bash
python main.py --confidence 0.6 --no-display > detections.log
```

### Demo/Presentation
```bash
python main.py --model yolo11s.pt --width 1280 --height 720
```

### Development/Testing
```bash
python main.py --confidence 0.3 --device cuda
```

## Contributing

Feel free to improve this project by:
- Adding new features
- Optimizing performance
- Fixing bugs
- Improving documentation

## License

This project is open source. The YOLO11 model is subject to Ultralytics' license terms.

## Support

For issues or questions:
1. Check this README thoroughly
2. Review the troubleshooting section
3. Check camera permissions and connections
4. Ensure all dependencies are properly installed

---

**Happy detecting! 🎯**
