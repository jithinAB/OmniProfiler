import pytest
from unittest.mock import patch, MagicMock
import sys

@pytest.fixture
def detector():
    # Import inside fixture to ensure patches are applied if we were reloading,
    # but here we rely on patching before import or patching the module attribute.
    from code.profiler.hardware import HardwareDetector
    return HardwareDetector()

def test_detect_gpu_nvidia_pynvml():
    # Create a mock for nvml module (nvidia-ml-py, formerly pynvml)
    mock_nvml = MagicMock()
    mock_nvml.nvmlDeviceGetCount.return_value = 1

    mock_handle = MagicMock()
    mock_nvml.nvmlDeviceGetHandleByIndex.return_value = mock_handle
    mock_nvml.nvmlDeviceGetName.return_value = b"NVIDIA Tesla T4"

    mock_memory = MagicMock()
    mock_memory.total = 16 * 1024 * 1024 * 1024
    mock_memory.used = 4 * 1024 * 1024 * 1024
    mock_memory.free = 12 * 1024 * 1024 * 1024
    mock_nvml.nvmlDeviceGetMemoryInfo.return_value = mock_memory

    mock_util = MagicMock()
    mock_util.gpu = 45
    mock_nvml.nvmlDeviceGetUtilizationRates.return_value = mock_util

    mock_nvml.nvmlDeviceGetTemperature.return_value = 65
    mock_nvml.nvmlSystemGetDriverVersion.return_value = b"535.104"

    # Patch the module in code.profiler.hardware
    # We renamed pynvml to nvml in hardware.py
    with patch('code.profiler.hardware.nvml', mock_nvml):
        with patch('code.profiler.hardware.cpuinfo'), \
             patch('code.profiler.hardware.psutil'), \
             patch('code.profiler.hardware.platform.system'), \
             patch('code.profiler.hardware.GPUtil', None):

            from code.profiler.hardware import HardwareDetector
            detector = HardwareDetector()
            info = detector.detect()

            assert len(info.gpu_info) == 1
            gpu = info.gpu_info[0]
            assert gpu['name'] == "NVIDIA Tesla T4"
            assert gpu['load'] == 45

def test_detect_gpu_amd_rocm():
    # Mock existence of /opt/rocm
    with patch('code.profiler.hardware.os.path.exists') as mock_exists:
        mock_exists.side_effect = lambda p: p == '/opt/rocm'

        with patch('code.profiler.hardware.cpuinfo'), \
             patch('code.profiler.hardware.psutil'), \
             patch('code.profiler.hardware.platform.system'), \
             patch('code.profiler.hardware.nvml', None), \
             patch('code.profiler.hardware.GPUtil', None):

            from code.profiler.hardware import HardwareDetector
            detector = HardwareDetector()
            info = detector.detect()

            assert any(g['vendor'] == 'AMD' for g in info.gpu_info)
