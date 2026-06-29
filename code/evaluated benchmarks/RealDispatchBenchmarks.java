package research;

public class RealDispatchBenchmarks {

  private static final int INVALID_SCORE = -100;

  interface ItemFactory {
    Item create(int selector, int payload);
  }

  static abstract class Item {
    abstract int score();
  }

  static class AItem extends Item {
    private final int v;

    AItem(int v) {
      this.v = v;
    }

    int score() {
      return v + 3;
    }
  }

  static class ZeroItem extends Item {
    private final int v;

    ZeroItem(int v) {
      this.v = v;
    }

    int score() {
      return v + 1;
    }
  }

  static class BItem extends Item {
    private final int v;

    BItem(int v) {
      this.v = v;
    }

    int score() {
      return v - 2;
    }
  }

  static class CItem extends Item {
    private final int x;
    private final int y;

    CItem(int x, int y) {
      this.x = x;
      this.y = y;
    }

    int score() {
      return x + y;
    }
  }

  static class AFactory implements ItemFactory {
    public Item create(int selector, int payload) {
      if (selector == 0) {
        return new ZeroItem(payload);
      }
      return null;
    }
  }

  static class BFactory implements ItemFactory {
    public Item create(int selector, int payload) {
      if (selector == 1) {
        return new AItem(payload);
      }
      return null;
    }
  }

  static class CFactory implements ItemFactory {
    public Item create(int selector, int payload) {
      if (selector == 2) {
        return new BItem(payload);
      }
      return null;
    }
  }

  static class DFactory implements ItemFactory {
    public Item create(int selector, int payload) {
      if (selector == 3) {
        return new CItem(payload, selector);
      }
      return null;
    }
  }

  static class AnyFactory implements ItemFactory {
    public Item create(int selector, int payload) {
      if (selector == 0) {
        return new AFactory().create(selector, payload);
      } else if (selector == 1) {
        return new BFactory().create(selector, payload);
      } else if (selector == 2) {
        return new CFactory().create(selector, payload);
      } else if (selector == 3) {
        return new DFactory().create(selector, payload);
      }
      return null;
    }
  }

  public static int factoriesRealStyle(int selector, int payload) {
    Item item = new AnyFactory().create(selector, payload);
    int score;
    if (item == null) {
      score = INVALID_SCORE;
    } else {
      score = item.score();
    }

    if (score > 0) {
      return 1;
    }
    return -1;
  }

  public static int factoriesBranchControl(int selector, int payload) {
    int score;
    if (selector == 1) {
      score = payload + 3;
    } else if (selector == 2) {
      score = payload - 2;
    } else if (selector == 3) {
      score = payload + selector;
    } else {
      score = INVALID_SCORE;
    }

    if (score > 0) {
      return 1;
    }
    return -1;
  }

  private static int scoreRealStyleStep(int selector, int payload) {
    Item item = new AnyFactory().create(selector, payload);
    if (item == null) {
      return INVALID_SCORE;
    }
    return item.score();
  }

  private static int scoreBranchControlStep(int selector, int payload) {
    if (selector == 0) {
      return payload + 1;
    } else if (selector == 1) {
      return payload + 3;
    } else if (selector == 2) {
      return payload - 2;
    }
    return INVALID_SCORE;
  }

  private static int classify(int total) {
    if (total > 0) {
      return 1;
    }
    return -1;
  }

  public static int factoriesDepth1RealStyle(int s1, int payload) {
    int total = scoreRealStyleStep(s1, payload);
    return classify(total);
  }

  public static int factoriesDepth1BranchControl(int s1, int payload) {
    int total = scoreBranchControlStep(s1, payload);
    return classify(total);
  }

  public static int factoriesDepth2RealStyle(int s1, int s2, int payload) {
    int total = 0;
    total += scoreRealStyleStep(s1, payload);
    total += scoreRealStyleStep(s2, payload + 1);
    return classify(total);
  }

  public static int factoriesDepth2BranchControl(int s1, int s2, int payload) {
    int total = 0;
    total += scoreBranchControlStep(s1, payload);
    total += scoreBranchControlStep(s2, payload + 1);
    return classify(total);
  }

