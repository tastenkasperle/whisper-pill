"""
whisper_pill.core.hardware
--------------------------
Hardware topology inspection and optimal thread allocation heuristics
for CTranslate2 / faster-whisper inference on modern hybrid and standard CPUs.
"""

from __future__ import annotations
import os
import platform
from dataclasses import dataclass


@dataclass(frozen=True)
class HardwareProfile:
    total_logical_cores: int
    optimal_threads: int
    cpu_architecture: str
    is_hybrid_architecture: bool
    description: str


def detect_optimal_hardware() -> HardwareProfile:
    """
    Analyzes host CPU topology and determines the optimal thread configuration
    for int8 CTranslate2 inference.
    
    Heuristic:
    - Intel 12th/13th/14th Gen Hybrid CPUs (e.g. i5-13500H: 6 P-Cores / 8 E-Cores / 20 Threads):
      Allocating threads to match the P-Core virtual execution capacity (e.g. 12 threads)
      prevents thread contention, cache thrashing, and unwanted E-Core spillover.
    - Standard symmetric CPUs (AMD Ryzen, Apple Silicon, older Intel):
      Uses physical core count or 75% of logical cores to reserve headroom for OS & GUI.
    """
    logical = os.cpu_count() or 4
    proc_desc = platform.processor() or ""
    machine = platform.machine() or ""
    
    is_hybrid = False
    
    # Intel Raptor Lake / Alder Lake heuristic detection
    # Common signature on Windows: Intel64 Family 6 Model 186/154/183 etc.
    if "Intel" in proc_desc or "Intel64" in proc_desc:
        if logical >= 16:  # Strong indicator of Hybrid (e.g. 14C/20T or 16C/24T)
            is_hybrid = True
            optimal = min(12, logical)
            desc = f"Intel Hybrid CPU detected ({logical} threads) -> Bound to 12 P-Core threads."
        elif logical >= 12:
            is_hybrid = True
            optimal = min(8, logical)
            desc = f"Intel Hybrid CPU detected ({logical} threads) -> Bound to 8 P-Core threads."
        else:
            optimal = max(2, logical - 1)
            desc = f"Intel Standard CPU ({logical} threads) -> Allocated {optimal} threads."
    elif "AMD" in proc_desc or "AuthenticAMD" in proc_desc:
        # AMD Symmetric multi-processing (Zen 3/4/5)
        # Typically SMT allows logical // 2 physical cores, or up to 8 threads for int8
        optimal = min(8, max(2, logical // 2 if logical > 4 else logical))
        desc = f"AMD Zen Architecture ({logical} threads) -> SMT-balanced to {optimal} threads."
    else:
        # Fallback
        optimal = min(12, max(2, logical - 1)) if logical > 4 else logical
        desc = f"Generic Architecture ({machine}, {logical} threads) -> Allocated {optimal} threads."

    return HardwareProfile(
        total_logical_cores=logical,
        optimal_threads=optimal,
        cpu_architecture=f"{proc_desc} ({machine})",
        is_hybrid_architecture=is_hybrid,
        description=desc
    )
