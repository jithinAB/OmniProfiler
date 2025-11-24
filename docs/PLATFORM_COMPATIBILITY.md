# Platform Compatibility Guide

## Overview
Omni-Profiler is designed to be **cross-platform** and works on Windows, macOS, and Linux with graceful degradation when certain features are unavailable.

## Supported Platforms

### ✅ Fully Supported
- **Windows** 10/11 (x64, ARM64)
- **macOS** 10.15+ (Intel, Apple Silicon)
- **Linux** (Ubuntu 20.04+, Debian, RHEL, Fedora, Arch)

### Architecture Support
- x86_64 (Intel/AMD 64-bit)
- ARM64 (Apple Silicon, ARM servers)
- x86 (32-bit, limited testing)

## Feature Availability Matrix

| Feature | Windows | macOS | Linux | Notes |
|---------|---------|-------|-------|-------|
| **CPU Detection** | ✅ | ✅ | ✅ | Via py-cpuinfo |
| **CPU Brand/Model** | ✅ | ✅ | ✅ | Full details |
| **CPU Frequency** | ✅ | ✅ | ✅ | Base & max frequency |
| **Physical/Logical Cores** | ✅ | ✅ | ✅ | Via psutil |
| **L1 Cache** | ⚠️ | ✅ | ✅ | Windows: Limited via wmic |
| **L2 Cache** | ✅ | ✅ | ✅ | All platforms |
| **L3 Cache** | ✅ | ✅ | ✅ | All platforms |
| **Memory Total** | ✅ | ✅ | ✅ | Via psutil |
| **Memory Type** | ✅ | ✅ | ⚠️ | Linux: May need sudo for dmidecode |
| **Memory Speed** | ✅ | ⚠️ | ⚠️ | Windows: Full support, Unix: Limited |
| **GPU (NVIDIA)** | ✅ | ✅ | ✅ | Requires nvidia-ml-py + drivers |
| **GPU (AMD)** | ⚠️ | ⚠️ | ⚠️ | Basic ROCm detection only |
| **GPU (Intel)** | ❌ | ❌ | ❌ | Not yet supported |
| **OS Version** | ✅ | ✅ | ✅ | Via platform module |
| **Kernel Version** | ✅ | ✅ | ✅ | All platforms |
| **Context Switches** | ✅ | ✅ | ✅ | resource (Unix) / psutil (Windows) |
| **I/O Metrics** | ✅ | ⚠️ | ✅ | macOS: Requires root for process I/O |
| **Memory Profiling** | ✅ | ✅ | ✅ | Via tracemalloc (built-in) |
| **GC Metrics** | ✅ | ✅ | ✅ | Via gc module (built-in) |
| **Theoretical FLOPs** | ✅ | ✅ | ✅ | Calculated from CPU specs |
| **Call Tree** | ✅ | ✅ | ✅ | Via pyinstrument |
| **Hotspots** | ✅ | ✅ | ✅ | Via cProfile |

**Legend**:
- ✅ Fully supported
- ⚠️ Partially supported or requires special permissions
- ❌ Not supported

## Dependencies

### Required (All Platforms)
```bash
pip install psutil py-cpuinfo pyinstrument
```

- **psutil** - Process and system utilities (cross-platform)
- **py-cpuinfo** - CPU information detection (cross-platform)
- **pyinstrument** - Call tree profiling (cross-platform)

### Optional (GPU Support)
```bash
# NVIDIA GPU support
pip install nvidia-ml-py

# Alternative NVIDIA support
pip install GPUtil
```

### Platform-Specific Tools

#### macOS
**Auto-detected** (no installation needed):
- `sysctl` - CPU and cache information
- `system_profiler` - Memory details
- `sw_vers` - OS version

#### Linux
**Auto-detected** (usually pre-installed):
- `lscpu` - CPU and cache information
- `dmidecode` - Memory type/speed (requires sudo)
- `lshw` - Hardware information (fallback)

**Optional** (for enhanced memory detection):
```bash
sudo apt-get install dmidecode  # Debian/Ubuntu
sudo yum install dmidecode      # RHEL/CentOS
```

#### Windows
**Auto-detected** (built-in):
- `wmic` - Windows Management Instrumentation

## Known Limitations

### macOS
- **I/O Metrics**: `psutil.Process.io_counters()` requires root privileges
  - **Workaround**: Run with sudo or accept 0 values
  - **Impact**: I/O read/write counts will be 0 for non-root users

### Linux
- **Memory Type/Speed**: Requires `dmidecode` with sudo
  - **Workaround**: Run with sudo or install dmidecode
  - **Impact**: Memory type shows "Unknown" without sudo

### Windows
- **L1 Cache**: Limited detection via wmic
  - **Impact**: L1 cache may show 0 or incomplete data
  - **Workaround**: None, Windows limitation

### All Platforms
- **GPU (AMD)**: Only basic ROCm detection
  - **Impact**: Limited AMD GPU information
  - **Future**: May add ROCm-SMI integration

## Error Handling

All platform-specific code includes:
1. **Try-except blocks** - Catches missing tools/permissions
2. **Timeouts** - Subprocess calls timeout after 2-5 seconds
3. **Graceful degradation** - Returns "Unknown" or 0 if detection fails
4. **Logging** - Warnings logged for debugging

Example:
```python
try:
    if system == "Darwin":  # macOS
        self._get_macos_cache_info(info)
    elif system == "Linux":
        self._get_linux_cache_info(info)
    elif system == "Windows":
        self._get_windows_cache_info(info)
except Exception as e:
    logger.warning(f"Cache detection failed: {e}")
    # Returns 0 for cache sizes
```

## Testing

### Tested Platforms
- ✅ macOS 15.3.1 (Apple Silicon M1)
- ⚠️ Linux (CI testing recommended)
- ⚠️ Windows (CI testing recommended)

### Testing Without Platform
You can test platform-specific code using mocks:
```python
# Mock platform.system() for testing
with patch('platform.system', return_value='Windows'):
    detector = HardwareDetector()
    info = detector.detect()
```

## Troubleshooting

### "Module not found" errors
**Solution**: Install required dependencies
```bash
pip install -r requirements.txt
```

### Memory type shows "Unknown" on Linux
**Solution**: Install dmidecode and run with sudo
```bash
sudo apt-get install dmidecode
sudo python -m code.cli serve
```

### I/O metrics are 0 on macOS
**Solution**: This is expected for non-root users. Run with sudo if needed:
```bash
sudo python -m code.cli serve
```

### GPU not detected
**Solution**: 
1. Ensure GPU drivers are installed
2. Install nvidia-ml-py: `pip install nvidia-ml-py`
3. Check GPU is recognized: `nvidia-smi` (NVIDIA)

## Best Practices

1. **Don't assume platform-specific features** - Always check return values
2. **Use cross-platform libraries** - Prefer psutil over platform-specific tools
3. **Provide fallbacks** - Gracefully degrade when features unavailable
4. **Log warnings, not errors** - Missing features shouldn't crash
5. **Document limitations** - Be clear about platform differences

## Contributing

When adding new platform-specific features:
1. Use `platform.system()` to detect OS
2. Wrap in try-except with timeout
3. Provide fallback for other platforms
4. Test on all major platforms
5. Document in this file

## Support

For platform-specific issues:
1. Check this compatibility guide
2. Review logs for warnings
3. Verify dependencies installed
4. Test with minimal example
5. Report issue with platform details
