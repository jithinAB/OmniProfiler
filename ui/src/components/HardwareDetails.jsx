import React, { useState } from 'react';
import { Cpu, ChevronDown, ChevronUp } from 'lucide-react';
import { formatBytes } from '../utils/formatters';
import './HardwareDetails.css';

const HardwareDetails = ({ hardware }) => {
    const [expanded, setExpanded] = useState(false);

    if (!hardware) return null;

    const {
        cpu_brand, cpu_frequency_max, cpu_physical_cores, cpu_logical_cores,
        cache_l1_data, cache_l1_instruction, cache_l2, cache_l3,
        ram_total, memory_type, memory_speed,
        os_info, os_version,
        theoretical_cpu_gflops,
        gpu_info
    } = hardware;

    return (
        <div className="hardware-details">
            <div className="hardware-header" onClick={() => setExpanded(!expanded)}>
                <div className="hardware-title">
                    <Cpu color="#10b981" size={20} />
                    <h4>Hardware Specifications</h4>
                </div>
                {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </div>

            {expanded && (
                <div className="hardware-content">
                    {/* CPU Section */}
                    <div className="hw-section">
                        <h5>Processor</h5>
                        <div className="hw-grid">
                            <div className="hw-item" title="CPU model and brand. This is your processor's identification.">
                                <span className="hw-label">Model</span>
                                <span className="hw-value">{cpu_brand || 'Unknown'}</span>
                            </div>
                            <div className="hw-item" title="Maximum CPU clock speed in GHz. Higher frequency = faster single-threaded performance.">
                                <span className="hw-label">Frequency</span>
                                <span className="hw-value">{cpu_frequency_max ? `${cpu_frequency_max.toFixed(2)} GHz` : 'N/A'}</span>
                            </div>
                            <div className="hw-item" title="Physical cores are actual CPU cores. Logical cores include hyper-threading. More cores = better multi-tasking.">
                                <span className="hw-label">Cores</span>
                                <span className="hw-value">{cpu_physical_cores} physical, {cpu_logical_cores} logical</span>
                            </div>
                            <div className="hw-item" title="Theoretical maximum floating-point operations per second. Higher = more computational power. This is a theoretical peak, not actual performance.">
                                <span className="hw-label">Theoretical GFLOPs</span>
                                <span className="hw-value">{theoretical_cpu_gflops ? theoretical_cpu_gflops.toFixed(2) : 'N/A'}</span>
                            </div>
                        </div>
                    </div>

                    {/* Cache Section */}
                    {(cache_l1_data > 0 || cache_l2 > 0 || cache_l3 > 0) && (
                        <div className="hw-section">
                            <h5>Cache</h5>
                            <div className="hw-grid">
                                {cache_l1_data > 0 && (
                                    <div className="hw-item" title="L1 Data Cache: Fastest, smallest cache for data. Larger = better for data-intensive operations.">
                                        <span className="hw-label">L1 Data</span>
                                        <span className="hw-value">{formatBytes(cache_l1_data)}</span>
                                    </div>
                                )}
                                {cache_l1_instruction > 0 && (
                                    <div className="hw-item" title="L1 Instruction Cache: Fastest cache for program instructions. Larger = better for complex code.">
                                        <span className="hw-label">L1 Instruction</span>
                                        <span className="hw-value">{formatBytes(cache_l1_instruction)}</span>
                                    </div>
                                )}
                                {cache_l2 > 0 && (
                                    <div className="hw-item" title="L2 Cache: Medium speed cache, shared between cores. Larger = better overall performance.">
                                        <span className="hw-label">L2</span>
                                        <span className="hw-value">{formatBytes(cache_l2)}</span>
                                    </div>
                                )}
                                {cache_l3 > 0 && (
                                    <div className="hw-item" title="L3 Cache: Largest, slowest cache, shared across all cores. Larger = better for multi-threaded workloads.">
                                        <span className="hw-label">L3</span>
                                        <span className="hw-value">{formatBytes(cache_l3)}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Memory Section */}
                    <div className="hw-section">
                        <h5>Memory</h5>
                        <div className="hw-grid">
                            <div className="hw-item" title="Total system RAM. More RAM = can handle larger datasets and more programs simultaneously.">
                                <span className="hw-label">Total RAM</span>
                                <span className="hw-value">{formatBytes(ram_total)}</span>
                            </div>
                            {memory_type && memory_type !== 'Unknown' && (
                                <div className="hw-item" title="Memory technology type. DDR5 > DDR4 > DDR3 in terms of speed and efficiency.">
                                    <span className="hw-label">Type</span>
                                    <span className="hw-value">{memory_type}</span>
                                </div>
                            )}
                            {memory_speed > 0 && (
                                <div className="hw-item" title="Memory clock speed in MHz. Higher = faster data transfer between RAM and CPU.">
                                    <span className="hw-label">Speed</span>
                                    <span className="hw-value">{memory_speed} MHz</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* GPU Section */}
                    {gpu_info && gpu_info.length > 0 && (
                        <div className="hw-section">
                            <h5>GPU / Accelerator</h5>
                            {gpu_info.map((gpu, idx) => (
                                <div key={idx} className="hw-grid gpu-info">
                                    <div className="hw-item" title="Graphics Processing Unit model. Used for parallel computing and graphics rendering.">
                                        <span className="hw-label">Model</span>
                                        <span className="hw-value">{gpu.name}</span>
                                    </div>
                                    {gpu.memory_total && (
                                        <div className="hw-item" title="Video RAM (vRAM): GPU's dedicated memory. More vRAM = can handle larger models and datasets.">
                                            <span className="hw-label">vRAM</span>
                                            <span className="hw-value">{formatBytes(gpu.memory_total)}</span>
                                        </div>
                                    )}
                                    {gpu.compute_capability && (
                                        <div className="hw-item" title="NVIDIA Compute Capability version. Higher = newer architecture with more features. 7.0+ supports Tensor Cores.">
                                            <span className="hw-label">Compute Capability</span>
                                            <span className="hw-value">{gpu.compute_capability}</span>
                                        </div>
                                    )}
                                    {gpu.clock_ghz > 0 && (
                                        <div className="hw-item" title="GPU clock speed in GHz. Higher = faster GPU processing.">
                                            <span className="hw-label">Clock Speed</span>
                                            <span className="hw-value">{gpu.clock_ghz.toFixed(2)} GHz</span>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* OS Section */}
                    <div className="hw-section">
                        <h5>Operating System</h5>
                        <div className="hw-grid">
                            <div className="hw-item" title="Operating system platform (Windows, macOS, Linux).">
                                <span className="hw-label">OS</span>
                                <span className="hw-value">{os_info || 'Unknown'}</span>
                            </div>
                            <div className="hw-item" title="Operating system version. Newer versions may have performance improvements.">
                                <span className="hw-label">Version</span>
                                <span className="hw-value">{os_version || 'Unknown'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default HardwareDetails;
