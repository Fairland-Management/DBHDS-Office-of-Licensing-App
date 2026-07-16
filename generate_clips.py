#!/usr/bin/env python3
"""
Render studio-voice CLIPS for the WHOLE app — flashcards, reels, versus, Listen mode.

The app plays audio/<key>.mp3 if it exists, otherwise falls back to the robotic
on-device voice. So run this once (with your API key) and the boring audio is gone
everywhere you rendered.

QUICK START:
    pip install openai pydub        # ffmpeg too (macOS: brew install ffmpeg)
    export OPENAI_API_KEY="sk-...your key..."
    python generate_clips.py                 # render ALL 120 clips (~$1-2)
    python generate_clips.py flash           # only flashcards + Listen mode (27 clips)
    python generate_clips.py reel            # only Micro-Reels
    python generate_clips.py vs              # only Versus cards

Clips are written to an  audio/  folder next to the app. Re-running skips clips
that already exist, so it's cheap to render one group at a time.
Reads clips_manifest.json (regenerate that only if the app's content changes).
"""
import os, sys, io, json

PROVIDER = "openai"           # "openai" or "elevenlabs"
OPENAI_VOICE = "nova"         # single narrator for clips (warm, clear)
ELEVEN_VOICE = "Rachel"

HERE = os.path.dirname(os.path.abspath(__file__))

def synth_openai(text):
    from openai import OpenAI
    return OpenAI().audio.speech.create(model="gpt-4o-mini-tts", voice=OPENAI_VOICE, input=text).content

def synth_eleven(text):
    from elevenlabs.client import ElevenLabs
    return b"".join(ElevenLabs().text_to_speech.convert(voice_id=ELEVEN_VOICE, model_id="eleven_multilingual_v2", text=text))

def main():
    mani = os.path.join(HERE, "clips_manifest.json")
    if not os.path.exists(mani):
        sys.exit("clips_manifest.json not found (ask Claude to regenerate it).")
    items = json.load(open(mani))

    prefix = sys.argv[1] if len(sys.argv) > 1 else None
    if prefix:
        items = [x for x in items if x["key"].startswith(prefix)]

    synth = synth_openai if PROVIDER == "openai" else synth_eleven
    key = "OPENAI_API_KEY" if PROVIDER == "openai" else "ELEVENLABS_API_KEY"
    if not os.environ.get(key):
        sys.exit(f"Set your API key first:  export {key}=...")

    outdir = os.path.join(HERE, "audio"); os.makedirs(outdir, exist_ok=True)
    from pydub import AudioSegment
    made = skipped = 0
    for i, it in enumerate(items, 1):
        dest = os.path.join(outdir, it["key"] + ".mp3")
        if os.path.exists(dest):
            skipped += 1; continue
        print(f"[{i:>3}/{len(items)}] {it['key']}: {it['text'][:50]}...")
        clip = AudioSegment.from_file(io.BytesIO(synth(it["text"])), format="mp3")
        clip.export(dest, format="mp3", bitrate="128k")
        made += 1
    print(f"\nDone. Rendered {made} new clip(s), skipped {skipped} existing. -> {outdir}")
    print("Refresh the app — flashcards, reels, versus, and Listen mode now use the studio voice.")

if __name__ == "__main__":
    main()
