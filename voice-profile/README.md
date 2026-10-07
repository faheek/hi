# Saved narration voice

The default is the Project 46 voice used in `How_Apps_Survive_10000_Sudden_Users_Project46_voice_v2.mp4`. On 2026-10-07, the user confirmed that this video's voice matched their requested voice and asked to use it for future edits. This preference supersedes the earlier `Recording (5).m4a` profile.

`profile.json` selects `project46-reference.wav`: the exact 8.1-second, 24 kHz mono reference used for the approved video, beginning at 19.68 seconds in `(Audio) Video Project 46 (1).m4a`. Its checked transcript is in `project46-reference.txt`. The complete upload is retained unchanged as `project46-original.m4a`. Hashes identify both files. The previous profile and its recordings remain available in `previous-recording-profile.json`, `original-recording.m4a`, `reference.wav`, and `reference.txt`.

`accepted-video-recipe.json` records the approved output, reference, model settings, sentence timings, pronunciation overrides, and final audio processing. The first 12 sentences used ZipVoice distill with 8 steps and guidance 1.0; the final sentence used full ZipVoice with 16 steps and guidance 3.0 to improve word accuracy. Use the same reference for both models. This is a reusable reference for new narration, rather than a separately trained model.

For future edits, preserve the video's original words and visuals. Extract and verify its script, generate speech sentence by sentence, and check the spoken words, voice likeness, timing, and final decoding. Copy the video stream and compare its hash to the input. Keep every spoken word; do not silently truncate narration. When the user supplies a matching narration recording, use that recording directly and preserve its pitch and speech speed. Write new output filenames and retain existing media.

## Generate new narration

The current workspace has the runtime in `/workspace/shared/voice-tools/python` and models in `/workspace/shared/voice-tools/models`. From `/workspace/hi`:

```bash
PYTHONPATH=/workspace/shared/voice-tools/python python3 voice-profile/generate.py \
  --text-file /workspace/outputs/new-sentence.txt \
  --output /workspace/outputs/new-narration.wav
```

The helper verifies source, reference, and model hashes, uses the accepted distill settings, and generates a WAV without overwriting existing files. Pass `--model full` for a sentence needing the word accuracy fallback, or `--models-dir` for a different model cache. The full model uses the distill model's text frontend.

The default `pronunciations.txt` supplies the unstressed article “a”. For an auction script where “live” means real-time, pass `--pronunciations voice-profile/accepted-pronunciations-distill.txt`; the approved final sentence used `accepted-pronunciations-full.txt`, which also supplies “bid”. Do not apply the adjective “live” pronunciation to the verb “live”. Keep the original script text and apply pronunciation entries only where appropriate.

If the runtime or models are missing, prepare them outside the checkout:

```bash
mkdir -p /workspace/shared/voice-tools/models
python3 -m pip install --target /workspace/shared/voice-tools/python sherpa-onnx==1.13.8 numpy
curl --fail --location --output /workspace/shared/voice-tools/models/zipvoice.tar.bz2 \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-zipvoice-distill-fp32-zh-en-emilia.tar.bz2
tar -xjf /workspace/shared/voice-tools/models/zipvoice.tar.bz2 -C /workspace/shared/voice-tools/models
curl --fail --location --output /workspace/shared/voice-tools/models/vocos_24khz.onnx \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/vocoder-models/vocos_24khz.onnx
```

For the optional full model:

```bash
curl --fail --location --output /workspace/shared/voice-tools/models/zipvoice-full.tar.bz2 \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-zipvoice-zh-en-emilia.tar.bz2
tar -xjf /workspace/shared/voice-tools/models/zipvoice-full.tar.bz2 -C /workspace/shared/voice-tools/models
```

Keep TLS and hash verification enabled. The helper checks the installed models against the profile before using them. Label generated narration as voice-cloned and keep exports separate from saved voice assets.
