import pytest
from unittest.mock import patch, MagicMock
from code.profiler.hardware import HardwareDetector, HardwareInfo

@pytest.fixture
def detector():
    return HardwareDetector()

def test_hardware_info_structure():
    info = HardwareInfo(
        cpu_vendor="TestVendor",
        cpu_arch="TestArch",
        cpu_cores=4,
        cpu_simd=["AVX"],
        gpu_info=[],
        os_info="TestOS",
        ram_total=16000
    )
    assert info.cpu_vendor == "TestVendor"
    assert info.cpu_cores == 4

@patch('code.profiler.hardware.cpuinfo')
@patch('code.profiler.hardware.psutil')
@patch('code.profiler.hardware.platform.system')
def test_detect_cpu_and_os(mock_system, mock_psutil, mock_cpuinfo, detector):
    # Mock CPU info
    # If cpuinfo was None in the module, patch replaces it with a Mock
    mock_cpuinfo.get_cpu_info.return_value = {
        'vendor_id_raw': 'GenuineIntel',
        'arch': 'X86_64',
        'count': 8,
        'flags': ['avx', 'sse']
    }
    
    # Mock Memory
    mock_mem = MagicMock()
    mock_mem.total = 16 * 1024 * 1024 * 1024
    mock_psutil.virtual_memory.return_value = mock_mem
    
    # Mock OS
    mock_system.return_value = 'Linux'
    
    info = detector.detect()
    
    assert info.cpu_vendor == 'GenuineIntel'
    assert info.cpu_arch == 'X86_64'
    assert info.cpu_cores == 8
    assert 'avx' in info.cpu_simd
    assert info.ram_total == 16 * 1024 * 1024 * 1024
    assert info.os_info == 'Linux'

@patch('code.profiler.hardware.GPUtil')
def test_detect_gpu_nvidia(mock_gputil, detector):
    # Mock GPU
    mock_gpu = MagicMock()
    mock_gpu.name = 'NVIDIA GeForce RTX 3080'
    mock_gpu.memoryTotal = 10240
    mock_gpu.driver = '535.104'
    
    mock_gputil.getGPUs.return_value = [mock_gpu]
    
    # We need to mock the other calls to avoid errors during full detect or side effects
    with patch('code.profiler.hardware.cpuinfo'), \
         patch('code.profiler.hardware.psutil'), \
         patch('code.profiler.hardware.platform.system'):
        
        info = detector.detect()

        assert len(info.gpu_info) == 1
        assert info.gpu_info[0]['name'] == 'NVIDIA GeForce RTX 3080'
        assert info.gpu_info[0]['memory_total'] == 10240 * 1024 * 1024  # GPUtil returns MB, we convert to bytes

def test_detect_gpu_no_driver(detector):
    # Simulate GPUtil being None or raising ImportError
    # Since we handle the import in the module, if it's missing, it's None.
    # If we want to test the "else" branch where GPUtil is None:
    with patch('code.profiler.hardware.GPUtil', None):
        with patch('code.profiler.hardware.cpuinfo'), \
             patch('code.profiler.hardware.psutil'), \
             patch('code.profiler.hardware.platform.system'):
            
            info = detector.detect()
            assert info.gpu_info == []
