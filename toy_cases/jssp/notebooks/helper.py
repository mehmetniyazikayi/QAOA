import matplotlib.pyplot as plt
import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_aer.primitives import Sampler as AerSampler

# === Functions for constructing the QUBO matrix ===

def apply_unique_start_constraint(Q, var_index, num_tasks, T_max, penalty):
    """
    Q: QUBO matrix to which this constraint is added
    var_index: Dictionary containing the indices of the variables
    num_tasks: Number of tasks
    T_max: Time horizon for the optimization
    penalty: Penalty constant
    """
    
    for k in range(num_tasks):
        for t1 in range(T_max):
            idx_1 = var_index[(k, t1)]
            Q[idx_1, idx_1] -= penalty # Diagonal term
            
            for t2 in range(t1 + 1, T_max):
                if t1 != t2:
                    idx_2 = var_index[(k, t2)]
                    Q[idx_1, idx_2] += penalty 
    return Q


def apply_machine_conflict_constraint(Q, var_index, task_map, T_max, penalty):
    """
    Q: QUBO matrix to which this constraint is added
    var_index: Dictionary containing the indices of the variables
    task_map: Maps task indices to task information
    T_max: Time horizon for the optimization
    penalty: Penalty constant
    """
    
    for k1, (j1, o1, m1, d1) in task_map.items():
        for k2, (j2, o2, m2, d2) in task_map.items():
            if k1 == k2: # Check if one considers different tasks 
                continue
            if m1 != m2: # Check if tasks are on the same machine
                continue
    
            for t1 in range(T_max):
                for t2 in range(T_max):
                    if 0 < (t2 - t1) < d1:
                        idx_1 = var_index[(k1, t1)]
                        idx_2 = var_index[(k2, t2)]
                        if idx_1 is not None and idx_2 is not None: 
                            Q[idx_1, idx_2] += penalty
    return Q

    
def apply_precedence_constraint(Q, var_index, task_map, T_max, penalty):
    """
    Q: QUBO matrix to which this constraint is added
    var_index: Dictionary containing the indices of the variables
    task_map: Maps task indices to task information
    T_max: Time horizon for the optimization
    penalty: Penalty constant
    """
    
    # Build job_tasks mapping:
    job_tasks = {}
    for k, (job, _, _, _) in task_map.items():
        if job not in job_tasks:
            job_tasks[job] = []
        job_tasks[job].append(k)
    
    for job in job_tasks:
        job_tasks[job].sort() # Sort operations in order
        
        for operation_idx in range(len(job_tasks[job]) - 1): # Loop over all k-1 operations of each job
            k1 = job_tasks[job][operation_idx] # current task
            k2 = job_tasks[job][operation_idx + 1] # next task
    
            _, _, _, duration_1 = task_map[k1]
    
            for t1 in range(T_max):
                for t2 in range(T_max):
                    if t2 < t1 + duration_1: # Check if tasks overlap
                        idx_1 = var_index.get((k1, t1))
                        idx_2 = var_index.get((k2, t2))
                        if idx_1 is not None and idx_2 is not None:
                            Q[idx_1, idx_2] += penalty
    return Q


# === Objective function ===
# Makespan minimization via late-finish penalty
def apply_makespan_objective(Q, var_index, task_map, num_tasks, T_max, weight):
    """
    Q: QUBO matrix to which the makespan is added
    var_index: Dictionary containing the indices of the variables
    num_tasks: Number of tasks
    task_map: Maps task indices to task information
    T_max: Time horizon for the optimization
    weight: Weight of the makespan ("how important it is")
    """
    
    for k in range(num_tasks):
        duration = task_map[k][3]
        for t in range(T_max):
            idx = var_index[(k, t)]
            Q[idx, idx] += weight * (t + duration)
    return Q



# === Functions for interpreting the results ===

def extract_schedule_from_result(result, var_index, task_map, num_tasks, T_max):
    """
    result: Optimization result as bitstring
    var_index: Dictionary containing the indices of the variables
    task_map: Maps task indices to task information
    num_tasks: Number of tasks
    T_max: Time horizon for the optimization
    """
    
    schedule = []
    for k in range(num_tasks):
        for t in range(T_max):
            idx = var_index[(k, t)]
            if round(result[idx]) == 1:
                job_id, task_idx, machine, duration = task_map[k]
                schedule.append({
                    "task": k,
                    "job": job_id,
                    "task_idx": task_idx,
                    "machine": machine,
                    "start": t,
                    "duration": duration,
                    "end": t + duration})
    return sorted(schedule, key=lambda x: x["start"])


def plot_gantt_chart_machines(schedule, T_max, title="Gantt Chart - QAOA Result"):
    """
    schedule: Resulting schedule of the optimization
    T_max: Time horizon for the optimization
    """
    
    fig, ax = plt.subplots(figsize=(8, 3))
    machines = {0: "Machine 0", 1: "Machine 1"}
    for task in schedule:
        ax.broken_barh(
            [(task["start"], task["duration"])],
            (10 * task["machine"], 8),
            facecolors='tab:blue')
        ax.text(
            task["start"] + task["duration"] / 2 - 0.2,
            10 * task["machine"] + 4,
            f"J{task['job']}-T{task['task_idx']}",
            va='center',
            ha='center',
            color='white',
            fontsize=8)
    ax.set_yticks([10, 20])
    ax.set_yticklabels([machines[0], machines[1]])
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.set_xlim(0, T_max + 1)
    ax.grid(True)
    plt.tight_layout()
    plt.show()


