import platform
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# Third-party imports with graceful degradation
try:
    import cpuinfo
except ImportError:
    cpuinfo = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    import pynvml as nvml  # nvidia-ml-py package
except ImportError:
    nvml = None

import os
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class HardwareInfo:
    """Data class holding comprehensive hardware specifications."""
    # CPU Information
    cpu_vendor: str = "Unknown"
    cpu_brand: str = "Unknown"
    cpu_model: str = "Unknown"
    cpu_arch: str = "Unknown"
    cpu_physical_cores: int = 0
    cpu_logical_cores: int = 0
    cpu_frequency_base: float = 0.0  # GHz
    cpu_frequency_max: float = 0.0   # GHz
    cpu_simd: List[str] = field(default_factory=list)
    
    # Cache Information
    cache_l1_data: int = 0      # bytes
    cache_l1_instruction: int = 0  # bytes
    cache_l2: int = 0            # bytes
    cache_l3: int = 0            # bytes
    
    # Memory Information
    ram_total: int = 0           # bytes
    memory_type: str = "Unknown"  # DDR3, DDR4, DDR5, etc.
    memory_speed: int = 0        # MHz
    memory_channels: int = 0
    
    # GPU Information
    gpu_info: List[Dict[str, Any]] = field(default_factory=list)
    
    # OS Information
    os_info: str = "Unknown"
    os_version: str = "Unknown"
    os_kernel: str = "Unknown"
    os_architecture: str = "Unknown"
    
    # Performance Metrics
    theoretical_cpu_gflops: float = 0.0
    theoretical_gpu_gflops: float = 0.0

