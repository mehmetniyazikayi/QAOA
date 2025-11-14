#!/bin/bash
set -e

ENV_NAME="qiskitenv"

# Create environment
conda create -y -n "$ENV_NAME" python=3.10

# Activate it
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# Install SDK-specific dependencies
pip install --no-cache-dir -r requirements.txt

echo "Environment '$ENV_NAME' created and ready."

