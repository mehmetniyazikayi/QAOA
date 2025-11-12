# The **Quantum Approximate Optimization Algorithm (QAOA)** 

## General Description

The Quantum Approximate Optimization Algorithm (QAOA) is a hybrid quantum–classical variational algorithm designed to solve combinatorial optimization problems that can be written as Quadratic Unconstrained Binary Optimization (QUBO) models.The core idea of the **QAOA** is to encode the objective function of a classical problem into a quantum mechanical energy landscape and to search for its ground state that the configuration of minimal energy, corresponding to the optimal or near-optimal solution. Problems where the goal is to find a configuration of binary variables that minimizes a given cost function, such as in Max-Cut, Traveling Salesman or Job Shop Scheduling.



**QAOA** searches for the ground state of $H_C$ using the variational quantum circuits that alternate between two Hamiltonians: a **cost Hamiltonian** $H_C$ (encoding the objective) and a **mixer Hamiltonian** $H_M$ (promoting exploration). The main goal is to find a binary string $x = (x_1, x_2, ... , x_n)$ that minimizes a given cost function:
            $C(x)= \sum_{i,j}Q_{ij}x_ix_j+\sum_{i}q_ix_i$

Formally, these problems can be expressed as a **Quandratic Unconstrained Binary Optimization (QUBO)**:
              $C(x)=x^TQx$     ,     $x_i$ $∈$ $\{0,1\}$
              
which can be mapped to a  quantum Hamiltonian $H_C$ whose ground state encodes the optimal solution. These kind of problems, typically NP-hard, appear in many areas, from graph partioning and scheduling to routing and resource allocation.

The algorithm alternates between two unitary transformations:

1. The **cost Hamiltonian** $H_C$, which encodes the problem objective
2. The **mixer Hamiltonian** $H_M$,  whcih drives transitions between different configurations(bitstrings).

By applying these operations repeatedly in a parametrized circuit and optimizing those parameters with a classcial optimizer, QAOA gradually biases the quantum state toward the optimal or near-optimal solution.

The **QAOA** combines the strengths of both paradigms:
*    **Quantum mechanics** provides a large Hilbert space in which all possible solutions can coexist as a superposition and evolve under interference.
*    **Classical optimization** guides the search by updating the parameters of the quantum circuit to iteratively minimize the expected energy.

The **QAOA** belongs to family of **Variational Quantum Algorithms (VQAs)**, which are particularly suited for today's noisy intermediate-scale quantum (NISQ) devices because they rely on shallow, parameterized circuits and can tolerate limited coherence times.

### Why QAOA ?

Classical algorithms for hard combinatorial problems, such as simulated annealing, tabu search or genetic algorithms, explore the solution space sequentially or heuristically. For large-scale problems, like the Job Shop Scheduling Problem (JSSP), the number of feasible schedules grows exponentially with the number of jobs and machines. Even state of the art classical heuristics struggle to find optimal or near-optimal solutions as instance sizes increase.

The **QAOA** is motivated by several key advantages:

**1. Quantum Parallelism**

The quantum state encodes all possible solutions simultaneously, allowing the algorithm to explore a vast search space in one coherent state evolution.

**2. Constructive Interference**

Through the choice of parameters, amplitudes associated with good solutions interfere constructively, while those of poor solutions interfere destructively. This effect concentrates measurement probabilities around low-energy(good) states

**3. Adaptability**

QAOA is problem-agnostic. Any optimization problem that can be expressed as a QUBO or and Ising Hamiltonian can be embedded into it by defining a suitable cost Hamiltonian.

**4. Near-term  Feasibility**

Most of the QAOA circuits are relatively shallow (often with depth p=1-3), they can run in current NISQ hardware, making them one of the few practically executable quantum algorithms available nowadays.

**5. Hybrid Optimization Loop**

The computationally expensive part(parameter optimization) is performed classically. The quantum hardware is only used for the energy evaluation step, which scales favorably in parallel with the number of qubits.

## Theoretical Foundation

### From Classical Optimization to Quantum Hamiltonian

* **1. Start from the QUBO form:**
    Any combinatorial optimization problem can be written as a Quadratic Unconstrained Binary Optimization (QUBO) problem:
        $\min_{x∈\{0,1\}^n} C(x)=x^TQx$
        
* **2. Map binary variables to spins:**
    Binary variables $x_i ∈\{0,1\}$ are replaced by spin variables ${\sigma}_i^z ∈\{-1,+1\}$:
    $x_i= \frac{1-{\sigma}_i^z}{2}$
    Substituting this relation transforms the cost function into an Ising Hamiltonian: $H_C = \sum_{i<j}J_{ij} {\sigma}_i^z{\sigma}_j^z + \sum_{i}h_i{\sigma}_i^z$
    Here $J_{ij}$ and $h_i$ are determined by the elements of $Q$.
    
* **3. Ground state $\rightarrow$ optimal solution:**
    The bitstring that minimizes $C(x)$ corresponds to ground state of $H_C$. Thus, finding the optimal solution becomes equivalent to finding the ground state energy of the system.
   