def compute_makespan(schedule):
    """
    schedule: Resulting schedule of the optimization
    """
    return max(task["end"] for task in schedule)


def check_machine_conflicts(schedule):
    """
    schedule: Resulting schedule of the optimization
    """
    
    conflicts = []
    for machine in {0, 1}:
        machine_tasks = sorted(
            [t for t in schedule if t["machine"] == machine],
            key=lambda x: x["start"])
        
        for i in range(len(machine_tasks) - 1):
            if machine_tasks[i]["end"] > machine_tasks[i + 1]["start"]:
                conflicts.append((machine_tasks[i], machine_tasks[i + 1]))
    return conflicts

    
def check_precedence_violations(schedule):
    """
    T_max: Time horizon for the optimization
    """
    
    violations = []
    by_job = {}
    for task in schedule:
        by_job.setdefault(task["job"], []).append(task)
    for job_tasks in by_job.values():
        sorted_tasks = sorted(job_tasks, key=lambda x: x["task_idx"])
        for i in range(len(sorted_tasks) - 1):
            if sorted_tasks[i]["end"] > sorted_tasks[i + 1]["start"]:
                violations.append((sorted_tasks[i], sorted_tasks[i + 1]))
    return violations


def check_unique_start_constraint(schedule, num_tasks):
    """
    schedule: Resulting schedule of the optimization
    num_tasks: Number of tasks
    """
    
    from collections import Counter

    task_counts = Counter(task["task"] for task in schedule)
    violations = []

    for task_id in range(num_tasks):
        count = task_counts.get(task_id, 0)
        if count != 1:
            violations.append((task_id, count))
    return violations


# === Solver ===
def solve_and_visualize_jssp(penalty_config, num_vars, var_index, task_map, num_tasks, T_max, colors):
    """
    penalty_config: Dictionary of all penalty constants
    num_vasrs: Number of varaibles
    var_index: Dictionary containing the indices of the variables
    num_tasks: Number of tasks
    task_map: Maps task indices to task information
    T_max: Time horizon for the optimization
    colors: List of desired colors for the plot
    """
    
    # Generate QUBO matrix:
    Q = np.zeros((num_vars, num_vars))
    Q = apply_unique_start_constraint(Q, var_index, num_tasks, T_max, penalty=penalty_config["one_hot"])
    Q = apply_machine_conflict_constraint(Q, var_index, task_map, T_max, penalty=penalty_config["machine"])
    Q = apply_precedence_constraint(Q, var_index, task_map, T_max, penalty=penalty_config["precedence"])
    Q = apply_makespan_objective(Q, var_index, task_map, num_tasks, T_max, weight=penalty_config["makespan"])

    # Construct the QuadraticProgram:
    qp = QuadraticProgram()
    for i in range(num_vars):
        qp.binary_var(name=f"x_{i}")
    linear = {f"x_{i}": Q[i, i] for i in range(num_vars)}
    quadratic = {(f"x_{i}", f"x_{j}"): Q[i, j] for i in range(num_vars) for j in range(i + 1, num_vars) if Q[i, j] != 0}
    qp.minimize(linear=linear, quadratic=quadratic)

    # QAOA pipeline:
    sampler = AerSampler(backend_options={"method": "statevector"})
    qaoa = QAOA(sampler=sampler, optimizer=COBYLA(), reps=1)
    optimizer = MinimumEigenOptimizer(min_eigen_solver=qaoa)

    # Solve and visualize the problem:
    result = optimizer.solve(qp)
    print(f"\n* Penalty Config: {penalty_config['name']}")
    print("  - Binary Solution:", result.x)

    schedule = extract_schedule_from_result(result.x, var_index, task_map, num_tasks, T_max)
    plot_gantt_chart_jobs(schedule, colors, title=penalty_config["name"] + " Job Gantt Chart")
    plot_gantt_chart_machines(schedule, T_max, title=penalty_config["name"] + " Machine Gantt Chart")


# === Job Gantt Chart ===
def plot_gantt_chart_jobs(schedule, colors, title):
    """
    schedule: Resulting schedule of the optimization
    colors: List of desired colors for the plot
    """
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    yticks = []
    ytick_labels = []
    for task in schedule:
        ax.broken_barh([(task["start"], task["duration"])], (task["task"] - 0.4, 0.8), facecolors=colors[task["job"] % len(colors)])
        yticks.append(task["task"])
        ytick_labels.append(f"Job {task["job"]}, Task {task["task_idx"]}")

    ax.set_xlabel("Time")
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels)
    ax.set_title(title)
    ax.grid(True)
    plt.tight_layout()
    plt.show()

