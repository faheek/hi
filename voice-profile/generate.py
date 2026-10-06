#!/usr/bin/env python3
"""Generate new narration using the saved recording as a voice reference."""

import argparse
import hashlib
import json
from pathlib import Path
import wave

import numpy as np
import sherpa_onnx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--models-dir", type=Path,
                        default=Path("/workspace/shared/voice-tools/models"))
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("The output already exists; choose a new filename.")
    if args.threads < 1:
        parser.error("Threads must be at least 1.")

    root = Path(__file__).resolve().parent
    profile = json.loads((root / "profile.json").read_text(encoding="utf-8"))
    reference_path = root / profile["reference_audio"]
    if hashlib.sha256(reference_path.read_bytes()).hexdigest() != profile["reference_sha256"]:
        raise ValueError("The saved reference audio does not match the profile.")
    with wave.open(str(reference_path)) as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("Expected a mono PCM16 reference WAV.")
        sample_rate = wav.getframerate()
        reference = np.frombuffer(wav.readframes(wav.getnframes()), np.int16)
        reference = reference.astype(np.float32) / 32768

    text = args.text_file.read_text(encoding="utf-8").strip()
    if not text:
        parser.error("The narration text file is empty.")
    base = args.models_dir / profile["generation"]["model_directory"]
    for name, expected in profile["generation"]["model_sha256"].items():
        path = args.models_dir / name
        with path.open("rb") as data:
            actual = hashlib.file_digest(data, "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"Model checksum mismatch: {path}")
    config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            zipvoice=sherpa_onnx.OfflineTtsZipvoiceModelConfig(
                tokens=str(base / "tokens.txt"),
                encoder=str(base / "encoder.onnx"),
                decoder=str(base / "decoder.onnx"),
                data_dir=str(base / "espeak-ng-data"),
                lexicon=str(base / "lexicon.txt"),
                vocoder=str(args.models_dir / "vocos_24khz.onnx"),
            ),
            num_threads=args.threads,
            provider="cpu",
        )
    )
    if not config.validate():
        raise ValueError("Model files are missing or invalid; see README.md.")
    tts = sherpa_onnx.OfflineTts(config)
    generation = sherpa_onnx.GenerationConfig()
    generation.reference_audio = reference
    generation.reference_sample_rate = sample_rate
    generation.reference_text = profile["reference_text"]
    generation.num_steps = profile["generation"]["num_steps"]
    generation.extra["min_char_in_sentence"] = "300"
    audio = tts.generate(text, generation)
    if not len(audio.samples):
        raise RuntimeError("The model produced no audio.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as output:
        with wave.open(output, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(audio.sample_rate)
            samples = np.asarray(audio.samples)
            wav.writeframes((np.clip(samples, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"Saved voice-cloned narration: {args.output}")
    print("New narration is an approximation of the saved voice, not an unchanged recording.")


if __name__ == "__main__":
    main()
