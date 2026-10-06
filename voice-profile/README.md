# Saved narration voice

The preferred voice is the user's own voice from `Recording (5).m4a`, saved here as `original-recording.m4a`. This is the recording used in `How_Caching_Prevents_Database_Crashes_your_recording.mp4`. Earlier generated videos and the JSON Web Token recording are not the preferred reference.

`profile.json` defines the reusable reference. `reference.wav` contains an 8.67-second excerpt from the original recording, and `reference.txt` contains its checked spoken text. The full original recording is retained unchanged; hashes in the profile identify these files.

This is a saved reference for zero-shot voice cloning, not a separately trained voice model. It can condition a model to speak new words, but an exact voice match is not guaranteed. Using a new recording of the user reading the complete target script preserves their actual voice.

The bundled generator is experimental. Its sample generation and decoding completed, but the transcription check flagged a possible extra word. Check word accuracy and voice likeness for each generated clip before using it in a video. The saved original recording and reference excerpt were verified independently of this synthesis test.

For a future edit, use the saved profile when the user requests their saved voice. Preserve the video's original words and visuals by default. Extract and verify the target script before generating speech. For a matching user recording, use the recording directly instead of synthesizing speech. Check timing before replacing audio; do not silently truncate narration, change the video, or change the pitch or speed of an actual recording. Only shorten quiet pauses when needed and verify all spoken content remains.

## Generate new narration

The current cloud workspace has the required runtime under `/workspace/shared/voice-tools/python` and models under `/workspace/shared/voice-tools/models`. From `/workspace/hi`:

```bash
PYTHONPATH=/workspace/shared/voice-tools/python python3 voice-profile/generate.py \
  --text-file /workspace/outputs/new-script.txt \
  --output /workspace/outputs/new-narration.wav
```

Use a new output filename. The helper checks the reference and model hashes and generates a WAV; it does not overwrite the video or existing recordings. Pass `--models-dir` to use another model cache.

If the runtime or models are absent, prepare them outside the checkout:

```bash
mkdir -p /workspace/shared/voice-tools/models
python3 -m pip install --target /workspace/shared/voice-tools/python sherpa-onnx==1.13.8 numpy
curl --fail --location --output /workspace/shared/voice-tools/models/zipvoice.tar.bz2 \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-zipvoice-distill-fp32-zh-en-emilia.tar.bz2
tar -xjf /workspace/shared/voice-tools/models/zipvoice.tar.bz2 -C /workspace/shared/voice-tools/models
curl --fail --location --output /workspace/shared/voice-tools/models/vocos_24khz.onnx \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/vocoder-models/vocos_24khz.onnx
```

The helper verifies the installed model files against the profile before using them. Keep TLS and hash verification enabled. Missing access or mismatched files require diagnosis, not disabling verification.

For real recorded narration in M4A/AAC format that fits the video, copy both streams into a new video:

```bash
ffmpeg -nostdin -i input-video.mp4 -i matching-recording.m4a \
  -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart output-video.mp4
```

Verify the final spoken content, duration, and decoding, and compare the video stream hash with the input. Label generated narration as voice-cloned rather than an unchanged recording. Keep generated exports separate from the saved voice assets.
