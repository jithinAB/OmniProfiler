from code.profiler.hardware import HardwareDetector
import json

print("Testing Enhanced Hardware Detection\n" + "="*50)

detector = HardwareDetector()
info = detector.detect()

# Convert to dict for display
info_dict = info.__dict__

print(json.dumps(info_dict, indent=2, default=str))

print("\n" + "="*50)
print("Summary:")
print(f"CPU: {info.cpu_brand} @ {info.cpu_frequency_max} GHz")
print(f"Cores: {info.cpu_physical_cores} physical, {info.cpu_logical_cores} logical")
print(f"Cache: L1D={info.cache_l1_data/1024:.0f}KB, L2={info.cache_l2/1024:.0f}KB, L3={info.cache_l3/1024/1024:.1f}MB")
print(f"RAM: {info.ram_total/1024/1024/1024:.1f} GB ({info.memory_type} @ {info.memory_speed} MHz)")
print(f"OS: {info.os_info} {info.os_version}")
print(f"Theoretical CPU GFLOPs: {info.theoretical_cpu_gflops:.2f}")
if info.gpu_info:
    for gpu in info.gpu_info:
        print(f"GPU: {gpu['name']} ({gpu.get('memory_total', 0)/1024/1024/1024:.1f} GB vRAM)")
