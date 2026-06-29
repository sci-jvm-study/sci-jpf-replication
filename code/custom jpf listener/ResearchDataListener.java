package gov.nasa.jpf.symbc;

import gov.nasa.jpf.Config;
import gov.nasa.jpf.JPF;
import gov.nasa.jpf.ListenerAdapter;
import gov.nasa.jpf.search.Search;
import gov.nasa.jpf.symbc.numeric.PCChoiceGenerator;
import gov.nasa.jpf.symbc.numeric.PathCondition;
import gov.nasa.jpf.vm.ChoiceGenerator;
import gov.nasa.jpf.vm.ThreadInfo;
import gov.nasa.jpf.vm.VM;
import gov.nasa.jpf.vm.Instruction;
import gov.nasa.jpf.jvm.bytecode.IfInstruction;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Listener for collecting per-path solver timing on completed paths.
 *
 * Exposes branch coverage progression, queue size, GC cycles, and heap allocations.
 */
public class ResearchDataListener extends ListenerAdapter {

  private static final String HEADER =
      "run_id,benchmark,search_strategy,method_label,path_index,status,state_id,depth,"
          + "constraint_count,solver_time_ns,sat,has_exception,has_loop,"
          + "has_division,has_nested_branch,has_dispatch,branches_covered,pc";
  private static final String SUMMARY_HEADER =
      "run_id,benchmark,search_strategy,method_label,total_elapsed_ns,total_solver_time_ns,"
          + "engine_time_ns,completed_paths,new_states,state_advanced_events,"
          + "choice_generators,pc_choice_generators,branches_covered,max_queue_size,"
          + "gc_cycles,heap_allocations_bytes,reproducible_seed";

  private final BufferedWriter writer;
  private final BufferedWriter summaryWriter;
  private final String benchmark;
  private final String searchStrategy;
  private final String configuredMethodLabel;
  private final String runId;
  private final boolean hasException;
  private final boolean hasLoop;
  private final boolean hasDivision;
  private final boolean hasNestedBranch;
  private final boolean hasDispatch;
  private final Set<String> seenPaths = new HashSet<String>();
  private final Set<String> uniqueBranchesCovered = new HashSet<String>();

  private long pathIndex = 0;
  private long completedPathCount = 0;
  private long totalSolverTimeNs = 0;
  private long runStartNs = 0;
  private long newStateCount = 0;
  private long stateAdvancedEvents = 0;
  private long choiceGeneratorCount = 0;
  private long pcChoiceGeneratorCount = 0;

  private int maxQueueSize = 0;
  private long gcStartCount = 0;
  private long heapAllocStart = 0;
  private long maxHeapAlloc = 0;
  private long choiceSeed = 42;

  public ResearchDataListener(Config conf, JPF jpf) {
    benchmark = conf.getString("research.benchmark", "unknown");
    searchStrategy = conf.getString("research.search_label",
        conf.getString("search.class", "unknown"));
    configuredMethodLabel = conf.getString("research.method_label", "unknown");
    runId = conf.getString("research.run_id", "run-0");
    hasException = conf.getBoolean("research.has_exception", false);
    hasLoop = conf.getBoolean("research.has_loop", false);
    hasDivision = conf.getBoolean("research.has_division", false);
    hasNestedBranch = conf.getBoolean("research.has_nested_branch", false);
    hasDispatch = conf.getBoolean("research.has_dispatch", false);
    choiceSeed = conf.getLong("choice.seed", 42);

    String outputPath = conf.getString(
        "research.output",
        "results/research_data.csv");
    boolean append = conf.getBoolean("research.append", false);

    try {
      File outputFile = new File(outputPath);
      File parent = outputFile.getParentFile();
      if (parent != null && !parent.exists()) {
        parent.mkdirs();
      }

      boolean writeHeader = !append || !outputFile.exists() || outputFile.length() == 0;
      writer = new BufferedWriter(new FileWriter(outputFile, append));
      if (writeHeader) {
        writer.write(HEADER);
        writer.newLine();
      }
      String summaryPath = conf.getString("research.summary_output", deriveSummaryPath(outputPath));
      File summaryFile = new File(summaryPath);
      File summaryParent = summaryFile.getParentFile();
      if (summaryParent != null && !summaryParent.exists()) {
        summaryParent.mkdirs();
      }
      boolean writeSummaryHeader = !append || !summaryFile.exists() || summaryFile.length() == 0;
      summaryWriter = new BufferedWriter(new FileWriter(summaryFile, append));
      if (writeSummaryHeader) {
        summaryWriter.write(SUMMARY_HEADER);
        summaryWriter.newLine();
      }
      writer.flush();
      summaryWriter.flush();
      System.out.println("[RESEARCH] CSV ready: " + outputFile.getAbsolutePath());
    } catch (IOException e) {
      throw new RuntimeException("Failed to open research output file", e);
    }
  }

