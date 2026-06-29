package gov.nasa.jpf.search.heuristic;

import gov.nasa.jpf.Config;
import gov.nasa.jpf.vm.ChoiceGenerator;
import gov.nasa.jpf.vm.VM;

/**
 * Structural Complexity Index (SCI) Guided Search Heuristic
 */
public class SCISearch extends SimplePriorityHeuristic {

  private final double w1;
  private final double w2;

  public SCISearch(Config config, VM vm) {
    super(config, vm);
    this.w1 = config.getDouble("search.sci.w1", 1.0);
    this.w2 = config.getDouble("search.sci.w2", 5.0);
    System.out.println(String.format("[SCI] Initialized SCISearch Heuristic: w1=%.3f, w2=%.3f", w1, w2));
  }

  @Override
  protected int computeHeuristicValue() {
    // 1. Calculate Ncg (cumulative Choice Generators on path)
    int nCg = 0;
    ChoiceGenerator<?> cg = vm.getChoiceGenerator();
    while (cg != null) {
      nCg++;
      cg = cg.getPreviousChoiceGenerator();
    }

    // 2. Calculate HeapMB
    double heapMb = (double) (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()) / (1024.0 * 1024.0);
    if (heapMb < 0) {
      heapMb = 0;
    }

    // 3. Compute SCI
    double sci = (w1 * nCg) + (w2 * heapMb);

    // 4. Map to min-heuristic score (low SCI gets priority, as lower means higher priority in JPF)
    return (int) Math.round(sci * 1000.0);
  }
}
