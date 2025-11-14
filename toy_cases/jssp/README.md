# jssp — Job Shop Scheduling Problem (Quantum Optimization)

This repository demonstrates how to model the Job Shop Scheduling Problem (JSSP) as a QUBO, map it to an Ising Hamiltonian, and solve it with QAOA (Quantum Approximate Optimization Algorithm) using Qiskit. The material follows the "Quantum Optimization ISC 2025" presentation and provides code, notebooks, and utilities to reproduce experiments on a simulator (and on IBM hardware if you configure credentials).

Contents
- README.md — this file
- notebooks/ — interactive walkthroughs and examples (small JSSP instances, visualization)
- utilities/ — helper scripts, requirements, environment files, and helper modules to build QUBO, map to Ising, run QAOA, and plot Gantt charts

Quick summary
- Variables: $x_{k,t} = 1$ if operation $k$ starts at time $t$
- Constraints encoded as penalty terms:
  - $h_1$: each operation starts exactly once
  - $h_2$: machine conflict (no overlapping ops on the same machine)
  - $h_3$: precedence constraints within each job
- Objective: $H(x) = \lambda_1 h_1 + \lambda_2 h_2 + \lambda_3 h_3$
- QUBO → Ising via $x = \frac{1 - \sigma}{2}$
- Solve using QAOA (cost and mixer Hamiltonians) implemented in Qiskit

Features
- Build QUBO from a JSSP instance (jobs, operations, machines, durations)
- Convert QUBO → Ising Hamiltonian (Pauli Z terms and ZZ interactions)
- Run QAOA via Qiskit (simulator or IBM backend)
- Decode solutions, validate feasibility, and draw Gantt charts
- Example notebooks for small instances and parameter tuning

Prerequisites
- Python 3.8+ (3.9 or 3.10 recommended)
- Recommended libraries (see utilities/requirements.txt):
  - qiskit, qiskit-terra, qiskit-aer (for local simulation)
  - qiskit-ibm-runtime (optional, for IBM backends)
  - qiskit-optimization
  - numpy, scipy, matplotlib, pandas, seaborn
  - plotly (optional, for interactive Gantt charts)

Installation (basic, using pip)
1. Create a virtual environment:
   ```python -m venv .venv
   source .venv/bin/activate  # Linux / macOS
   .venv\Scripts\activate     # Windows```

2. Install dependencies:
   ```
   pip install -r utilities/requirements.txt
   ```

Or use the supplied conda script:
   ```bash utilities/create_conda_env.sh``` 

Structure and important files
- notebooks/
  - jssp_qubo_qaoa_qiskit.ipynb — end-to-end walkthrough: build QUBO, map to Ising, run QAOA, decode, and plot Gantt
  - helper.py — helper routines used by the notebooks (QUBO builder, decoder, plotting);
    - build_qubo.py        — helper to construct QuadraticProgram / QUBO
    - qubo_to_ising.py    — convert QUBO to Ising coefficients (J, h)
    - qaoa_runner.py      — wrapper to run QAOA with Qiskit, choose optimizer, and backends
    - decode.py           — decode bitstrings → start times → schedule validator
    - gantt_plot.py       — functions to render Gantt charts (matplotlib & plotly)
    

- utilities/
  - requirements.txt
  - create_conda_env.sh
  - qiskit_container.def

How the QUBO is constructed (outline)
- Binary variables:
  $x_{k,t} = 1$ iff operation $k$ starts at time $t$ ($t \in \{0, \dots, T\}$)
- Operation-start-once penalty:
  $h_1(x) = \sum_k \left( \sum_t x_{k,t} - 1 \right)^2$
- Machine conflict penalty:
  $h_2(x) = \sum_m \sum_{k\ne k'} \sum_{t,t'} x_{k,t} x_{k',t'}$ with the overlap condition $0 < t' - t < \ell_k$