  private long getGcCycles() {
    long gcCount = 0;
    try {
      List<GarbageCollectorMXBean> beans = ManagementFactory.getGarbageCollectorMXBeans();
      for (GarbageCollectorMXBean bean : beans) {
        long count = bean.getCollectionCount();
        if (count != -1) {
          gcCount += count;
        }
      }
    } catch (Exception ignored) {}
    return gcCount;
  }

  private long getHeapAllocatedBytes() {
    return Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
  }

  @Override
  public void searchStarted(Search search) {
    runStartNs = System.nanoTime();
    gcStartCount = getGcCycles();
    heapAllocStart = getHeapAllocatedBytes();
    maxHeapAlloc = heapAllocStart;
  }

  @Override
  public void stateAdvanced(Search search) {
    stateAdvancedEvents++;
    if (search.isNewState()) {
      newStateCount++;
    }
    
    int qSize = -1;
    if (search instanceof gov.nasa.jpf.search.heuristic.HeuristicSearch) {
      qSize = ((gov.nasa.jpf.search.heuristic.HeuristicSearch) search).getQueueSize();
    }
    if (qSize > maxQueueSize) {
      maxQueueSize = qSize;
    }
    
    long currentHeap = getHeapAllocatedBytes();
    if (currentHeap > maxHeapAlloc) {
      maxHeapAlloc = currentHeap;
    }

    if (search.isEndState()) {
      recordCompletedPath(search, "END");
    }
  }

  @Override
  public void instructionExecuted(VM vm, ThreadInfo currentThread, Instruction nextInstruction, Instruction executedInstruction) {
    if (executedInstruction instanceof IfInstruction) {
      String branchId = executedInstruction.getMethodInfo().getFullName() + ":" + executedInstruction.getPosition();
      uniqueBranchesCovered.add(branchId);
    }
  }

  @Override
  public void choiceGeneratorAdvanced(VM vm, ChoiceGenerator<?> currentCG) {
    choiceGeneratorCount++;
    if (currentCG instanceof PCChoiceGenerator) {
      pcChoiceGeneratorCount++;
    }
  }

  @Override
  public void propertyViolated(Search search) {
    recordCompletedPath(search, "ERROR");
  }

  @Override
  public void searchFinished(Search search) {
    try {
      if (pathIndex == 0) {
        recordCompletedPath(search, "END");
      }
      writeRunSummary();
      writer.flush();
      summaryWriter.flush();
      writer.close();
      summaryWriter.close();
      System.out.println("[RESEARCH] CSV closed successfully.");
    } catch (IOException e) {
      throw new RuntimeException("Failed to close research output file", e);
    }
  }

  private void recordCompletedPath(Search search, String status) {
    completedPathCount++;
    VM vm = search.getVM();
    PathCondition pc = getCurrentPathCondition(vm);
    if (pc == null) {
      pc = new PathCondition();
    }

    String methodLabel = resolveMethodLabel(vm);
    String pcText = normalize(pc.toString());
    String uniqueKey = benchmark + "|" + status + "|" + methodLabel + "|" + pcText;
    if (!seenPaths.add(uniqueKey)) {
      return;
    }

    long startedAt = System.nanoTime();
    boolean sat = pc.solve();
    long solverTimeNs = System.nanoTime() - startedAt;
    totalSolverTimeNs += solverTimeNs;
    pathIndex++;

    try {
      writer.write(csv(
          runId,
          benchmark,
          searchStrategy,
          methodLabel,
          Long.toString(pathIndex),
          status,
          Integer.toString(vm.getStateId()),
          Integer.toString(resolveDepth(search, vm)),
          Integer.toString(pc.count()),
          Long.toString(solverTimeNs),
          Boolean.toString(sat),
          Boolean.toString(hasException),
          Boolean.toString(hasLoop),
          Boolean.toString(hasDivision),
          Boolean.toString(hasNestedBranch),
          Boolean.toString(hasDispatch),
          Integer.toString(uniqueBranchesCovered.size()),
          pcText));
      writer.newLine();
    } catch (IOException e) {
      throw new RuntimeException("Failed to write research CSV row", e);
    }
  }

