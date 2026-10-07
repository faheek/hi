# Video editing preferences

The user requested that future video voice updates use the default at `voice-profile/profile.json`. Read `voice-profile/README.md` before using it. On 2026-10-07, they approved the voice in `How_Apps_Survive_10000_Sudden_Users_Project46_voice_v2.mp4` and requested it for future edits. Use its Project 46 source recording and reference excerpt, saved as `voice-profile/project46-original.m4a` and `voice-profile/project46-reference.wav`. This preference supersedes the earlier `Recording (5).m4a` profile, which remains archived.

Preserve the original video visuals and spoken words by default. A saved voice reference can generate new narration only through voice cloning; do not promise an exact voice match or describe generated audio as an unchanged user recording. When the user provides a matching narration recording, use their actual recording directly and preserve its pitch and speech speed. Investigate duration differences before making timing changes, and never drop spoken content to make a recording fit.

Validate generated words and voice likeness for each new clip. The default uses the accepted video's ZipVoice distill settings; the full model is available for sentences with word accuracy problems. `voice-profile/accepted-video-recipe.json` records the approved video's settings. Apply pronunciation overrides according to word meaning; in particular, the adjective “live” and the verb “live” have different pronunciations.

The cloud task already has an isolated checkout. Use it; do not create a Git worktree unless explicitly requested. Write edited videos to new filenames and preserve existing media, user changes, and voice reference files.
