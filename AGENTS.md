# Video editing preferences

The user requested that future video voice updates use their saved voice reference at `voice-profile/profile.json`. Read `voice-profile/README.md` before using it. The preferred source is their own `Recording (5).m4a`, saved as `voice-profile/original-recording.m4a`, rather than the earlier JSON Web Token narrator or generated voice approximations.

Preserve the original video visuals and spoken words by default. A saved voice reference can generate new narration only through voice cloning; do not promise an exact voice match or describe generated audio as an unchanged user recording. When the user provides a matching narration recording, use their actual recording directly and preserve its pitch and speech speed. Investigate duration differences before making timing changes, and never drop spoken content to make a recording fit.

The bundled synthesis helper is experimental. Validate generated words and voice likeness before using its output; its initial sample produced a possible extra token in the automated transcription check.

The cloud task already has an isolated checkout. Use it; do not create a Git worktree unless explicitly requested. Write edited videos to new filenames and preserve existing media, user changes, and voice reference files.
