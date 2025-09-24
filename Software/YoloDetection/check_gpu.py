#!/usr/bin/env python3
"""
GPU availability checker for YOLO11 object detection
"""

import torch
import cv2


def check_gpu_support():
    """Check GPU support and availability."""
    print("GPU Support Checker")
    print("=" * 40)
    
    # Check PyTorch CUDA support
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available in PyTorch: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        
        # Test GPU allocation
        try:
            test_tensor = torch.zeros(1).cuda()
            print("✅ GPU tensor allocation successful")
            del test_tensor
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"❌ GPU tensor allocation failed: {e}")
    else:
        print("❌ CUDA not available")
        print("\nTo enable GPU support:")
        print("1. Install NVIDIA drivers")
        print("2. Install CUDA toolkit")
        print("3. Install PyTorch with CUDA:")
        print("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
    
    # Check OpenCV CUDA support
    print(f"\nOpenCV CUDA support: {cv2.cuda.getCudaEnabledDeviceCount() > 0}")
    
    return torch.cuda.is_available()


def benchmark_devices():
    """Benchmark CPU vs GPU performance."""
    if not torch.cuda.is_available():
        print("GPU not available for benchmarking")
        return
    
    print("\nRunning device benchmark...")
    
    # Create test data
    test_data = torch.randn(1, 3, 640, 640)
    
    # CPU benchmark
    start_time = time.time()
    for _ in range(10):
        _ = test_data * 2
    cpu_time = time.time() - start_time
    
    # GPU benchmark
    test_data_gpu = test_data.cuda()
    torch.cuda.synchronize()
    start_time = time.time()
    for _ in range(10):
        _ = test_data_gpu * 2
    torch.cuda.synchronize()
    gpu_time = time.time() - start_time
    
    print(f"CPU time: {cpu_time:.3f}s")
    print(f"GPU time: {gpu_time:.3f}s")
    print(f"GPU speedup: {cpu_time/gpu_time:.1f}x")
    
    # Cleanup
    del test_data_gpu
    torch.cuda.empty_cache()


if __name__ == "__main__":
    import time
    
    gpu_available = check_gpu_support()
    
    if gpu_available:
        benchmark_devices()
        print(f"\n✅ Your system supports GPU acceleration!")
        print("To use GPU with YOLO detection:")
        print("  python main.py --device cuda")
        print("Or edit config.py and change device to 'cuda'")
    else:
        print(f"\n❌ GPU acceleration not available")
        print("The program will run on CPU (slower but still functional)")
