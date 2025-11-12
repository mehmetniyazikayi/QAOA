# Quantum Approximate Optimization Algorithm (QAOA)

## General Description

The Quantum Approximate Optimization Algorithm (QAOA) is a hybrid quantum–classical variational algorithm designed to solve combinatorial optimization problems that can be written as Quadratic Unconstrained Binary Optimization (QUBO) models.

The core idea of QAOA is to encode the objective function of a classical problem into a quantum mechanical energy landscape and to search for its ground state — the configuration of minimal energy, corresponding to the optimal or near-optimal solution.

These problems aim to find a binary configuration x = (x₁, x₂, …, xₙ) that minimizes a given cost function:

C(x) = Σ<sub>i,j</sub> Q<sub>ij</sub> x<sub>i</sub> x<sub>j</sub> + Σ<sub>i</sub> q<sub>i</sub> x<sub>i</sub>

Formally, this can be expressed as:

C(x) = xᵀQx ,  x<sub>i</sub> ∈ {0,1}

which can be mapped to a quantum Hamiltonian H<sub>C</sub> whose ground state encodes the optimal solution.

QAOA searches for this ground state using a parameterized quantum circuit that alternates between two Hamiltonians:

1. The cost Hamiltonian H<sub>C</sub> — encodes the problem objective  
2. The mixer Hamiltonian H<sub>M</sub> — promotes exploration between bitstrings

By applying these unitaries repeatedly and optimizing their parameters with a classical optimizer, QAOA biases the quantum state toward the optimal or near-optimal solution.

QAOA combines the strengths of both paradigms:

- Quantum mechanics provides a large Hilbert space in which all possible solutions coexist in superposition and evolve under interference.
- Classical optimization guides the search by iteratively updating parameters to minimize the measured energy.
- Variational design (VQA) makes QAOA practical for today’s noisy intermediate-scale quantum (NISQ) devices by requiring only shallow, parameterized circuits.

---

## Why QAOA

Classical algorithms for NP-hard problems (e.g., simulated annealing, tabu search, genetic algorithms) explore the search space sequentially or heuristically. For large-scale problems, the number of feasible configurations grows exponentially, and even advanced heuristics struggle to find optimal or near-optimal solutions.

QAOA provides several major advantages:

1. **Quantum Parallelism**  
   The quantum state encodes all possible solutions simultaneously, exploring an exponentially large space in one coherent evolution.

2. **Constructive Interference**  
   Proper parameter choices cause good solutions to interfere constructively while suppressing poor ones, concentrating probability near low-energy states.

3. **Adaptability**  
   Any optimization problem expressible as a QUBO or an Ising Hamiltonian can be embedded into QAOA by defining a suitable cost Hamiltonian.

4. **Near-term Feasibility**  
   QAOA circuits are relatively shallow (often depth p = 1–3), which makes them executable on current NISQ hardware.

5. **Hybrid Optimization Loop**  
   The computationally expensive parameter optimization runs classically, while the quantum processor is used only for evaluating expectation values ⟨H<sub>C</sub>⟩.

---

## Theoretical Foundation

### From Classical Optimization to Quantum Hamiltonian

1. **Start from the QUBO form**

Any combinatorial optimization problem can be written as a Quadratic Unconstrained Binary Optimization (QUBO) problem:

min<sub>x∈{0,1}ⁿ</sub> C(x) = xᵀQx

2. **Map binary variables to spins**

Binary variables x<sub>i</sub> ∈ {0,1} are replaced by spin variables σ<sup>z</sup><sub>i</sub> ∈ {−1,+1}:

x<sub>i</sub> = (1 − σ<sup>z</sup><sub>i</sub>) / 2

Substituting this relation transforms the cost function into an Ising Hamiltonian:

H<sub>C</sub> = Σ<sub>i<j</sub> J<sub>ij</sub> σ<sup>z</sup><sub>i</sub> σ<sup>z</sup><sub>j</sub> + Σ<sub>i</sub> h<sub>i</sub> σ<sup>z</sup><sub>i</sub>

Here, J<sub>ij</sub> and h<sub>i</sub> are determined by the elements of Q.

3. **Ground state → optimal solution**

The bitstring that minimizes C(x) corresponds to the ground state of H<sub>C</sub>. Thus, finding the optimal solution becomes equivalent to finding the ground state energy of the system.

---

### Variational Ansatz

QAOA prepares a parameterized quantum state that approximates the ground state of H<sub>C</sub>. It alternates between evolutions under the cost Hamiltonian H<sub>C</sub> and the mixer Hamiltonian H<sub>M</sub>:

|Ψ(γ, β)⟩ = ∏<sub>l=1</sub><sup>p</sup> e<sup>−i β<sub>l</sub> H<sub>M</sub></sup> e<sup>−i γ<sub>l</sub> H<sub>C</sub></sup> |s⟩

where:

- p is the number of layers (also called **depth**)  
- γ = (γ₁, …, γ<sub>p</sub>) and β = (β₁, …, β<sub>p</sub>) are real-valued parameters  
- |s⟩ = H<sup>⊗n</sup> |0⟩<sup>⊗n</sup> is the uniform superposition of all computational basis states  
- H<sub>C</sub> encodes the problem objective  
- H<sub>M</sub> = Σ<sub>i</sub> X<sub>i</sub> (where X<sub>i</sub> are Pauli-X operators) serves as a mixing Hamiltonian that flips qubits