  public static int factoriesDepth4RealStyle(int s1, int s2, int s3, int s4, int payload) {
    int total = 0;
    total += scoreRealStyleStep(s1, payload);
    total += scoreRealStyleStep(s2, payload + 1);
    total += scoreRealStyleStep(s3, payload + 2);
    total += scoreRealStyleStep(s4, payload + 3);
    return classify(total);
  }

  public static int factoriesDepth4BranchControl(int s1, int s2, int s3, int s4, int payload) {
    int total = 0;
    total += scoreBranchControlStep(s1, payload);
    total += scoreBranchControlStep(s2, payload + 1);
    total += scoreBranchControlStep(s3, payload + 2);
    total += scoreBranchControlStep(s4, payload + 3);
    return classify(total);
  }

  public static int factoriesDepth6RealStyle(
      int s1,
      int s2,
      int s3,
      int s4,
      int s5,
      int s6,
      int payload) {
    int total = 0;
    total += scoreRealStyleStep(s1, payload);
    total += scoreRealStyleStep(s2, payload + 1);
    total += scoreRealStyleStep(s3, payload + 2);
    total += scoreRealStyleStep(s4, payload + 3);
    total += scoreRealStyleStep(s5, payload + 4);
    total += scoreRealStyleStep(s6, payload + 5);
    return classify(total);
  }

  public static int factoriesDepth6BranchControl(
      int s1,
      int s2,
      int s3,
      int s4,
      int s5,
      int s6,
      int payload) {
    int total = 0;
    total += scoreBranchControlStep(s1, payload);
    total += scoreBranchControlStep(s2, payload + 1);
    total += scoreBranchControlStep(s3, payload + 2);
    total += scoreBranchControlStep(s4, payload + 3);
    total += scoreBranchControlStep(s5, payload + 4);
    total += scoreBranchControlStep(s6, payload + 5);
    return classify(total);
  }

  public static int factoriesDepth8RealStyle(
      int s1,
      int s2,
      int s3,
      int s4,
      int s5,
      int s6,
      int s7,
      int s8,
      int payload) {
    int total = 0;
    total += scoreRealStyleStep(s1, payload);
    total += scoreRealStyleStep(s2, payload + 1);
    total += scoreRealStyleStep(s3, payload + 2);
    total += scoreRealStyleStep(s4, payload + 3);
    total += scoreRealStyleStep(s5, payload + 4);
    total += scoreRealStyleStep(s6, payload + 5);
    total += scoreRealStyleStep(s7, payload + 6);
    total += scoreRealStyleStep(s8, payload + 7);
    return classify(total);
  }

  public static int factoriesDepth8BranchControl(
      int s1,
      int s2,
      int s3,
      int s4,
      int s5,
      int s6,
      int s7,
      int s8,
      int payload) {
    int total = 0;
    total += scoreBranchControlStep(s1, payload);
    total += scoreBranchControlStep(s2, payload + 1);
    total += scoreBranchControlStep(s3, payload + 2);
    total += scoreBranchControlStep(s4, payload + 3);
    total += scoreBranchControlStep(s5, payload + 4);
    total += scoreBranchControlStep(s6, payload + 5);
    total += scoreBranchControlStep(s7, payload + 6);
    total += scoreBranchControlStep(s8, payload + 7);
    return classify(total);
  }

  public static int factoriesDepth10RealStyle(
      int s1, int s2, int s3, int s4, int s5, int s6, int s7, int s8, int s9, int s10,
      int payload) {
    int total = 0;
    total += scoreRealStyleStep(s1, payload);
    total += scoreRealStyleStep(s2, payload + 1);
    total += scoreRealStyleStep(s3, payload + 2);
    total += scoreRealStyleStep(s4, payload + 3);
    total += scoreRealStyleStep(s5, payload + 4);
    total += scoreRealStyleStep(s6, payload + 5);
    total += scoreRealStyleStep(s7, payload + 6);
    total += scoreRealStyleStep(s8, payload + 7);
    total += scoreRealStyleStep(s9, payload + 8);
    total += scoreRealStyleStep(s10, payload + 9);
    return classify(total);
  }