class HardwareDetector:
    """Detects system hardware capabilities."""

    def __init__(self):
        pass

    def detect(self) -> HardwareInfo:
        """
        Scan the system and return comprehensive HardwareInfo.
        """
        info = HardwareInfo()
        
        # 1. Enhanced CPU Detection
        self._detect_cpu_details(info)
        
        # 2. Cache Detection
        self._detect_cache_sizes(info)
        
        # 3. Enhanced Memory Detection
        self._detect_memory_details(info)
        
        # 4. Enhanced OS Detection
        self._detect_os_details(info)

        # 5. GPU Detection
        self._detect_gpu_details(info)
        
        # 6. Calculate Theoretical Performance
        self._calculate_theoretical_flops(info)
        
        return info
    
    def _detect_cpu_details(self, info: HardwareInfo):
        """Detect comprehensive CPU information."""
        if cpuinfo:
            try:
                cpu_data = cpuinfo.get_cpu_info()
                info.cpu_vendor = cpu_data.get('vendor_id_raw', 'Unknown')
                info.cpu_brand = cpu_data.get('brand_raw', 'Unknown')
                info.cpu_model = cpu_data.get('brand_raw', 'Unknown')
                info.cpu_arch = cpu_data.get('arch_string_raw', cpu_data.get('arch', 'Unknown'))
                info.cpu_logical_cores = cpu_data.get('count', 0)
                info.cpu_simd = cpu_data.get('flags', [])
                
                # Frequency in GHz
                hz = cpu_data.get('hz_advertised_friendly', '0 GHz')
                try:
                    # Parse "2.60 GHz" -> 2.60
                    freq_str = hz.split()[0]
                    info.cpu_frequency_base = float(freq_str)
                except:
                    pass
                
                # Try to get max frequency
                if 'hz_actual_friendly' in cpu_data:
                    try:
                        freq_str = cpu_data['hz_actual_friendly'].split()[0]
                        info.cpu_frequency_max = float(freq_str)
                    except:
                        info.cpu_frequency_max = info.cpu_frequency_base
                else:
                    info.cpu_frequency_max = info.cpu_frequency_base
                    
            except Exception as e:
                logger.warning(f"CPU detection failed: {e}")
        else:
            logger.warning("cpuinfo module not found. CPU details will be limited.")
            info.cpu_arch = platform.machine()
        
        # Get physical cores using psutil
        if psutil:
            try:
                info.cpu_physical_cores = psutil.cpu_count(logical=False) or 0
                if info.cpu_logical_cores == 0:
                    info.cpu_logical_cores = psutil.cpu_count(logical=True) or 0
            except Exception as e:
                logger.warning(f"Physical core detection failed: {e}")
    
    def _detect_cache_sizes(self, info: HardwareInfo):
        """Detect CPU cache sizes (L1, L2, L3)."""
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                self._get_macos_cache_info(info)
            elif system == "Linux":
                self._get_linux_cache_info(info)
            elif system == "Windows":
                self._get_windows_cache_info(info)
        except Exception as e:
            logger.warning(f"Cache detection failed: {e}")
    
    def _get_macos_cache_info(self, info: HardwareInfo):
        """Get cache info on macOS using sysctl."""
        try:
            # L1 data cache
            result = subprocess.run(['sysctl', '-n', 'hw.l1dcachesize'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                info.cache_l1_data = int(result.stdout.strip())
            
            # L1 instruction cache
            result = subprocess.run(['sysctl', '-n', 'hw.l1icachesize'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                info.cache_l1_instruction = int(result.stdout.strip())
            
            # L2 cache
            result = subprocess.run(['sysctl', '-n', 'hw.l2cachesize'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                info.cache_l2 = int(result.stdout.strip())
            
            # L3 cache
            result = subprocess.run(['sysctl', '-n', 'hw.l3cachesize'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                info.cache_l3 = int(result.stdout.strip())
        except Exception as e:
            logger.debug(f"macOS cache detection failed: {e}")
    
    def _get_linux_cache_info(self, info: HardwareInfo):
        """Get cache info on Linux from /sys or lscpu."""
        try:
            # Try lscpu first
            result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'L1d cache' in line:
                        size_str = line.split(':')[1].strip()
                        info.cache_l1_data = self._parse_size_string(size_str)
                    elif 'L1i cache' in line:
                        size_str = line.split(':')[1].strip()
                        info.cache_l1_instruction = self._parse_size_string(size_str)
                    elif 'L2 cache' in line:
                        size_str = line.split(':')[1].strip()
                        info.cache_l2 = self._parse_size_string(size_str)
                    elif 'L3 cache' in line:
                        size_str = line.split(':')[1].strip()
                        info.cache_l3 = self._parse_size_string(size_str)
        except Exception as e:
            logger.debug(f"Linux cache detection failed: {e}")
    
    def _get_windows_cache_info(self, info: HardwareInfo):
        """Get cache info on Windows using wmic."""
        try:
            result = subprocess.run(['wmic', 'cpu', 'get', 'L2CacheSize,L3CacheSize', '/format:list'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'L2CacheSize=' in line:
                        size = line.split('=')[1].strip()
                        if size:
                            info.cache_l2 = int(size) * 1024  # KB to bytes
                    elif 'L3CacheSize=' in line:
                        size = line.split('=')[1].strip()
                        if size:
                            info.cache_l3 = int(size) * 1024  # KB to bytes
        except Exception as e:
            logger.debug(f"Windows cache detection failed: {e}")
    
    def _parse_size_string(self, size_str: str) -> int:
        """Parse size string like '256 KiB' or '8 MiB' to bytes."""
        try:
            parts = size_str.strip().split()
            if len(parts) >= 2:
                value = float(parts[0])
                unit = parts[1].upper()
                
                if 'K' in unit:
                    return int(value * 1024)
                elif 'M' in unit:
                    return int(value * 1024 * 1024)
                elif 'G' in unit:
                    return int(value * 1024 * 1024 * 1024)
        except:
            pass
        return 0
    
    def _detect_memory_details(self, info: HardwareInfo):
        """Detect memory details including type and speed."""
        # Get total RAM
        if psutil:
            try:
                mem = psutil.virtual_memory()
                info.ram_total = mem.total
            except Exception as e:
                logger.warning(f"Memory detection failed: {e}")
        
        # Detect memory type and speed (platform-specific)
        system = platform.system()
        try:
            if system == "Darwin":
                self._get_macos_memory_info(info)
            elif system == "Linux":
                self._get_linux_memory_info(info)
            elif system == "Windows":
                self._get_windows_memory_info(info)
        except Exception as e:
            logger.warning(f"Memory type detection failed: {e}")
    
    def _get_macos_memory_info(self, info: HardwareInfo):
        """Get memory info on macOS."""
        try:
            result = subprocess.run(['system_profiler', 'SPMemoryDataType'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stdout
                # Parse memory type (DDR3, DDR4, etc.)
                for line in output.split('\n'):
                    if 'Type:' in line:
                        info.memory_type = line.split(':')[1].strip()
                    elif 'Speed:' in line:
                        speed_str = line.split(':')[1].strip()
                        # Parse "2667 MHz" -> 2667
                        try:
                            info.memory_speed = int(speed_str.split()[0])
                        except:
                            pass
        except Exception as e:
            logger.debug(f"macOS memory info detection failed: {e}")
    
    def _get_linux_memory_info(self, info: HardwareInfo):
        """Get memory info on Linux."""
        try:
            # Try dmidecode (requires sudo, may fail)
            result = subprocess.run(['dmidecode', '-t', 'memory'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stdout
                for line in output.split('\n'):
                    if 'Type:' in line and 'DDR' in line:
                        info.memory_type = line.split(':')[1].strip()
                    elif 'Speed:' in line and 'MHz' in line:
                        try:
                            speed_str = line.split(':')[1].strip()
                            info.memory_speed = int(speed_str.split()[0])
                        except:
                            pass
        except Exception as e:
            logger.debug(f"Linux memory info detection failed (may need sudo): {e}")
    
    def _get_windows_memory_info(self, info: HardwareInfo):
        """Get memory info on Windows."""
        try:
            result = subprocess.run(['wmic', 'memorychip', 'get', 'MemoryType,Speed', '/format:list'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'MemoryType=' in line:
                        mem_type_code = line.split('=')[1].strip()
                        # Map Windows memory type codes
                        type_map = {
                            '20': 'DDR', '21': 'DDR2', '24': 'DDR3', 
                            '26': 'DDR4', '34': 'DDR5'
                        }
                        info.memory_type = type_map.get(mem_type_code, f"Type {mem_type_code}")
                    elif 'Speed=' in line:
                        speed = line.split('=')[1].strip()
                        if speed:
                            info.memory_speed = int(speed)
        except Exception as e:
            logger.debug(f"Windows memory info detection failed: {e}")
    
    def _detect_os_details(self, info: HardwareInfo):
        """Detect detailed OS information."""
        try:
            info.os_info = platform.system()
            info.os_version = platform.version()
            info.os_kernel = platform.release()
            info.os_architecture = platform.machine()
            
            # Get more friendly OS version
            system = platform.system()
            if system == "Darwin":
                info.os_info = "macOS"
                try:
                    result = subprocess.run(['sw_vers', '-productVersion'], 
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        info.os_version = result.stdout.strip()
                except:
                    pass
            elif system == "Linux":
                try:
                    # Try to get distribution info
                    with open('/etc/os-release', 'r') as f:
                        for line in f:
                            if line.startswith('PRETTY_NAME='):
                                info.os_version = line.split('=')[1].strip().strip('"')
                                break
                except:
                    pass
            elif system == "Windows":
                info.os_version = platform.win32_ver()[0]
        except Exception as e:
            logger.warning(f"OS detection failed: {e}")
    
    def _detect_gpu_details(self, info: HardwareInfo):
        """Detect GPU details including vRAM and compute capability."""
        # Try nvidia-ml-py (nvml) first for NVIDIA
        if nvml:
            try:
                nvml.nvmlInit()
                try:
                    device_count = nvml.nvmlDeviceGetCount()
                    driver_version = nvml.nvmlSystemGetDriverVersion()
                    if isinstance(driver_version, bytes):
                        driver_version = driver_version.decode('utf-8')

                    for i in range(device_count):
                        handle = nvml.nvmlDeviceGetHandleByIndex(i)
                        name = nvml.nvmlDeviceGetName(handle)
                        if isinstance(name, bytes):
                            name = name.decode('utf-8')

                        mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                        util = nvml.nvmlDeviceGetUtilizationRates(handle)
                        temp = nvml.nvmlDeviceGetTemperature(handle, 0)
                        
                        # Get compute capability
                        try:
                            major, minor = nvml.nvmlDeviceGetCudaComputeCapability(handle)
                            compute_capability = f"{major}.{minor}"
                        except:
                            compute_capability = "Unknown"
                        
                        # Get GPU clock
                        try:
                            clock_mhz = nvml.nvmlDeviceGetClockInfo(handle, 0)  # 0 = graphics clock
                            clock_ghz = clock_mhz / 1000.0
                        except:
                            clock_ghz = 0.0

                        info.gpu_info.append({
                            'vendor': 'NVIDIA',
                            'name': name,
                            'memory_total': mem_info.total,
                            'memory_used': mem_info.used,
                            'memory_free': mem_info.free,
                            'load': util.gpu,
                            'temperature': temp,
                            'driver': driver_version,
                            'compute_capability': compute_capability,
                            'clock_ghz': clock_ghz
                        })
                    return  # Return early if nvml worked
                finally:
                    nvml.nvmlShutdown()
            except Exception as e:
                logger.warning(f"NVML detection failed: {e}")

        # Check for AMD ROCm
        if os.path.exists('/opt/rocm'):
            try:
                info.gpu_info.append({
                    'vendor': 'AMD',
                    'name': 'ROCm Detected (Detailed stats unavailable)',
                    'path': '/opt/rocm'
                })
            except Exception:
                pass

        # Fallback to GPUtil
        if GPUtil and not info.gpu_info:
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    info.gpu_info.append({
                        'vendor': 'NVIDIA',
                        'name': gpu.name,
                        'memory_total': gpu.memoryTotal * 1024 * 1024,
                        'memory_used': gpu.memoryUsed * 1024 * 1024,
                        'load': gpu.load * 100,
                        'driver': gpu.driver
                    })
            except Exception as e:
                logger.warning(f"GPUtil detection failed: {e}")
    
    def _calculate_theoretical_flops(self, info: HardwareInfo):
        """Calculate theoretical FLOPs for CPU and GPU."""
        # CPU FLOPs calculation
        if info.cpu_physical_cores > 0 and info.cpu_frequency_max > 0:
            # Determine SIMD width based on flags
            ops_per_cycle = 4  # Default SSE
            if 'avx512' in [flag.lower() for flag in info.cpu_simd]:
                ops_per_cycle = 32  # AVX-512: 16 double-precision FMA ops/cycle
            elif 'avx2' in [flag.lower() for flag in info.cpu_simd]:
                ops_per_cycle = 16  # AVX2: 8 double-precision FMA ops/cycle
            elif 'avx' in [flag.lower() for flag in info.cpu_simd]:
                ops_per_cycle = 8   # AVX: 4 double-precision FMA ops/cycle
            
            # FLOPs = cores × frequency (GHz) × ops_per_cycle × 10^9
            info.theoretical_cpu_gflops = (
                info.cpu_physical_cores * 
                info.cpu_frequency_max * 
                ops_per_cycle
            )
        
        # GPU FLOPs calculation (simplified)
        for gpu in info.gpu_info:
            if 'clock_ghz' in gpu and gpu['clock_ghz'] > 0:
                # This is a rough estimate - actual calculation depends on GPU architecture
                # For NVIDIA, we'd need CUDA cores count which isn't easily available
                # Placeholder calculation
                gpu['theoretical_gflops'] = 0.0  # Would need more GPU-specific info
