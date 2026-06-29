# Causal Attributions and JVM Metric Correlations

Below is the Pearson / Spearman rank correlation matrix computed across all campaign runs. Each cell contains `Pearson (Spearman)` coefficients.

| Metric | Engine Latency (ms) | Heap Allocations (MB) | Queue Growth (States) | GC Cycles | TypeCG Density |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Engine Latency (ms)** | 1.000 (1.000) | 0.939 (0.844) | 0.559 (0.358) | 0.899 (0.533) | 0.333 (0.692) |
| **Heap Allocations (MB)** | 0.939 (0.844) | 1.000 (1.000) | 0.480 (0.474) | 0.913 (0.537) | 0.205 (0.566) |
| **Queue Growth (States)** | 0.559 (0.358) | 0.480 (0.474) | 1.000 (1.000) | 0.331 (0.359) | -0.085 (0.156) |
| **GC Cycles** | 0.899 (0.533) | 0.913 (0.537) | 0.331 (0.359) | 1.000 (1.000) | 0.216 (0.520) |
| **TypeCG Density** | 0.333 (0.692) | 0.205 (0.566) | -0.085 (0.156) | 0.216 (0.520) | 1.000 (1.000) |
