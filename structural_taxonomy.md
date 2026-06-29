# Control-Flow and JVM Feature Taxonomy

This document provides the full structural taxonomy of the evaluated JVM symbolic execution workloads under a linear-integer SMT baseline, as described in Section IV-A (Table III / `tab:taxonomy`) of the paper.

| Category Group | Benchmark Name | Workload Type | Primary JVM Features | Loops | Max Depth | Symbolic Vars | Explored States | SMT Complexity |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Category 1: Dynamic-Dispatch Heavy Synthetic** | `DispatchFamily` | Synthetic | Dynamic Dispatch, `TypeCG` | Yes | 6 | 2 | 1,457 | Linear Integer |
| | `mixed-dispatch-branches` | Synthetic | Mixed polymorphism and branching | No | 6 | 4 | 200 | Linear Integer |
| | `adverse-dispatch-branches` | Synthetic | Pathological dispatch cost-utility | No | 6 | 4 | 200 | Linear Integer |
| **Category 2: Exception Heavy** | `ExceptionFamily` | Synthetic | Catch unwinding, Exception table | No | 6 | 2 | 728 | Linear Integer |
| **Category 3: SV-COMP Suite** | `real-factories` | SV-COMP | Dynamic class loading, Polymorphism | No | 3 | 1 | 1,457 | Linear Integer |
| | `real-exceptions` | SV-COMP | Recursive frame unwinding, try-catch | No | 4 | 1 | 728 | Linear Integer |
| **Category 4: Algorithmic Workloads** | `TreeMapSimple` | Collections | Red-Black Tree Insertion, References | Yes | 4 | 5 | 396 | Linear Integer |
| | `DecisionGraph` | Decision-graph | Highly nested branch conditions | No | 3 | 10 | 502 | Linear Integer |
| **Category 5: Real-World Libraries** | `real-jsonparser` | Real-World | Object-heavy JSON parser, dispatches | Yes | 4 | 4 | 500 | Linear Integer |
| | `real-expressionevaluator` | Real-World | Polymorphic AST expression evaluation | No | 5 | 5 | 500 | Linear Integer |
| | `real-configresolver` | Real-World | Configuration dependency resolution | Yes | 6 | 8 | 500 | Linear Integer |
| | `guava-immutablelist` | Guava Lib | Object-heavy collection utility, polymorphism | Yes | 12 | 15 | 10,000 | Linear Integer |
| | `commons-complex` | Commons Math | Complex arithmetic, deep execution branch | Yes | 8 | 12 | 5,000 | Linear Integer |
