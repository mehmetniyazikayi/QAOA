#!/bin/sh

conda create --name qiskitenv 
python=3.12 conda activate qiskitenv
conda install notebook ipykernel
python -m ipykernel install --user --name qiskitenv --display-name "QiskitEnv"
pip install numpy scipy pandas qiskit[visualization]==1.4.3 qiskit-aer qiskit-ibm-runtime qiskit-algorithms qiskit-machine-learning qiskit-nature qiskit-optimization qiskit-finance qiskit-dynamics
