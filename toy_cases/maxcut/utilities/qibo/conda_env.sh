#!/bin/bash
set -e

ENV_NAME="qiboenv"

conda create -y -n "$ENV_NAME" python=3.10

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

pip install --no-cache-dir -r requirements.txt

echo "Environment '$ENV_NAME' created and ready."

