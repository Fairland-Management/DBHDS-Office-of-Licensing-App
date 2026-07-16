#!/usr/bin/env python3
"""
Render the "So You Want to Get Licensed" podcast to a real studio-voice MP3.

Two hosts, two distinct AI voices, stitched into one file: podcast.mp3
Drop podcast.mp3 next to DBHDS_Exam_Trainer.html and the app's 🎧 button lights up.

------------------------------------------------------------------------
QUICK START (OpenAI voices — most natural, ~2 minutes):
    pip install openai pydub
    # ffmpeg must be installed too:  macOS ->  brew install ffmpeg
    export OPENAI_API_KEY="sk-...your key..."
    python generate_podcast_audio.py

Prefer ElevenLabs? Set PROVIDER = "elevenlabs" below and:
    pip install elevenlabs pydub
    export ELEVENLABS_API_KEY="...your key..."
------------------------------------------------------------------------
No coding needed beyond pasting your key. The script does the rest.
"""

import os, sys, io

PROVIDER = "openai"          # "openai" or "elevenlabs"

# Voice choices (change to taste)
OPENAI_VOICE_MAYA  = "nova"    # warm, curious
OPENAI_VOICE_THEO  = "onyx"    # deeper, steady
ELEVEN_VOICE_MAYA  = "Rachel"
ELEVEN_VOICE_THEO  = "Adam"

GAP_MS = 350   # pause between lines (natural rhythm)

# ---- The script: (speaker, text) in order --------------------------------
LINES = [
 ("M","Okay Theo, real talk. Someone wakes up tomorrow and says, I want to open a group home for adults with developmental disabilities. Where do they even start?"),
 ("T","You'd think step one is paperwork. It's not. Step one is a classroom."),
 ("M","A classroom? Come on."),
 ("T","Before you can even apply, you complete an orientation, sixteen modules, and you pass an exam with an eighty-five percent."),
 ("M","Wait. You can't even apply until you pass a test?"),
 ("T","Not for the high-priority services. That's the gate. And honestly, it's there so people know exactly what they're walking into."),
 ("M","So who's actually in charge here? Who hands you the license?"),
 ("T","The Office of Licensing. Think of them as the referee. They issue your license, they monitor you, they investigate, and they enforce the rules."),
 ("M","Referee. I like that."),
 ("T","And here's a mental model that'll save you a headache. Most services live under one big rulebook. Children's homes have their own. Human rights has its own."),
 ("M","One big rulebook, plus a couple of special ones. Got it."),
 ("M","When you say group home, what does that actually look like day to day?"),
 ("T","For adults with developmental disabilities, it's round-the-clock supervision, but for a small number of people. Eight or fewer. A real home, not an institution."),
 ("M","That not an institution line keeps coming up."),
 ("T","Because it's the whole philosophy. Ordinary life. Small settings. Real choices. Everything else is just details protecting that."),
 ("M","Alright, our person passed the exam. Now the paperwork?"),
 ("T","Almost. First, a move most people skip and later regret. Read the regulations, and sign up for the email list."),
 ("M","The email list? That feels kind of minor."),
 ("T","It's the opposite of minor. If a rule changes and you didn't get the memo, your application can be rejected for something you never even knew about."),
 ("M","So it's basically free insurance."),
 ("T","Free insurance. Take it."),
 ("M","Okay. Now the paperwork?"),
 ("T","Now the paperwork. Every service needs the same eight documents. The one that trips people up is proof you can cover ninety days of expenses, plus a full year's budget."),
 ("M","So they want to know you won't run out of money in month two."),
 ("T","Exactly. And think about why. If you fold in a month, it's the people you were serving who get hurt. The money rule is really a safety rule."),
 ("M","Where does all of this actually go?"),
 ("T","An online system called Connect. You build the whole application in there. But, one warning I give everybody."),
 ("M","Uh oh."),
 ("T","When you pick your service, choose carefully. The second you hit submit, that choice is locked. No do-overs."),
 ("M","So measure twice, submit once."),
 ("M","You hit submit. Then you just, wait?"),
 ("T","If it's complete, you land on the waitlist and you get a welcome letter. And that letter basically says, start your background checks now."),
 ("M","Why the rush?"),
 ("T","Because you cannot serve a single person until you've requested background and registry checks for your direct-care staff and their supervisors. Start early, or you'll be stuck waiting."),
 ("M","Background checks. Any hidden traps?"),
 ("T","One really bites people. When a staff member's eligibility letter comes back, print it immediately. It vanishes from the system after six months."),
 ("M","And if you miss that window?"),
 ("T","You redo the whole check. Pay the fee again. So the habit is simple. It comes in, you print it, you file it. Done."),
 ("M","Does a real person actually read all your policies?"),
 ("T","Line by line. A Policy Review Specialist. And if something's off, they send back what's called a deficiency letter."),
 ("M","Deficiency letter sounds scary."),
 ("T","It just means fix these. But there's a clock, thirty days if you're priority. Miss it, and the whole application closes. So you answer fast."),
 ("M","Is there ever a real person walking through the actual house?"),
 ("T","For a residential program? Absolutely. Before any license, a Licensing Specialist inspects the physical space."),
 ("M","What are they even checking for?"),
 ("T","Little things that are secretly big. The air stays between sixty-five and eighty degrees. The hot water stays between a hundred and one-twenty, so nobody gets scalded. The kind of safety you'd want for your own family."),
 ("M","So they hand you the license and you're off to the races?"),
 ("T","Sort of. Your very first license is conditional. Think of it like a learner's permit. Six months, and you can't add services or locations yet."),
 ("M","What are they waiting to see?"),
 ("T","That you can actually do it. You have to serve real people, and serve them well, before they'll trust you with the full license."),
 ("M","You have to prove it, not just promise it."),
 ("M","What happens if they find a problem once you're up and running?"),
 ("T","They cite it, and you write a Corrective Action Plan. A cap, people call it. It's basically a promise. Here's what I'll fix, here's by when, and here's who's responsible."),
 ("M","So a citation isn't a death sentence."),
 ("T","Not even close. How you respond is the whole game. You submit the plan in the portal, and here's the part that trips everyone up, the status flips to Returned."),
 ("M","Returned? Like they sent it back to me?"),
 ("T","That's the trap! Returned means you returned it to them. It's with the Office of Licensing now. It's in their court, not yours."),
 ("M","Heavier question. What about emergencies? Someone actually gets hurt?"),
 ("T","Then reporting becomes sacred. A serious incident, say an emergency-room visit, gets reported within twenty-four hours."),
 ("M","Twenty-four hours from when it happens?"),
 ("T","From when you discover it. And abuse or neglect? Also twenty-four hours, straight to the Office of Human Rights. That speed is exactly how the whole system keeps people safe."),
 ("M","So how does the story end? Do they ever get off the training wheels?"),
 ("T","They do. Show full compliance, actually serve people well, and the conditional becomes a real license. First an annual, one year, then eventually a three-year."),
 ("M","From I have an idea to trusted provider."),
 ("T","That's the arc. And every rule we just walked through? It was never really about paperwork. It was about the person who gets to live a good life, because somebody did this right."),
 ("M","Okay. That actually gave me chills. Roll the credits."),
]

