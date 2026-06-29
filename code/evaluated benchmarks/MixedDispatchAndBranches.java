package research;

public class MixedDispatchAndBranches {

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

  public static int runMixed(int type1, int selector, int val, int x) {
    int res = 0;

    // Competing branches:
    if (type1 == 0) {
      // BRANCH A: Highly Polymorphic Dispatch (4 choices), but dead-ends / low utility
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
      res += op.compute(x); // High cost, moderate utility (only a few leaves)
      if (res > 100) {
        return 1; // Unreachable/dead-end
      }
      
    } else {
      // BRANCH B: Cheap Branching, but high utility (lots of reachable branch leaves!)
      if (val == 0) {
        res += x + 2;
      } else if (val == 1) {
        res += x - 2;
      } else if (val == 2) {
        res += x * 3;
      } else {
        res += x - 5;
      }
      
      // Nested branch options:
      if (res > 0) {
        res += 1;
      } else {
        res -= 1;
      }
    }

    if (res > 5) {
      return 2;
    }
    return -1;
  }

  public static void main(String[] args) {
    runMixed(0, 0, 0, 10);
  }
}
