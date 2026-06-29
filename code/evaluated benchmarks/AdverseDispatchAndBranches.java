package research;

public class AdverseDispatchAndBranches {

  interface Operation {
    int compute(int x);
  }

  static class AddOp implements Operation {
    public int compute(int x) { return x + 1; }
  }

  static class SubOp implements Operation {
    public int compute(int x) { return x - 1; }
  }

  static class MulOp implements Operation {
    public int compute(int x) { return x * 2; }
  }

  static class DivOp implements Operation {
    public int compute(int x) { return x / 2; }
  }

  public static int runAdverse(int type1, int selector, int val, int x) {
    int res = 0;

    // Competing branches:
    if (type1 == 0) {
      // BRANCH A: Highly Polymorphic Dispatch (4 choices), carrying HIGH utility (nested branches!)
      Operation op;
      if (selector == 0) {
        op = new AddOp();
      } else if (selector == 1) {
        op = new SubOp();
      } else if (selector == 2) {
        op = new MulOp();
      } else {
        op = new DivOp();
      }
      res += op.compute(x); // High cost
      
      // Sub-branches inside the expensive path
      if (res > 10) {
        res += 5;
      } else if (res > 5) {
        res += 2;
      } else if (res > 0) {
        res += 1;
      } else {
        res -= 1;
      }
      
    } else {
      // BRANCH B: Cheap Branching, but dead-ends / low utility
      if (val == 0) {
        res += x + 2;
      } else {
        res += x - 2;
      }
      if (res > 100) {
        return 1; // Dead-end
      }
    }

    if (res > 5) {
      return 2;
    }
    return -1;
  }

  // Regime 1: Cheap High Utility
  public static int runCheapHighUtility(int type1, int selector, int val, int x) {
    int res = 0;
    if (type1 == 0) {
      res += x + selector; 
      if (res > 10) {
        res += 5;
      } else if (res > 5) {
        res += 2;
      } else if (res > 0) {
        res += 1;
      } else {
        res -= 1;
      }
    } else {
      res += x + val;
    }
    return res;
  }

  // Regime 2: Balanced Cost Utility
  public static int runBalancedCostUtility(int type1, int selector, int val, int x) {
    return runAdverse(type1, selector, val, x);
  }

  // Regime 3: Expensive High Utility
  public static int runExpensiveHighUtility(int type1, int selector, int val, int x) {
    int res = 0;
    if (type1 == 0) {
      Operation op1 = (selector == 0) ? new AddOp() : new SubOp();
      Operation op2 = (val == 0) ? new MulOp() : new DivOp();
      res += op1.compute(x) + op2.compute(x);
      
      if (res > 20) {
        res += 10;
      } else if (res > 10) {
        res += 5;
      } else if (res > 0) {
        res += 2;
      } else {
        res -= 2;
      }
    } else {
      res += x - val;
    }
    return res;
  }

  public static void main(String[] args) {
    runAdverse(0, 0, 0, 10);
  }
}