def synth_openai(text, speaker):
    from openai import OpenAI
    client = OpenAI()  # reads OPENAI_API_KEY
    voice = OPENAI_VOICE_MAYA if speaker == "M" else OPENAI_VOICE_THEO
    r = client.audio.speech.create(model="gpt-4o-mini-tts", voice=voice, input=text)
    return r.content  # mp3 bytes

def synth_eleven(text, speaker):
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs()  # reads ELEVENLABS_API_KEY
    voice = ELEVEN_VOICE_MAYA if speaker == "M" else ELEVEN_VOICE_THEO
    audio = client.text_to_speech.convert(voice_id=voice, model_id="eleven_multilingual_v2", text=text)
    return b"".join(audio)

def main():
    from pydub import AudioSegment
    synth = synth_openai if PROVIDER == "openai" else synth_eleven
    key = "OPENAI_API_KEY" if PROVIDER == "openai" else "ELEVENLABS_API_KEY"
    if not os.environ.get(key):
        sys.exit(f"Set your API key first:  export {key}=...")

    episode = AudioSegment.silent(duration=300)
    gap = AudioSegment.silent(duration=GAP_MS)
    for i, (spk, text) in enumerate(LINES, 1):
        print(f"[{i:>2}/{len(LINES)}] {('Maya' if spk=='M' else 'Theo')}: {text[:60]}...")
        clip = AudioSegment.from_file(io.BytesIO(synth(text, spk)), format="mp3")
        episode += clip + gap

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "podcast.mp3")
    episode.export(out, format="mp3", bitrate="128k")
    print(f"\n✅ Done → {out}\nDrop it next to the app; the 🎧 button in Story Mode will light up.")

if __name__ == "__main__":
    main()
