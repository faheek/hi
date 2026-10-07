#!/usr/bin/env python3
"""Generate new narration using the saved recording as a voice reference."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
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
    parser.add_argument("--model", choices=["distill", "full"], default="distill",
                        help="Use the accepted default or the word accuracy fallback.")
    parser.add_argument("--pronunciations", type=Path,
                        help="Supplemental lexicon entries for the target script.")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("The output already exists; choose a new filename.")
    if args.threads < 1:
        parser.error("Threads must be at least 1.")

    root = Path(__file__).resolve().parent
    profile = json.loads((root / "profile.json").read_text(encoding="utf-8"))
    source_path = root / profile["source_audio"]
    with source_path.open("rb") as data:
        if hashlib.file_digest(data, "sha256").hexdigest() != profile["source_sha256"]:
            raise ValueError("The saved source recording does not match the profile.")
    reference_path = root / profile["reference_audio"]
    if hashlib.sha256(reference_path.read_bytes()).hexdigest() != profile["reference_sha256"]:
        raise ValueError("The saved reference audio does not match the profile.")
    with wave.open(str(reference_path)) as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("Expected a mono PCM16 reference WAV.")
        sample_rate = wav.getframerate()
        if sample_rate != profile["reference_sample_rate"]:
            raise ValueError("The reference sample rate does not match the profile.")
        if abs(wav.getnframes() / sample_rate - profile["reference_duration_seconds"]) > 1 / sample_rate:
            raise ValueError("The reference duration does not match the profile.")
        reference = np.frombuffer(wav.readframes(wav.getnframes()), np.int16)
        reference = reference.astype(np.float32) / 32768

    text = args.text_file.read_text(encoding="utf-8").strip()
    if not text:
        parser.error("The narration text file is empty.")
    settings = profile["generation"]
    if args.model == "full":
        settings = settings["fallback"]
    base = args.models_dir / settings["model_directory"]
    frontend = args.models_dir / settings["frontend_directory"]
    for name, expected in settings["model_sha256"].items():
        path = args.models_dir / name
        with path.open("rb") as data:
            actual = hashlib.file_digest(data, "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"Model checksum mismatch: {path}")
    pronunciations = args.pronunciations or root / settings["pronunciations"]
    with tempfile.TemporaryDirectory(prefix="saved-voice-") as temporary:
        lexicon = Path(temporary) / "lexicon.txt"
        lexicon.write_text(
            (frontend / "lexicon.txt").read_text(encoding="utf-8")
            + "\n" + pronunciations.read_text(encoding="utf-8") + "\n",
            encoding="utf-8",
        )
        config = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                zipvoice=sherpa_onnx.OfflineTtsZipvoiceModelConfig(
                    tokens=str(base / "tokens.txt"),
                    encoder=str(base / settings["encoder"]),
                    decoder=str(base / settings["decoder"]),
                    data_dir=str(frontend / "espeak-ng-data"),
                    lexicon=str(lexicon),
                    vocoder=str(args.models_dir / settings["vocoder"]),
                ),
                num_threads=args.threads,
                provider="cpu",
            ),
        )
        if not config.validate():
            raise ValueError("Model files are missing or invalid; see README.md.")
        tts = sherpa_onnx.OfflineTts(config)
        generation = sherpa_onnx.GenerationConfig()
        generation.reference_audio = reference
        generation.reference_sample_rate = sample_rate
        generation.reference_text = profile["reference_text"]
        generation.num_steps = settings["num_steps"]
        generation.extra["guidance_scale"] = str(settings["guidance_scale"])
        generation.extra["min_char_in_sentence"] = "300"
        generation.extra["max_char_in_sentence"] = "500"
        audio = tts.generate(text, generation)
    if not len(audio.samples):
        raise RuntimeError("The model produced no audio.")
    samples = np.asarray(audio.samples)
    if not np.all(np.isfinite(samples)):
        raise RuntimeError("The model produced invalid samples.")
    peak = np.max(np.abs(samples))
    if peak > .98:
        samples = samples * (.98 / peak)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as output:
        with wave.open(output, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(audio.sample_rate)
            wav.writeframes((samples * 32767).astype(np.int16).tobytes())
    print(f"Saved voice-cloned narration: {args.output}")
    print(f"Voice profile: {profile['name']}; model: {args.model}; reference: {profile['reference_audio']}")


if __name__ == "__main__":
    main()
