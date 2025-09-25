#!/usr/bin/env python3
"""
Windows Face Recognition Installation Fix
Solves common Windows installation issues for dlib and face recognition.
"""

import subprocess
import sys
import os
import platform
import requests
import zipfile
from pathlib import Path


def is_windows():
    """Check if running on Windows."""
    return platform.system().lower() == 'windows'


def check_cmake():
    """Check if CMake is properly installed."""
    try:
        result = subprocess.run(['cmake', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ CMake is installed: {result.stdout.split()[2]}")
            return True
        else:
            print("❌ CMake is not working properly")
            return False
    except FileNotFoundError:
        print("❌ CMake is not installed or not in PATH")
        return False


def install_cmake_windows():
    """Install CMake on Windows."""
    print("🔧 Installing CMake for Windows...")
    print("Please follow these steps:")
    print("\n1. Download CMake from: https://cmake.org/download/")
    print("2. Choose 'Windows x64 Installer' (.msi file)")
    print("3. During installation, check 'Add CMake to system PATH'")
    print("4. Restart your command prompt after installation")
    print("\nAlternatively, if you have Chocolatey installed:")
    print("   choco install cmake")
    print("\nOr if you have winget:")
    print("   winget install Kitware.CMake")
    
    input("\nPress Enter after installing CMake...")
    return check_cmake()


def download_precompiled_dlib():
    """Download precompiled dlib wheel for Windows."""
    print("🔄 Attempting to install precompiled dlib...")
    
    # Try installing with pip directly first
    commands_to_try = [
        "pip install dlib --no-cache-dir",
        "pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.0-cp39-cp39-win_amd64.whl",
        "pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.0-cp310-cp310-win_amd64.whl",
        "pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.0-cp311-cp311-win_amd64.whl",
    ]
    
    for cmd in commands_to_try:
        print(f"Trying: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Successfully installed dlib!")
                return True
            else:
                print(f"❌ Failed: {result.stderr[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False


def install_visual_studio_build_tools():
    """Guide user to install Visual Studio Build Tools."""
    print("🔧 Visual Studio Build Tools Installation")
    print("=" * 50)
    print("To compile dlib from source, you need Visual Studio Build Tools.")
    print("\nOption 1 - Visual Studio Build Tools (Recommended):")
    print("1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print("2. Run the installer")
    print("3. Select 'C++ build tools'")
    print("4. Install and restart")
    
    print("\nOption 2 - Full Visual Studio Community:")
    print("1. Download from: https://visualstudio.microsoft.com/vs/community/")
    print("2. Install with C++ development tools")
    
    print("\nOption 3 - Use precompiled wheels (easier):")
    print("We'll try to download precompiled dlib wheels instead.")


def fix_windows_installation():
    """Complete Windows installation fix."""
    print("🪟 Windows Face Recognition Installation Fix")
    print("=" * 50)
    
    if not is_windows():
        print("❌ This script is for Windows only")
        return False
    
    print("Python version:", sys.version)
    print("Platform:", platform.platform())
    
    # Step 1: Check and install CMake
    print("\n📋 Step 1: Checking CMake...")
    if not check_cmake():
        print("CMake is required for compiling dlib.")
        choice = input("Install CMake now? (y/n): ").lower().strip()
        if choice.startswith('y'):
            if not install_cmake_windows():
                print("❌ CMake installation failed")
                return False
        else:
            print("⏭️  Skipping CMake installation")
    
    # Step 2: Try precompiled dlib first
    print("\n📋 Step 2: Installing dlib...")
    print("Trying precompiled wheels first (recommended)...")
    
    if download_precompiled_dlib():
        print("✅ dlib installed successfully!")
    else:
        print("❌ Precompiled dlib installation failed")
        print("\nYou have two options:")
        print("1. Install Visual Studio Build Tools and compile from source")
        print("2. Try alternative installation methods")
        
        choice = input("Choose option (1/2): ").strip()
        
        if choice == "1":
            install_visual_studio_build_tools()
            input("Press Enter after installing Visual Studio Build Tools...")
            
            # Try installing dlib from source
            print("🔄 Attempting to compile dlib from source...")
            result = subprocess.run("pip install dlib --no-cache-dir", shell=True)
            if result.returncode != 0:
                print("❌ Source compilation failed")
                return False
        else:
            print("❌ Installation aborted")
            return False
    
    # Step 3: Install face_recognition
    print("\n📋 Step 3: Installing face_recognition...")
    result = subprocess.run("pip install face_recognition", shell=True, capture_output=True)
    if result.returncode == 0:
        print("✅ face_recognition installed successfully!")
    else:
        print("❌ face_recognition installation failed")
        print(result.stderr.decode())
        return False
    
    # Step 4: Test installation
    print("\n📋 Step 4: Testing installation...")
    try:
        import dlib
        import face_recognition
        print("✅ All packages imported successfully!")
        print(f"dlib version: {dlib.DLIB_VERSION}")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def alternative_solutions():
    """Show alternative solutions."""
    print("\n🔧 Alternative Solutions")
    print("=" * 30)
    print("If the automated installation fails, try these:")
    
    print("\n1. Use Anaconda/Miniconda:")
    print("   conda install -c conda-forge dlib")
    print("   conda install -c conda-forge face_recognition")
    
    print("\n2. Use Windows Subsystem for Linux (WSL):")
    print("   Install WSL2 and run the project in Linux environment")
    
    print("\n3. Use Docker:")
    print("   Run the entire project in a Docker container")
    
    print("\n4. Manual wheel download:")
    print("   Visit: https://pypi.org/project/dlib/#files")
    print("   Download appropriate .whl file for your Python version")
    print("   Install with: pip install downloaded_file.whl")
    
    print("\n5. Use older dlib version:")
    print("   pip install dlib==19.22.0")


def main():
    print("🎯 Windows Installation Troubleshooter")
    print("=" * 40)
    print("This script will help fix dlib installation issues on Windows.")
    
    print("\nOptions:")
    print("1. Automated fix (recommended)")
    print("2. Show alternative solutions")
    print("3. Check current installation")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        success = fix_windows_installation()
        if success:
            print("\n🎉 Installation completed successfully!")
            print("You can now use face recognition:")
            print("  python register_faces.py --team")
            print("  python main.py --face-recognition")
        else:
            print("\n❌ Installation failed. Try alternative solutions.")
            alternative_solutions()
    
    elif choice == "2":
        alternative_solutions()
    
    elif choice == "3":
        print("\n🔍 Checking current installation...")
        check_cmake()
        
        packages = ["dlib", "face_recognition", "cmake"]
        for package in packages:
            try:
                __import__(package)
                print(f"✅ {package} is installed")
            except ImportError:
                print(f"❌ {package} is not installed")
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