  public static int factoriesDepth10BranchControl(
      int s1, int s2, int s3, int s4, int s5, int s6, int s7, int s8, int s9, int s10,
      int payload) {
    int total = 0;
    total += scoreBranchControlStep(s1, payload);
    total += scoreBranchControlStep(s2, payload + 1);
    total += scoreBranchControlStep(s3, payload + 2);
    total += scoreBranchControlStep(s4, payload + 3);
    total += scoreBranchControlStep(s5, payload + 4);
    total += scoreBranchControlStep(s6, payload + 5);
    total += scoreBranchControlStep(s7, payload + 6);
    total += scoreBranchControlStep(s8, payload + 7);
    total += scoreBranchControlStep(s9, payload + 8);
    total += scoreBranchControlStep(s10, payload + 9);
    return classify(total);
  }

  public static int factoriesDepth12RealStyle(
      int s1, int s2, int s3, int s4, int s5, int s6, int s7, int s8, int s9, int s10, int s11, int s12,
      int payload) {
    int total = 0;
    total += scoreRealStyleStep(s1, payload);
    total += scoreRealStyleStep(s2, payload + 1);
    total += scoreRealStyleStep(s3, payload + 2);
    total += scoreRealStyleStep(s4, payload + 3);
    total += scoreRealStyleStep(s5, payload + 4);
    total += scoreRealStyleStep(s6, payload + 5);
    total += scoreRealStyleStep(s7, payload + 6);
    total += scoreRealStyleStep(s8, payload + 7);
    total += scoreRealStyleStep(s9, payload + 8);
    total += scoreRealStyleStep(s10, payload + 9);
    total += scoreRealStyleStep(s11, payload + 10);
    total += scoreRealStyleStep(s12, payload + 11);
    return classify(total);
  }

  public static int factoriesDepth12BranchControl(
      int s1, int s2, int s3, int s4, int s5, int s6, int s7, int s8, int s9, int s10, int s11, int s12,
      int payload) {
    int total = 0;
    total += scoreBranchControlStep(s1, payload);
    total += scoreBranchControlStep(s2, payload + 1);
    total += scoreBranchControlStep(s3, payload + 2);
    total += scoreBranchControlStep(s4, payload + 3);
    total += scoreBranchControlStep(s5, payload + 4);
    total += scoreBranchControlStep(s6, payload + 5);
    total += scoreBranchControlStep(s7, payload + 6);
    total += scoreBranchControlStep(s8, payload + 7);
    total += scoreBranchControlStep(s9, payload + 8);
    total += scoreBranchControlStep(s10, payload + 9);
    total += scoreBranchControlStep(s11, payload + 10);
    total += scoreBranchControlStep(s12, payload + 11);
    return classify(total);
  }

  public static void main(String[] args) {
    factoriesRealStyle(1, 2);
    factoriesBranchControl(1, 2);
    factoriesDepth1RealStyle(0, 2);
    factoriesDepth1BranchControl(0, 2);
    factoriesDepth2RealStyle(0, 1, 2);
    factoriesDepth2BranchControl(0, 1, 2);
    factoriesDepth4RealStyle(0, 1, 2, 0, 2);
    factoriesDepth4BranchControl(0, 1, 2, 0, 2);
    factoriesDepth6RealStyle(0, 1, 2, 0, 1, 2, 2);
    factoriesDepth6BranchControl(0, 1, 2, 0, 1, 2, 2);
    factoriesDepth8RealStyle(0, 1, 2, 0, 1, 2, 0, 1, 2);
    factoriesDepth8BranchControl(0, 1, 2, 0, 1, 2, 0, 1, 2);
    factoriesDepth10RealStyle(0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 2);
    factoriesDepth10BranchControl(0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 2);
    factoriesDepth12RealStyle(0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 2);
    factoriesDepth12BranchControl(0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 2);
  }
}