  private PathCondition getCurrentPathCondition(VM vm) {
    ChoiceGenerator<?> cg = vm.getChoiceGenerator();
    while (cg != null) {
      if (cg instanceof PCChoiceGenerator) {
        PathCondition pc = ((PCChoiceGenerator) cg).getCurrentPC();
        if (pc != null) {
          return pc;
        }
      }
      cg = cg.getPreviousChoiceGenerator();
    }
    return null;
  }

  private String resolveMethodLabel(VM vm) {
    if (configuredMethodLabel != null && configuredMethodLabel.length() > 0
        && !"unknown".equals(configuredMethodLabel)) {
      return configuredMethodLabel;
    }

    ThreadInfo ti = vm.getCurrentThread();
    if (ti != null && ti.getTopFrame() != null && ti.getTopFrame().getMethodInfo() != null) {
      return ti.getTopFrame().getMethodInfo().getFullName();
    }
    return "unknown";
  }

  private String deriveSummaryPath(String outputPath) {
    if (outputPath.endsWith(".csv")) {
      return outputPath.substring(0, outputPath.length() - 4) + "_summary.csv";
    }
    return outputPath + "_summary.csv";
  }

  private void writeRunSummary() throws IOException {
    long totalElapsedNs = runStartNs == 0 ? 0 : (System.nanoTime() - runStartNs);
    long engineTimeNs = totalElapsedNs - totalSolverTimeNs;
    if (engineTimeNs < 0) {
      engineTimeNs = 0;
    }
    long gcCycles = getGcCycles() - gcStartCount;
    if (gcCycles < 0) {
      gcCycles = 0;
    }
    long heapAllocBytes = maxHeapAlloc - heapAllocStart;
    if (heapAllocBytes < 0) {
      heapAllocBytes = 0;
    }

    summaryWriter.write(csv(
        runId,
        benchmark,
        searchStrategy,
        configuredMethodLabel,
        Long.toString(totalElapsedNs),
        Long.toString(totalSolverTimeNs),
        Long.toString(engineTimeNs),
        Long.toString(completedPathCount),
        Long.toString(newStateCount),
        Long.toString(stateAdvancedEvents),
        Long.toString(choiceGeneratorCount),
        Long.toString(pcChoiceGeneratorCount),
        Integer.toString(uniqueBranchesCovered.size()),
        Integer.toString(maxQueueSize),
        Long.toString(gcCycles),
        Long.toString(heapAllocBytes),
        Long.toString(choiceSeed)));
    summaryWriter.newLine();
  }

  private int resolveDepth(Search search, VM vm) {
    int stateId = vm.getStateId();
    if (stateId >= 0) {
      try {
        return search.getStateDepth(stateId);
      } catch (RuntimeException ignored) {
        return -1;
      }
    }
    return -1;
  }

  private String normalize(String text) {
    if (text == null) {
      return "";
    }

    return text
        .replace("\r", " ")
        .replace("\n", " ")
        .replaceAll("\\s+", " ")
        .trim();
  }

  private String csv(String... values) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < values.length; i++) {
      if (i > 0) {
        sb.append(',');
      }

      String value = values[i] == null ? "" : values[i];
      sb.append('"');
      for (int j = 0; j < value.length(); j++) {
        char ch = value.charAt(j);
        if (ch == '"') {
          sb.append('"');
        }
        sb.append(ch);
      }
      sb.append('"');
    }
    return sb.toString();
  }
}