The expectation value of H<sub>C</sub> under this state,

F<sub>p</sub>(γ, β) = ⟨Ψ(γ, β)| H<sub>C</sub> |Ψ(γ, β)⟩

is minimized with respect to γ and β by a classical optimizer.

---

## The Algorithm

1. **Problem encoding:**  
   Convert the classical optimization task into a QUBO or Ising model, obtaining the cost Hamiltonian H<sub>C</sub>.

2. **Build the ansatz (parameterized quantum circuit):**  
   Construct the alternating sequence of unitaries e<sup>−i γ<sub>l</sub> H<sub>C</sub></sup> and e<sup>−i β<sub>l</sub> H<sub>M</sub></sup>, applied to the initial state |s⟩.

3. **Execute circuit and measure:**  
   Run the quantum circuit on a simulator or device to estimate the expectation value ⟨H<sub>C</sub>⟩.

4. **Classical optimization:**  
   Use a classical optimizer (COBYLA, SPSA, etc.) to adjust (γ, β) to minimize ⟨H<sub>C</sub>⟩.

5. **Convergence and measurement:**  
   Once convergence is reached, measure the final state multiple times to obtain bitstrings. The bitstring corresponding to the lowest energy is the approximate solution to the original optimization problem.

---

## The QAOA Quantum Circuit

A QAOA circuit with depth p = 1 consists of the following layers:

1. **Initialization:**  
   All qubits start in the |0⟩ state, then Hadamard gates prepare a uniform superposition  
   |s⟩ = H<sup>⊗n</sup> |0⟩<sup>⊗n</sup>.

2. **Cost Hamiltonian layer:**  
   Applies a phase based on the cost function:

   U<sub>C</sub>(γ) = e<sup>−i γ H<sub>C</sub></sup>

   For a two-qubit term J<sub>ij</sub> Z<sub>i</sub> Z<sub>j</sub>, this is implemented as:

   CNOT(i, j) → RZ(2γJ<sub>ij</sub>) → CNOT(i, j)

   Single-qubit bias terms h<sub>i</sub> Z<sub>i</sub> become RZ(2γh<sub>i</sub>) rotations.

3. **Mixer Hamiltonian layer:**  
   Applies X-rotations that mix the basis states:

   U<sub>M</sub>(β) = e<sup>−i β H<sub>M</sub></sup> = ∏<sub>i</sub> R<sub>X</sub>(2β)

4. **Measurements:**  
   The qubits are measured in the computational basis. The most frequently observed bitstrings correspond to low-energy solutions.

---

## Detailed Workflow

| **Step** | **Process** | **Description** |
|-----------|--------------|-----------------|
| **1. Problem Encoding** | Define cost function C(x) | Formulate the classical optimization problem and express it as a QUBO:<br> C(x) = xᵀQx.<br>Map to Ising form H<sub>C</sub> = Σ<sub>i,j</sub>J<sub>ij</sub>Z<sub>i</sub>Z<sub>j</sub> + Σ<sub>i</sub>h<sub>i</sub>Z<sub>i</sub>. |
| **2. Circuit Construction** | Build the QAOA ansatz | Prepare the uniform superposition |s⟩ = H<sup>⊗n</sup>|0⟩ and construct *p* alternating layers of cost and mixer unitaries:<br>U<sub>C</sub>(γ) = e<sup>−iγH<sub>C</sub></sup>, U<sub>M</sub>(β) = e<sup>−iβH<sub>M</sub></sup>. |
| **3. Quantum Execution** | Evaluate the cost expectation | Run the QAOA circuit on a simulator or quantum backend and measure the expected energy ⟨H<sub>C</sub>⟩. |
| **4. Classical Optimization** | Parameter update loop | Use a classical optimizer (COBYLA, SPSA, BFGS, etc.) to update parameters (γ, β) to minimize ⟨H<sub>C</sub>⟩. Rebuild and re-run the circuit after each update. |
| **5. Convergence & Measurement** | Final state sampling | Once convergence is reached, measure the final state repeatedly to obtain bitstrings. The bitstring(s) with the lowest energy correspond to approximate or optimal solutions. |
| **6. Decoding** | Map back to classical solution | Interpret the output bitstring according to the original problem — e.g., a graph partition, schedule, or assignment. |

---

## Intuitive Picture
Think of QAOA as a quantum analogue of classical simulated annealing:

*    The cost Hamiltonian guides the system toward low-energy (good) solutions.
*    The mixer Hamiltonian injects “quantum motion” that allows exploration of the space.
*    The alternation between the two mimics cooling: as parameters optimize, probability density accumulates in regions of low energy.

For small depth $p$, QAOA yields approximate solutions; as $p\rightarrow ∞$, it approaches the exact ground state solution.

### Pros. & Cons.
Advantages

*   Works on today’s hardware (NISQ-ready).

*	General framework — applicable to any QUBO-formulated problem.

*	Tunable trade-off between circuit depth and solution quality.

*	Naturally hybrid: leverages both quantum and classical resources.

Limitations

*	Performance depends strongly on the choice of initial parameters and optimizer.

*	Quantum noise can affect the accuracy of measured energies.

*	Number of qubits required grows with problem size (scalability challenge).
