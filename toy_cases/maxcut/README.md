maxcut — Max-Cut Problem (Quantum Optimization)


This directory contains implementations and resources to solve the MaxCut problem using QAOA across multiple quantum SDKs. The README documents the problem formulation, circuit construction, measurement & evaluation, recommended experiments, and the repository layout for the new file structure you provided.

## Problem statement

Given an undirected graph $G = (V, E)$, partition the vertices into two disjoint sets so that the number (or total weight) of edges between the sets is maximized.

Representations:
- Ising variables: $z_i \in \{+1, -1\}$
- Binary variables: $x_i \in \{0, 1\}$
- Relation: $z_i = 1 - 2 x_i$

Cost Hamiltonian (unweighted edges):
$H_C = \sum_{(i,j)\in E} \dfrac{1 - Z_i Z_j}{2}$

For weighted edges include $w_{ij}$:
$H_C = \sum_{(i,j)\in E} w_{ij}\,\dfrac{1 - Z_i Z_j}{2}$

We use the QAOA ansatz:
$|\psi(\boldsymbol{\gamma},\boldsymbol{\beta})\rangle = U_B(\beta_p)\,U_C(\gamma_p)\,\dots\,U_B(\beta_1)\,U_C(\gamma_1)\,|+\rangle^{\otimes n}$,  
$U_C(\gamma) = \exp\big(-i \gamma H_C\big)$,  
$U_B(\beta) = \exp\big(-i \beta \sum_i X_i\big)$.

## New directory layout (as provided)

maxcut/
- readme.md (this file)
- utilities/
  - qiskit/
    - conda_env.sh
    - qiskit_container.def
  - qulacs/
    - conda_env.sh
    - qulacs_container.def
  - qsim/
  - cudaq/
  - pennylane/
  - qubo/
  - qutip/
- notebooks/
  - maxcut_qiskit.iphyn
  - maxcut_qulacs.iphyn
  - maxcut_qsim.iphyn
  - maxcut_qubo.iphyn
  - maxcut_cudaq.iphyn
  - maxcut_pennylane.iphyn
  - maxcut_qutip.iphyn

Notes:
- The `utilities/` folder contains per-SDK environment and container definitions (where provided) and should also host shared helper scripts (graph generation, converters, cost evaluators). Place common utilities at `utilities/shared/` or at the top of `utilities/` if preferred.
- The `notebooks/` folder holds portable problem-instance notebooks or `.iphyn` files tailored per SDK.

## What to include in each SDK utility folder

- conda environment script: `conda_env.sh` — creates a reproducible environment for examples and CI.
- container definition: `*_container.def` — Singularity/Apptainer or similar container recipe to reproduce runtime environment (optional but recommended).
- Example driver scripts or notebooks (placed under `utilities/<sdk>/examples/` OR under separate top-level SDK folders if you prefer).

## Circuit construction notes (SDK-agnostic)

- Phase separator for edge $(i,j)$: implement $\exp\!\big(-i \gamma (1 - Z_i Z_j)/2\big)$.
  - Implement $Z_i Z_j$ using CNOT$(i\to j)$; $RZ(2\gamma w_{ij})$ on $j$; CNOT$(i\to j)$ (or controlled-phase).
- Mixer: single-qubit $X$-rotations $R_X(2\beta)$ on each qubit.
- Repeat phase + mixer for $p$ layers.
- Verify gate-angle sign and factor conventions per SDK (RZ/rotation conventions vary).

## Measurement, cost evaluation & reporting

- For a measured bitstring $s$ compute: \maxcut
                     \readme.md
                     \utilities
                             \qiskit
                                conda_env.sh	
                                qiskit_container.def
                             \qulacs
                               conda_env.sh	
                               qulacs_container.def
                             \qsim
                             \cudaq
                             \pennylane
                             \qubo
                             \qutip
                     \notebooks
                          \maxcut_qiskit.iphyn
                          \maxcut_qulacs.iphyn
                          \maxcut_qsim.iphyn
                          \maxcut_qubo.iphyn
                          \maxcut_cudaq.iphyn
                          \maxcut_pennylane.iphyn
                          \maxcut_qutip.iphyn
                     
                   
  $\text{cut}(s) = \sum_{(i,j)\in E} w_{ij}\,[s_i \ne s_j]$
- Estimate expectation via sample mean or compute exact $\langle \psi| H_C |\psi \rangle$ for statevector simulators.
- Report: best sampled cut & bitstring, mean cut ± std, approximation ratio $\dfrac{\text{observed-cut}}{\text{max-cut-value}}$ (if known), optimizer iterations, wall-clock time.

## Suggested toy graphs & hyperparameters

- Small graphs: $C_4$ (4-cycle), $K_3$, $K_4$, random $G(6,0.5)$.
- Shots: 1024 for sampling experiments.
- Optimizers: COBYLA, Nelder–Mead, or gradient-based (Adam) if analytic gradients available.
- QAOA depths: $p=1,2,3$ for early experiments.
- Warm-start: $\beta \approx \pi/4$, $\gamma \approx \pi/(4\cdot\text{degree-mean})$.

## Notebooks / .iphyn files

The `notebooks/` folder already lists per-SDK `.iphyn` files. Use these to:
- encode the problem instance (nodes, edges, weights, seed),
- include example parameter sets and expected outputs (best bitstrings) for reproducibility,
- demonstrate how to load the same instance across different SDKs.

Example `maxcut_*.iphyn` fields (JSON-like):
- name, nodes, edges (i, j, w), seed, recommended $p$, recommended initial $(\gamma,\beta)$.

## Testing & CI recommendations

- Add unit tests that validate graph → Hamiltonian → QAOA mapping for canonical graphs ($C_3$, $C_4$).
- Small CI jobs should:
  - create a conda env using `utilities/<sdk>/conda_env.sh`,
  - run a quick example from `notebooks/` using a lightweight simulator (e.g., Pennylane `default.qubit` or Qiskit Aer).
- Container-based CI: use `*_container.def` recipes to produce deterministic test environments when available.

## Files to add or verify

- utilities/shared/graph.py — graph creation utilities (C_n, K_n, G(n,p))
- utilities/shared/convert.py — graph ↔ QUBO/Ising converters, cost evaluator
- utilities/<sdk>/conda_env.sh — environment creation script (already present for qiskit and qulacs)
- utilities/<sdk>/*_container.def — container recipes (already present for qiskit and qulacs)
- notebooks/*.iphyn — problem instance files (already listed)

## References

- E. Farhi, J. Goldstone, S. Gutmann (2014), "A Quantum Approximate Optimization Algorithm"
- Qiskit and PennyLane QAOA tutorials and docs

---
License
- Placeholder: will be updated.

Contact
- Repository owner: @mehmetniyazikayi
- For questions, open an issue or pull request.

