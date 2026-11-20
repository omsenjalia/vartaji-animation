#!/usr/bin/env bash
set -e
echo "Starting Indic-Parler-TTS installation in WSL..."
mkdir -p ~/.venvs
if [ ! -d ~/.venvs/vartaji-tts ]; then
  python3 -m venv ~/.venvs/vartaji-tts
fi
source ~/.venvs/vartaji-tts/bin/activate
echo "Upgrading pip..."
pip install --upgrade pip
echo "Installing PyTorch with CUDA 12.4..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
echo "Installing transformers, soundfile, sentencepiece, accelerate..."
pip install transformers soundfile sentencepiece accelerate
echo "Installing parler-tts from huggingface git..."
pip install git+https://github.com/huggingface/parler-tts.git
echo "Verifying installation..."
python3 -c "import torch, parler_tts, transformers, soundfile; print('SUCCESS: PyTorch CUDA available:', torch.cuda.is_available(), 'Parler-TTS ready!')"
echo "TTS_SETUP_COMPLETE"
