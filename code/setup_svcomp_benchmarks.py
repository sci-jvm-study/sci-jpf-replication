import os

workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Define the Java source code for the 16 SV-COMP exception cases
java_code = """package research;

class ExCaseA extends Throwable { int val = 1; }
class ExCaseB extends ExCaseA { ExCaseB() { val = 2; } }
class ExCaseC extends ExCaseB { ExCaseC() { val = 3; } }
class ExCaseD extends ExCaseC { ExCaseD() { val = 4; } }

class ExCaseRA extends RuntimeException { int val = 1; }
class ExCaseRB extends ExCaseRA { ExCaseRB() { val = 2; } }
class ExCaseRC extends ExCaseRB { ExCaseRC() { val = 3; } }

public class OpenSourceExceptionCases {

    private static int sink(int state) {
        return state > 0 ? 1 : -1;
    }

    // EX1: exception scoping & nesting
    public static int exceptions1RealStyle(int selector) {
        int state = 0;
        try {
            ExCaseD d = new ExCaseD();
            ExCaseC c = new ExCaseC();
            if (d == null || c == null) state = -1;
            if (selector == 3) throw d;
            else if (selector == 2) throw c;
            else throw new ExCaseA();
        } catch (ExCaseD exc) {
            state = 4000;
        } catch (ExCaseC exc) {
            state = 3000;
        } catch (ExCaseA exc) {
            state = 1000;
        }
        return sink(state);
    }

    public static int exceptions1BranchControl(int selector) {
        int state;
        if (selector == 3) state = 4000;
        else if (selector == 2) state = 3000;
        else state = 1000;
        return sink(state);
    }

    // EX2: throw subclass, catch ordering
    public static int exceptions2RealStyle(int selector) {
        int state = 0;
        try {
            if (selector == 1) throw new ExCaseB();
            else if (selector == 2) throw new ExCaseC();
        } catch (ExCaseC exc) {
            state = 20;
        } catch (ExCaseB exc) {
            state = 10;
        } catch (ExCaseA exc) {
            state = 5;
        }
        return sink(state);
    }

    public static int exceptions2BranchControl(int selector) {
        int state;
        if (selector == 2) state = 20;
        else if (selector == 1) state = 10;
        else state = 5;
        return sink(state);
    }

    // EX3: throw inline in block
    public static int exceptions3RealStyle(int selector) {
        int state = 0;
        try {
            if (selector == 1) {
                ExCaseB b = new ExCaseB();
                throw b;
            }
        } catch (ExCaseC exc) {
            state = 20;
        } catch (ExCaseB exc) {
            state = 10;
        }
        return sink(state);
    }

    public static int exceptions3BranchControl(int selector) {
        int state;
        if (selector == 1) state = 10;
        else state = 0;
        return sink(state);
    }

    // EX4: exception assert failure bypass
    public static int exceptions4RealStyle(int selector) {
        int state = 0;
        try {
            if (selector == 1) throw new ExCaseB();
        } catch (ExCaseC exc) {
            state = -1;
        } catch (ExCaseB exc) {
            state = 10;
        }
        return sink(state);
    }

    public static int exceptions4BranchControl(int selector) {
        int state;
        if (selector == 1) state = 10;
        else state = 0;
        return sink(state);
    }

    // EX5: throw runtime hierarchy
    public static int exceptions5RealStyle(int selector) {
        int state = 0;
        try {
            if (selector == 3) throw new ExCaseRC();
            else if (selector == 2) throw new ExCaseRB();
            else throw new ExCaseRA();
        } catch (ExCaseRC exc) {
            state = 40;
        } catch (ExCaseRB exc) {
            state = 30;
        } catch (ExCaseRA exc) {
            state = 10;
        }
        return sink(state);
    }

    public static int exceptions5BranchControl(int selector) {
        int state;
        if (selector == 3) state = 40;
        else if (selector == 2) state = 30;
        else state = 10;
        return sink(state);
    }

    // EX6: catch nested fields
    public static int exceptions6RealStyle(int selector) {
        int state = 0;
        try {
            if (selector == 1) throw new ExCaseRB();
        } catch (ExCaseRB exc) {
            state = exc.val * 10;
        } catch (ExCaseRA exc) {
            state = exc.val * 5;
        }
        return sink(state);
    }

    public static int exceptions6BranchControl(int selector) {
        int state;
        if (selector == 1) state = 20;
        else state = 0;
        return sink(state);
    }

    // EX7: catch rethrow propagation
    public static int exceptions7RealStyle(int selector) {
        int state = 0;
        try {
            try {
                if (selector == 2) throw new ExCaseRC();
                else if (selector == 1) throw new ExCaseRB();
                state = 1;
            } catch (ExCaseRC exc) {
                state = 100;
            } catch (ExCaseRB exc) {
                throw exc;
            }
        } catch (ExCaseRB exc) {
            state = 200;
        }
        return sink(state);
    }

    public static int exceptions7BranchControl(int selector) {
        int state;
        if (selector == 2) state = 100;
        else if (selector == 1) state = 200;
        else state = 1;
        return sink(state);
    }

    // EX9: nested runtime exception frame
    private static void foo9(int selector) {
        if (selector == 1) throw new ExCaseRB();
    }

    public static int exceptions9RealStyle(int selector) {
        int state = 0;
        try {
            foo9(selector);
            state = 1;
        } catch (ExCaseRB exc) {
            state = 200;
        }
        return sink(state);
    }

    public static int exceptions9BranchControl(int selector) {
        int state;
        if (selector == 1) state = 200;
        else state = 1;
        return sink(state);
    }

    // EX10: double nested propagation
    private static void foo10(int selector) {
        try {
            if (selector == 1) throw new ExCaseRA();
        } catch (ExCaseRB exc) {
            // bypass
        }
    }

    public static int exceptions10RealStyle(int selector) {
        int state = 0;
        try {
            foo10(selector);
            state = 1;
        } catch (ExCaseRA exc) {
            state = 300;
        }
        return sink(state);
    }

    public static int exceptions10BranchControl(int selector) {
        int state;
        if (selector == 1) state = 300;
        else state = 1;
        return sink(state);
    }

    // EX11: dynamic exception values
    private static void foo11(int selector) {
        if (selector == 1) throw new ExCaseRB();
        else throw new ExCaseRA();
    }

    public static int exceptions11RealStyle(int selector) {
        int state = 0;
        try {
            foo11(selector);
            state = 1;
        } catch (ExCaseRB exc) {
            state = exc.val * 100;
        } catch (ExCaseRA exc) {
            state = exc.val * 50;
        }
        return sink(state);
    }

    public static int exceptions11BranchControl(int selector) {
        int state;
        if (selector == 1) state = 200;
        else state = 50;
        return sink(state);
    }

    // EX12: type-matched deep handler
    private static void foo12(int selector) {
        if (selector == 1) throw new ExCaseRA();
    }

    public static int exceptions12RealStyle(int selector) {
        int state = 0;
        try {
            foo12(selector);
            state = 1;
        } catch (ExCaseRA exc) {
            state = 120;
        }
        return sink(state);
    }

    public static int exceptions12BranchControl(int selector) {
        int state;
        if (selector == 1) state = 120;
        else state = 1;
        return sink(state);
    }

    // EX13: sub-scoping handler
    private static void foo13(int selector) {
        try {
            if (selector == 1) throw new ExCaseRB();
        } catch (ExCaseRC exc) {
            // bypass
        }
    }

    public static int exceptions13RealStyle(int selector) {
        int state = 0;
        try {
            foo13(selector);
            state = 1;
        } catch (ExCaseRB exc) {
            state = 130;
        }
        return sink(state);
    }

    public static int exceptions13BranchControl(int selector) {
        int state;
        if (selector == 1) state = 130;
        else state = 1;
        return sink(state);
    }

    // EX14: dynamic rethrow
    private static void foo14(int selector) {
        try {
            if (selector == 1) throw new ExCaseRA();
        } catch (ExCaseRA exc) {
            throw exc;
        }
    }

    public static int exceptions14RealStyle(int selector) {
        int state = 0;
        try {
            foo14(selector);
            state = 1;
        } catch (ExCaseRA exc) {
            state = 140;
        }
        return sink(state);
    }

    public static int exceptions14BranchControl(int selector) {
        int state;
        if (selector == 1) state = 140;
        else state = 1;
        return sink(state);
    }

    // EX15: multi-site propagation
    private static void foo15(int selector) {
        if (selector == 1) throw new ExCaseRA();
    }

    public static int exceptions15RealStyle(int selector) {
        int state = 0;
        try {
            foo15(selector);
            state = 1;
        } catch (ExCaseRB exc) {
            state = 150;
        } catch (ExCaseRA exc) {
            state = 155;
        }
        return sink(state);
    }

    public static int exceptions15BranchControl(int selector) {
        int state;
        if (selector == 1) state = 155;
        else state = 1;
        return sink(state);
    }

    // EX16: exception-driven state exit
    public static int exceptions16RealStyle(int selector) {
        int state = 0;
        try {
            if (selector == 1) throw new ExCaseRA();
            state = 160;
        } catch (ExCaseRA exc) {
            state = 165;
        }
        return sink(state);
    }

    public static int exceptions16BranchControl(int selector) {
        int state;
        if (selector == 1) state = 165;
        else state = 160;
        return sink(state);
    }

    // EX18: simple throw caught by parent class handler
    private static void foo18(int selector) {
        if (selector == 1) throw new ExCaseRB();
    }

    public static int exceptions18RealStyle(int selector) {
        int state = 0;
        try {
            foo18(selector);
            state = 1;
        } catch (ExCaseRC exc) {
            state = 200;
        } catch (ExCaseRA exc) {
            state = 300;
        }
        return sink(state);
    }

    public static int exceptions18BranchControl(int selector) {
        int state;
        if (selector == 1) state = 300;
        else state = 1;
        return sink(state);
    }

    public static void main(String[] args) {
        exceptions1RealStyle(0);
        exceptions1BranchControl(0);
        exceptions2RealStyle(0);
        exceptions2BranchControl(0);
        exceptions3RealStyle(0);
        exceptions3BranchControl(0);
        exceptions4RealStyle(0);
        exceptions4BranchControl(0);
        exceptions5RealStyle(0);
        exceptions5BranchControl(0);
        exceptions6RealStyle(0);
        exceptions6BranchControl(0);
        exceptions7RealStyle(0);
        exceptions7BranchControl(0);
        exceptions9RealStyle(0);
        exceptions9BranchControl(0);
        exceptions10RealStyle(0);
        exceptions10BranchControl(0);
        exceptions11RealStyle(0);
        exceptions11BranchControl(0);
        exceptions12RealStyle(0);
        exceptions12BranchControl(0);
        exceptions13RealStyle(0);
        exceptions13BranchControl(0);
        exceptions14RealStyle(0);
        exceptions14BranchControl(0);
        exceptions15RealStyle(0);
        exceptions15BranchControl(0);
        exceptions16RealStyle(0);
        exceptions16BranchControl(0);
        exceptions18RealStyle(0);
        exceptions18BranchControl(0);
    }
}
"""