### Variational Ansatz

QAOA Prepares a parameterized quantum state that approximates the ground state of $H_C$. It alternates between evolutions under the **cost Hamiltonian** $H_C$ and the **mixer Hamiltonian** $H_M$:
    $$|{\Psi(\gamma,\beta)}\rangle=\prod_{l=1}^pe^{-i\beta_lH_M}e^{-i\gamma_lH_C}|s\rangle$$
    
where;
*    $p$ is the number of layers(also called depth),
*    $\gamma=(\gamma_1,...,\gamma_p)$ and $\beta=(\beta_1,...,\beta_p)$ are real-valued parameters,
*    $|s〉=H^{\otimes n}|0〉^{\otimes n}$ is the uniform superposition of all omputational basis states,
*    $H_C$ encodes the problem objective,
*    $H_M=\sum_{i}X_i$ (where $X_i$ are Pauli-X operators) serves as a mixing Hamiltonian that flips qubits.

The expectation value of $H_C$ under this state,
    $F_p(\gamma,\beta)=\langle{\Psi(\gamma,\beta)}|H_C|{\Psi(\gamma,\beta)}\rangle$
is minimized with respect to $\gamma$ and $\beta$ by a classical optimizer.

## The Algorithm 

* **1.)** Problem encoding:
Convert the classical optimization task into a QUBO or Ising model, obtaining the cost Hamiltonian $H_C$.
* **2.)** Build the ansatz(parametrized quantum circuit):
Construct the alternating  sequence of unitaries $e^{-i\gamma_lH_C}$ and $e^{-i\beta_lH_M}$, applied to the initial state $|s\rangle$.
* **3.)** Execute circuit and measure:
Run the quantum circuit on a simulator or device to estimate the expectation value ($H_C$).
* **4.)** Classical optimization:
Use a classical optimizer (COBYLA, etc.) to adjust the parameters $(\gamma,\beta)$ to minimize $H_C$.
* **5.)** Convergence and measurement:
Once convergence is reached, measure the final state multiple times to abtain bitstrings. The bitstring corresponding to the lowest energy is the approximate solution to the original optimization problem.

 Hybrid Quantum–Classical Optimization Loop



### The QAOA Quantum Circuit

A QAOA circuit with depth $p=1$ consists of the following layers:

**1. Initialization:**
All qubits start in the $|0\rangle$ state, then Hadamard gates prepare a uniform superposition $|s\rangle=H^{\otimes n}|0\rangle^{\otimes n}$.

**2. Cost Hamiltonian layer:**
Applies a phase based on the cost function:
$U_C(\gamma)=e^{-i\gamma H_C}$
For a two-qubit term $J_{ij}Z_iZ_j$ , this is implemented as

$CNOT(i,j)\rightarrow RZ(2\gamma J_{ij}) \rightarrow CNOT(i,j)$
Single-qubit bias terms $h_iZ_i$ become $RZ(2\gamma h_i)$ rotations.

**3. Mixer Hamiltonian layer:**
Applies X-rotations that mix the basis states:
$U_M(\beta)=e^{-i\beta H_M}= \prod_iR_X(2\beta)$

**4. Measurements:**
The qubits are measured in the computational basis. The most frequently observed bitstrings correspond to low-energy solutions.

### Detailed Workflow

| **Step** | **Process** | **Description** |
|-----------|--------------|-----------------|
| **1. Problem Encoding** | Define cost function C(x) | Formulate the classical optimization problem and express it as a QUBO: <br> C(x) = xᵀQx. <br> Map to Ising form H<sub>C</sub> = Σ<sub>i,j</sub>J<sub>ij</sub>Z<sub>i</sub>Z<sub>j</sub> + Σ<sub>i</sub>h<sub>i</sub>Z<sub>i</sub>. |
| **2. Circuit Construction** | Build the QAOA ansatz | Prepare the uniform superposition \|s⟩ = H<sup>⊗n</sup>\|0⟩ and construct *p* alternating layers of cost and mixer unitaries: <br> U<sub>C</sub>(γ) = e<sup>−iγH<sub>C</sub></sup>, U<sub>M</sub>(β) = e<sup>−iβH<sub>M</sub></sup>. |
| **3. Quantum Execution** | Evaluate the cost expectation | Run the QAOA circuit on a simulator or quantum backend and measure the expected energy ⟨H<sub>C</sub>⟩. |
| **4. Classical Optimization** | Parameter update loop | Use a classical optimizer (COBYLA, SPSA, BFGS, etc.) to update parameters (γ, β) to minimize ⟨H<sub>C</sub>⟩. Rebuild and re-run the circuit after each update. |
| **5. Convergence & Measurement** | Final state sampling | Once convergence is reached, measure the final state repeatedly to obtain bitstrings. The bitstring(s) with the lowest energy correspond to approximate or optimal solutions. |
| **6. Decoding** | Map back to classical solution | Interpret the output bitstring according to the original problem — e.g., a graph partition, schedule, or assignment. |



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