- Precedence penalty:
  $h_3(x) = \sum_{j=1}^J \sum_{k \in \text{ops of job } j} \sum_{\substack{t,t' \\ t + \ell_k > t'}} x_{k,t} x_{k+1,t'}$
- Final QUBO: $H(x) = \lambda_1 h_1 + \lambda_2 h_2 + \lambda_3 h_3$

Tips for choosing $\lambda$ weights
- $\lambda_1$ must be large enough that all operations start exactly once (otherwise trivial solutions are favored)
- $\lambda_2$ should penalize machine overlaps strongly; scale relative to $\lambda_1$ and typical processing times
- $\lambda_3$ must enforce job ordering; adjust depending on instance slack
- Practical approach: set $\lambda_1 = 10 \times \text{max-processing-time}$, $\lambda_2 = 10 \times \lambda_1$, $\lambda_3 = \lambda_1$ (experiment and tune)
- The notebooks include small sweeps to show sensitivity

Mapping QUBO → Ising
- Replace $x_i$ with $\frac{1 - \sigma_i}{2}$ and expand to get linear $\sigma_i$ and pairwise $\sigma_i \sigma_j$ terms
- The utilities/qubo_to_ising.py returns:
  - linear fields $h_i$ (for $\sigma_i$)
  - couplings $J_{ij}$ (for $\sigma_i \sigma_j$)
- These map directly to Qiskit PauliSum or Operator objects for $U_C$.

QAOA formulation (summary)
- Cost unitary: $U_C(\gamma) = e^{-i \gamma H_C}$
- Mixer Hamiltonian: $H_0 = \sum_j \sigma_x^{(j)}$
  - Mixer unitary: $U_0(\beta) = e^{-i \beta H_0}$
- QAOA state at depth $p$:
  $|\gamma,\beta\rangle = \prod_{k=1}^{p} U_0(\beta_k)\, U_C(\gamma_k)\, |s\rangle$
- Objective to minimize:
  $F_p(\gamma,\beta) = \langle \gamma,\beta | H_C | \gamma,\beta \rangle$

Running QAOA (outline)
- Cost Hamiltonian: $H_C$ = Ising Hamiltonian from QUBO
- Mixer: $H_0 = \sum_j \sigma_x^{(j)}$
- Use Qiskit's QAOA class and MinimumEigenOptimizer (qiskit-optimization)
- Example optimizer: SPSA or COBYLA (classical)
- Depth $p$: start small ($p = 1, 2$) and increase while monitoring runtime
- Two execution modes:
  - Local simulation: qiskit-aer (fast for small $n$)
  - IBM hardware: qiskit-ibm-runtime (requires token / account setup)

Quick example (snippet)
```python
from qiskit_optimization import QuadraticProgram
from qiskit_algorithms import QAOA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms.optimizers import SPSA

# Build problem using utilities/helpers/build_qubo.py
# This provides a QuadraticProgram instance with binary variables and objective = QUBO.

qp = build_qubo_from_instance(my_instance, T=20, lambdas=(100, 1000, 100))
qaoa = QAOA(optimizer=SPSA(maxiter=200), reps=1, quantum_instance=local_simulator_instance)
solver = MinimumEigenOptimizer(qaoa)

result = solver.solve(qp)
print(result)
# Use utilities/helpers to convert result.x to start times and validate schedule
```

Decoding and visualization
- After obtaining the binary solution, decode the vector into start times for operations.
- Validate constraints (operation-once, machine conflicts, precedence).
- If invalid, increase $\lambda$ weights or use a classical local-improvement heuristic to repair.
- Use utilities/helpers/gantt_plot.py to draw the schedule; notebooks include example Gantt charts.

Benchmarking and baselines
- Provide simple classical baselines for comparison:
  - Greedy list scheduling
  - Local search (swap/start-time adjustments)
  - Simulated annealing (small instances)
- Notebooks show baseline runs side-by-side with QAOA results (energy, feasibility, makespan).

Troubleshooting & notes
- QAOA parameters and QUBO penalties greatly affect results — run parameter sweeps.
- Problem sizes blow up quickly: number of binary variables $\approx$ (number of operations) $\times$ $(T+1)$.
- Reduce $T$ by computing a reasonable upper bound (sum of durations per job or lower bounds).
- Running on real hardware requires noise-aware mapping and transpiler settings.

Contributing
- Open issues and PRs welcome. Suggested tasks:
  - Add more efficient QUBO encoding to reduce variable counts (time-window compression)
  - Implement advanced mixers tailored to scheduling constraints
  - Add repair heuristics to post-process near-feasible states

License
- Placeholder: will be updated.

Acknowledgements
- Based on the work of my work at GWDG/Quantum Computing for "Quantum Optimization ISC 2025" presentation and the Qiskit Optimization framework at ISC 2025.

Contact
- Repository owner: @mehmetniyazikayi
- For questions, open an issue or pull request.
