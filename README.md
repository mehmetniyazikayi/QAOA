# QAOA — Quantum Approximate Optimization Algorithm

A compact, hands-on implementation and set of notebooks for exploring the Quantum Approximate Optimization Algorithm (QAOA) with Qiskit. This repository provides educational notebooks, example scripts and utilities for:

- encoding QUBO/Ising problems,
- building QAOA circuits,
- running them on simulators and (optionally) real quantum backends,
- visualizing and analyzing results.

---

Table of contents
- Overview
- Quickstart
- Algorithm flow (visual)
- QAOA circuit (visual)
- Implementation notes
- Examples & notebooks
- Tips & best practices
- Contributing
- License
- References
- Contact

---

## Overview

QAOA is a hybrid quantum–classical variational algorithm for approximately solving combinatorial optimization problems that can be expressed as QUBO or Ising models. The algorithm alternates between applying the cost (problem) Hamiltonian and a mixer Hamiltonian to bias the quantum state toward low-energy solutions, while a classical optimizer updates parameters to minimize the measured energy.

---

## Quickstart

Prerequisites
- Git
- Python 3.10+ (3.12 recommended where supported)
- Conda or virtualenv recommended
- (Optional) IBM Quantum account for running on real devices

Clone the repo
```bash
git clone https://github.com/mehmetniyazikayi/QAOA.git
cd QAOA
```

Create environment (conda example)
```bash
conda create --name qaoa-env python=3.12 -y
conda activate qaoa-env
pip install -r requirements.txt
# or, if no requirements.txt:
# pip install qiskit qiskit-aer qiskit-ibm-runtime qiskit-algorithms numpy scipy matplotlib notebook
```

Run notebooks
```bash
jupyter notebook
# or
jupyter lab
```
Open the notebooks/ directory and run them in order. Start with `notebooks/01_intro_qaoa.ipynb`.

Example script (replace with actual script names in the repo)
```bash
python examples/run_qaoa_simple.py --problem data/sample_qubo.json --p 1 --shots 1024
```

---

## Algorithm flow 

A compact visual of the hybrid classical–quantum loop. This is your ASCII diagram, slightly cleaned for alignment and readability:
```

Classical Computer                     Quantum Processor
─────────────────────────────────────────────────────────────
 Define H_C, H_M                      Prepare |s⟩ (Hadamards)
          │                                     │
          ▼                                     ▼
 Choose (γ, β) parameters     ───►   Apply U_C(γ), U_M(β)
          │                                     │
          │                        ◄───   Measure ⟨H_C⟩
          ▼
 Update parameters via optimizer
          │
 ─────────┴───────── Repeat until convergence ─────────►

``` 

Step-by-step (expanded)
1. Classical: choose or update parameters $(γ, β)$  
2. Quantum: prepare $|s⟩$ and apply alternating unitaries $U_C$, $U_M$ with given parameters  
3. Quantum: measure to estimate $⟨H_C⟩$ (expectation of the cost Hamiltonian)  
4. Classical: evaluate cost, update parameters using an optimizer (COBYLA, SPSA, etc.)  
5. Repeat until convergence or stopping condition

---

## QAOA circuit (p = 1) 

- Initialization: apply H^⊗n to $|0⟩^⊗n$ to prepare $|s⟩$ (uniform superposition)  
- Cost layer $U_C(γ)$: implement $ZZ$ coupling terms $(J_ij Z_i Z_j)$ and Z-bias terms $(h_i Z_i)$. Typical implementation for a two-qubit $ZZ$ term:
  $CNOT(i, j) → RZ(2γ J_ij)$ on qubit $j → CNOT(i, j)$
- Mixer layer $U_M(β)$: apply $RX(2β)$ on every qubit (implements $e^{-i β Σ_i X_i}$)
- Measurement: measure qubits in the computational basis; collect bitstrings and estimate energies

Simple ASCII circuit (p = 1)
```
q0: ──H───■────RZ(θ)──■───Rx(φ)───M──
          │            │
q1: ──H───■────RZ(θ)──■───Rx(φ)───M──
``` 
Notes:
- Each two-qubit $J_{ij}$ term maps to a $CNOT—RZ—CNOT$ sequence.
- Single-qubit bias $h_i$ maps to a single $RZ$ rotation.

---

## Implementation notes

- Binary-to-spin mapping:
  $x_i ∈ {0,1} → σ^z_i ∈ {−1,+1}$ with $x_i = (1 − σ^z_i) / 2$
- Cost Hamiltonian $H_C$ built from the QUBO matrix Q and single-qubit biases
- Mixer Hamiltonian $H_M$ typically is $∑_i X_i$ (single-qubit $RX$ rotations). Custom mixers are possible for problem-specific constraints.
- Variational ansatz (depth p):
  $Ψ(γ, β) = ∏_{l=1..p} e^{-i β_l H_M} e^{-i γ_l H_C} |s⟩$
- Objective: minimize $F_p(γ, β) = ⟨Ψ(γ,β)| H_C |Ψ(γ,β)⟩$ using a classical optimizer

Practical considerations
- Start with p = 1 or 2 to gain intuition. Increasing p can improve solutions but increases circuit depth and optimizer complexity.
- Use simulators (qiskit-aer) for parameter sweeps and debugging.
- When running on real hardware, use small instances and apply error mitigation strategies.

---

## Using IBM Quantum backends (optional)

1. Install and configure IBM credentials (see qiskit-ibm-runtime docs).
2. Example usage in a notebook/script:
```python
from qiskit_ibm_runtime import IBMProvider
provider = IBMProvider()
backend = provider.backends(simulator=False)[0]  # choose an available device
```
3. Prefer small instances on real devices; apply error mitigation and keep circuits shallow.

---

## Tips & best practices

- Reuse good parameters as initial guesses when increasing p.
- For noisy hardware, reduce depth and apply mitigation.
- Use random restarts or multiple optimizers if stuck in local minima.
- Record measurement seeds and optimizer states for reproducibility.

---

## Contributing

Contributions are welcome — issues, feature requests and PRs:
- Open an issue describing the problem or feature.
- Fork the repo, create a topic branch, and open a PR with a clear description and tests/examples where applicable.
- Use descriptive commit messages and include tests or example notebooks where relevant.

---

## License

- Placeholder: will be updated.

---

## References

- QAOA original paper: E. Farhi et al., "A Quantum Approximate Optimization Algorithm", 2014.
- Qiskit documentation and tutorials: https://qiskit.org/documentation

---

## Contact

- Repository owner: @mehmetniyazikayi  
- For questions, open an issue or pull request.
