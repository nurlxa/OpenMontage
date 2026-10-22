#!/bin/bash
# Installs the tools for the TikTok devlog videos (see docs/tiktok-roblox/devlog-editor/).
# Runs only in Claude Code cloud sessions. Safe to run more than once.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# ffmpeg (renders and audio mixing)
if ! command -v ffmpeg >/dev/null 2>&1; then
  (apt-get update -qq && apt-get install -y -qq ffmpeg) >/dev/null 2>&1 || echo "warning: could not install ffmpeg"
fi

# Python packages: narrator voice, word timing, frame rendering
PIP_ROOT_USER_ACTION=ignore python3 -m pip install -q --disable-pip-version-check \
  kokoro-onnx soundfile faster-whisper opencv-python-headless pillow scipy numpy pyloudnorm 2>&1 | grep -v "already satisfied" || true

# Kokoro narrator voice model files
mkdir -p "$HOME/kokoro"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  if [ ! -s "$HOME/kokoro/$f" ]; then
    curl -sSfL -o "$HOME/kokoro/$f.part" \
      "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f" \
      && mv "$HOME/kokoro/$f.part" "$HOME/kokoro/$f" || echo "warning: could not download $f"
  fi
done

# Lilita One font (captions and titles)
mkdir -p "$HOME/fonts"
if [ ! -s "$HOME/fonts/LilitaOne.ttf" ]; then
  curl -sSfL -o "$HOME/fonts/LilitaOne.ttf" \
    "https://raw.githubusercontent.com/google/fonts/main/ofl/lilitaone/LilitaOne-Regular.ttf" \
    || echo "warning: could not download Lilita One font"
fi

# Whisper model for word timestamps (downloaded once, then cached)
python3 -c "from faster_whisper import WhisperModel; WhisperModel('small.en', device='cpu', compute_type='int8')" \
  >/dev/null 2>&1 || echo "warning: could not pre-download whisper small.en"

echo "devlog video tools ready"
