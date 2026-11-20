#!/usr/bin/env bash
set -e
echo "Starting Indic-Parler-TTS installation in WSL via uv..."
mkdir -p ~/.venvs
if [ ! -d ~/.venvs/vartaji-tts ]; then
  python3 -m venv ~/.venvs/vartaji-tts
fi
UV_BIN="$HOME/.local/bin/uv"
if ! command -v "$UV_BIN" &> /dev/null; then
  UV_BIN="uv"
fi
echo "Using uv at: $UV_BIN"
echo "Installing PyTorch with CUDA 12.4..."
"$UV_BIN" pip install --python ~/.venvs/vartaji-tts/bin/python torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
echo "Installing transformers, soundfile, sentencepiece, accelerate, and parler-tts..."
"$UV_BIN" pip install --python ~/.venvs/vartaji-tts/bin/python transformers soundfile sentencepiece accelerate "git+https://github.com/huggingface/parler-tts.git"
echo "Verifying installation..."
~/.venvs/vartaji-tts/bin/python -c "import torch, parler_tts, transformers, soundfile; print('SUCCESS: PyTorch CUDA available:', torch.cuda.is_available(), 'Parler-TTS ready!')"
echo "TTS_SETUP_COMPLETE"