# Write java file
java_path = os.path.join(workspace, "jpf-symbc", "src", "examples", "research", "OpenSourceExceptionCases.java")
with open(java_path, "w", encoding="utf-8") as f:
    f.write(java_code)
print("Updated OpenSourceExceptionCases.java")

# Generate all 16 Real JPF configuration files
cases = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 18]

for case in cases:
    for variant in ["realstyle", "branchcontrol"]:
        jpf_name = f"real-exceptions{case}-{variant}.jpf"
        jpf_path = os.path.join(workspace, "jpf-symbc", "src", "examples", "research", jpf_name)
        
        realstyle_flag = "true" if variant == "realstyle" else "false"
        symbolic_method = f"research.OpenSourceExceptionCases.exceptions{case}RealStyle(sym)" if variant == "realstyle" else f"research.OpenSourceExceptionCases.exceptions{case}BranchControl(sym)"
        method_label = f"research.OpenSourceExceptionCases.exceptions{case}RealStyle" if variant == "realstyle" else f"research.OpenSourceExceptionCases.exceptions{case}BranchControl"
        
        jpf_content = f"""target=research.OpenSourceExceptionCases
classpath=${{jpf-symbc}}/build/examples
sourcepath=${{jpf-symbc}}/src/examples
symbolic.method={symbolic_method}
symbolic.dp=z3
listener=gov.nasa.jpf.symbc.ResearchDataListener
search.class=gov.nasa.jpf.search.DFSearch
vm.storage.class=nil
search.multiple_errors=true
symbolic.min_int=0
symbolic.max_int=3
research.benchmark=real-exceptions{case}-{variant}
research.method_label={method_label}
research.has_exception=true
research.has_loop=false
research.has_division=false
research.has_nested_branch=true
research.has_dispatch=false
"""
        with open(jpf_path, "w", encoding="utf-8") as f:
            f.write(jpf_content)
        # print(f"Generated {jpf_name}")

print("All 16 JPF configurations generated.")
