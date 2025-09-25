#!/usr/bin/env python3
"""
Face Recognition Installation Helper
Helps install and test face recognition dependencies.
"""

import subprocess
import sys
import os
import importlib


def run_command(command, description):
    """Run a command and show progress."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False


def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is not installed")
        return False


def install_face_recognition():
    """Install face recognition dependencies."""
    print("🎯 Face Recognition Installation")
    print("=" * 40)
    
    # Check system requirements
    print("\n📋 Checking system requirements...")
    
    # Check if we're on Windows
    is_windows = os.name == 'nt'
    
    if is_windows:
        print("🪟 Windows detected")
        print("Note: On Windows, you may need Visual Studio Build Tools")
        print("Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 6):
        print("❌ Python 3.6+ is required for face recognition")
        return False
    
    # Install packages step by step
    packages_to_install = [
        ("cmake", "CMake (required for dlib)"),
        ("dlib", "dlib (face detection library)"),
        ("face-recognition", "face-recognition (main library)"),
    ]
    
    print("\n📦 Installing packages...")
    
    for package, description in packages_to_install:
        success = run_command(f"pip install {package}", f"Installing {description}")
        if not success:
            print(f"\n⚠️  Failed to install {package}")
            print("You can try:")
            print(f"  pip install --upgrade pip")
            print(f"  pip install {package} --no-cache-dir")
            if is_windows and package == "dlib":
                print("  Or download pre-compiled wheel from:")
                print("  https://github.com/z-mahmud22/Dlib_Windows_Python3.x")
    
    # Test installation
    print("\n🧪 Testing installation...")
    
    test_packages = [
        ("cmake", "cmake"),
        ("dlib", "dlib"),
        ("face-recognition", "face_recognition"),
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
    ]
    
    all_success = True
    for package, import_name in test_packages:
        if not check_package(package, import_name):
            all_success = False
    
    if all_success:
        print("\n🎉 All packages installed successfully!")
        print("\nYou can now use face recognition features:")
        print("  python register_faces.py --team")
        print("  python main.py --face-recognition")
        return True
    else:
        print("\n❌ Some packages failed to install")
        print("Please check the error messages above and try manual installation")
        return False


def test_face_recognition():
    """Test face recognition functionality."""
    print("\n🧪 Testing face recognition...")
    
    try:
        import face_recognition
        import cv2
        import numpy as np
        
        # Create a test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Try face detection
        face_locations = face_recognition.face_locations(test_image)
        print(f"✅ Face detection test passed (found {len(face_locations)} faces)")
        
        print("✅ Face recognition is working!")
        return True
        
    except Exception as e:
        print(f"❌ Face recognition test failed: {e}")
        return False


def main():
    print("🎯 Face Recognition Setup Helper")
    print("=" * 40)
    print("This script will help you install face recognition dependencies.")
    print("\nOptions:")
    print("1. Install face recognition packages")
    print("2. Test existing installation")
    print("3. Show installation instructions")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        success = install_face_recognition()
        if success:
            test_face_recognition()
    
    elif choice == "2":
        test_face_recognition()
    
    elif choice == "3":
        print("\n📖 Manual Installation Instructions")
        print("=" * 40)
        print("1. Install CMake:")
        print("   pip install cmake")
        print("\n2. Install dlib:")
        print("   pip install dlib")
        print("   (This may take several minutes)")
        print("\n3. Install face-recognition:")
        print("   pip install face-recognition")
        print("\n4. Test installation:")
        print("   python -c \"import face_recognition; print('Success!')\"")
        print("\nTroubleshooting:")
        print("- On Windows: Install Visual Studio Build Tools")
        print("- On Ubuntu: sudo apt-get install build-essential cmake")
        print("- On macOS: Install Xcode command line tools")
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
