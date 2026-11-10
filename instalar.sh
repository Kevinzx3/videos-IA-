#!/usr/bin/env bash
# Instala todo lo necesario (Linux/macOS). Requiere python3, ffmpeg y node.
set -e
cd "$(dirname "$0")"
pip install piper-tts numpy pillow
mkdir -p voces
if [ ! -f voces/es-carlfm-x-low.onnx ]; then
  curl -L -o /tmp/voz.tar.gz https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-es-carlfm-x-low.tar.gz
  tar xzf /tmp/voz.tar.gz -C voces
fi
(cd remotion && npm install)
echo "Listo."
