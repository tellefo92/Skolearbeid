import java.io.IOException;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;


class oblig2 {
  public static void main(String[] args) throws IOException {
    String filename = args[0];
    ProjectPlanner pp = new ProjectPlanner();
    pp.readFile(filename);

    if(pp.findCycle()){
      System.out.println("Terminating program.");
      System.exit(1);
    }
    else {
      //System.out.println("No cycle. Starting project.");
      System.out.println("\n------------------\nPROJECT SIMULATION\n------------------");
      pp.grapSort();
      System.out.println("\n---------------\nCRITICAL TASKS\n---------------");
      pp.criticalTasks();
      System.out.println("\n----------------\nTASK INFORMATION");
      pp.taskPrint();
    }

  }
}

//RENAME VARIABLES, make different!!!!!
class Task {
    int id, time, staff;
    String name;
    int earliestStart, latestStart;
    List<Task> outEdges = new ArrayList<>();
    List<Task> inEdges = new ArrayList<>();
    int cntPredecessors;
    boolean critical;

    void removePredecessors() {
        for (Task task: outEdges) {
            task.cntPredecessors--;
        }
    }

    int findRequiredStartTime(int MaxTime) {
        int requiredStartTime = -1;
        int decendantLatestStart;
        if (latestStart != -1) {
            return latestStart;
        }
        if (outEdges.isEmpty()) {
            latestStart = MaxTime - time;
            return latestStart;
        } else {
            for (Task decendants: outEdges) {
                if (requiredStartTime == -1) {
                    requiredStartTime = decendants.findRequiredStartTime(MaxTime);
                } else {
                    decendantLatestStart = decendants.findRequiredStartTime(MaxTime);
                    if (decendantLatestStart < requiredStartTime) {
                        requiredStartTime = decendantLatestStart;
                    }
                }
            }
        }
        latestStart = requiredStartTime - time;
        return latestStart;
    }
}

class ProjectPlanner {
  ArrayList<Task> startingTasks = new ArrayList<>(); // List of starting tasks in the project
  ArrayList<Task> readyTasks = new ArrayList<>(); // List of tasks ready to start, where their predecessor tasks are completed
  ArrayList<Task> runningTasks = new ArrayList<>(); // List of tasks currently running
  ArrayList<Task> finishedTasks = new ArrayList<>(); // List of tasks that have finished running
  static boolean findCycle = false;
  Task[] tasks;
  int currentTime = 0; //change name

  void readFile(String filename)  throws IOException {
    Scanner in = new Scanner(new File(filename));

    int n = in.nextInt(); // Number of tasks
    tasks = new Task[n]; // Create array of tasks with length n

    for (int i = 0; i < n; i++) {
      tasks[i] = new Task(); // Set all entries of array to a new task
    }
    for (int i = 0; i < n; i++) {
      int id = in.nextInt();
      Task task = tasks[id - 1];
      task.id = id;
      task.name = in.next();
      task.time = in.nextInt();
      task.staff = in.nextInt();

      while (true) {
        int dep = in.nextInt();
        if (dep == 0) {
          break;
        }
        tasks[dep - 1].outEdges.add(task); // Append dependant task to their predecessor
        tasks[id - 1].cntPredecessors++;
        tasks[id-1].inEdges.add(tasks[dep-1]);
      }
    }
    startingTasks = findReadyTasks(0);
  }

  ArrayList<Task> findReadyTasks(int time) {
    ArrayList<Task> readyTasks = new ArrayList<>();
    for (Task task: tasks) {
      if (task != null && task.cntPredecessors == 0) {
        readyTasks.add(task);
        task.earliestStart = time;
      }
    }
    return readyTasks;
  }

  boolean findCycle() {
    ArrayList<Task> v = new ArrayList<>();
    for (Task task: startingTasks) {
      if (cycleSearch(v, task)) {
        return true;
      }
    }
    return false;
  }

  boolean cycleSearch(ArrayList<Task> v, Task task) {
    if (v.contains(task)) {
      return true;
    }
    ArrayList<Task> tmp = new ArrayList<>();
    tmp.addAll(v);
    tmp.add(task);
    for (Task t: task.outEdges) {
      if (cycleSearch(tmp, t)) {
        if(!findCycle) {
          findCycle = true;
          tmp.add(t);
          int lastTask = tmp.get(tmp.size()-1).id;
          boolean path = false;
          System.out.println("Cycle detected:");
          for(Task _t: tmp) {
            if(_t.id == lastTask) {
              System.out.println(_t.id);
              path = true;
            }
            else if(path) {
              System.out.println(_t.id);
            }
          }
        }
        return true;
      }
    }
    return false;
  }

  //MAKE DIFFERENT
  void grapSort() {
    ArrayList<Task> started = new ArrayList<>();
    ArrayList<Task> completed = new ArrayList<>();
    boolean updated = false;
    int manpower = 0;

    while (!finishedProject()) {
      for (int i = runningTasks.size()-1; i >= 0; i--) {
        if((runningTasks.get(i).earliestStart + runningTasks.get(i).time) == currentTime) {
          completed.add(runningTasks.get(i));
          finishedTasks.add(runningTasks.get(i));
          manpower -= runningTasks.get(i).staff;
          runningTasks.get(i).removePredecessors();
          runningTasks.remove(i);
          updated = true;
        }
      }
      readyTasks = findReadyTasks(currentTime);
      for(Task t: readyTasks) {
        if (t == null) {
          break;
        }
        runningTasks.add(t);
        started.add(t);
        manpower += t.staff;
        finishTask(t.id);
        updated = true;
      }

      if (updated) {
        System.out.println("Time: " + currentTime);

        if (!completed.isEmpty()) {
          for (Task c : completed) {
            System.out.println("Finished: " + c.id);
          }
        }
        if (!started.isEmpty()) {
          for(Task s : started) {
            System.out.println("Started: " + s.id);
          }
        }
        System.out.println("Manpower: " + manpower);
        readyTasks.clear();
        started.clear();
        completed.clear();
        updated = false;
        System.out.println();
      }
      currentTime++;

    }
    currentTime--;
    System.out.println("All tasks have been completed!");
  }

  boolean finishedProject(){
    for (Task task : tasks) {
      if (task != null) return false;
    }
    for(Task task : runningTasks) {
      if (task != null) return false;
    }
    return true;
  }

  void finishTask(int id) {
    for (int i = 0; i < tasks.length; i++) {
      if (tasks[i] != null) {
        if (tasks[i].id == id) {
          tasks[i] = null;
        }
      }
    }
  }


  //DOES NOT WORK AND MAKE DIFFERENT
  void criticalTasks() {
    int min = -1;
    int latestStart;
    for (Task task : startingTasks) {
      latestStart = task.findRequiredStartTime(currentTime);
      if (min == -1) {
        min = latestStart;
      }
      if (latestStart < min) {
        min = latestStart;
      }
    }
    for (Task task : finishedTasks) {
      if((-1*task.latestStart - task.earliestStart) == 0) {
        task.critical = true;
        System.out.println(task.id+ ": " +task.name);
      }
    }
  }

  void taskPrint() {
    for (Task task: finishedTasks) {
      System.out.println("----------------");
      System.out.println("ID: " + task.id);
      System.out.println("Name: " + task.name);
      System.out.println("Time needed: " + task.time);
      System.out.println("Manpower needed: " + task.staff);
      System.out.println("Earliest start: " + task.earliestStart);
      System.out.println("Slack: " + (-1*task.latestStart - task.earliestStart)); //DOES NOT WORK BEACUSE OF LATEST TIME
      System.out.println("Tasks depending on this task: ");
      for (Task k : task.outEdges){
        System.out.println("- Task ID: " + k.id);
      }
      /*System.out.println("InEdges:");
      for (Task m : task.inEdges){
        System.out.println("ID: " + m.id + "  ");
      }*/
    }
  }
}
