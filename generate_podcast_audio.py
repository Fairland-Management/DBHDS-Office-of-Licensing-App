#!/usr/bin/env python3
"""
Render the podcast LIBRARY to studio-voice MP3s — one file per episode.

Outputs (drop these next to DBHDS_Exam_Trainer.html; the app auto-detects them):
    podcast.mp3            -> "The Full Journey"
    podcast-caps.mp3       -> "Corrective Action Plans"
    podcast-crisis.mp3     -> "Crisis Services"
    podcast-incidents.mp3  -> "Death & Serious Incident Reporting"
    podcast-rights.mp3     -> "Human Rights & Home-Based Services"

QUICK START (OpenAI voices, most natural):
    pip install openai pydub          # also install ffmpeg (macOS: brew install ffmpeg)
    export OPENAI_API_KEY="sk-...your key..."
    python generate_podcast_audio.py                 # renders ALL episodes
    python generate_podcast_audio.py podcast-caps    # or just one, by base name

ElevenLabs instead? set PROVIDER="elevenlabs" and export ELEVENLABS_API_KEY=...
Cost: roughly 10-25 cents per episode on OpenAI.
"""
import os, sys, io

PROVIDER = "openai"          # "openai" or "elevenlabs"
OPENAI_VOICE_MAYA  = "nova"
OPENAI_VOICE_THEO  = "onyx"
ELEVEN_VOICE_MAYA  = "Rachel"
ELEVEN_VOICE_THEO  = "Adam"
GAP_MS = 350

EPISODES = {
"podcast": [
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
],
"podcast-caps": [
 ("M","Worst case. An inspector finds a problem. Is that the end of the road?"),
 ("T","Not at all. It just means you owe a Corrective Action Plan. People call it a cap. It's your written promise to fix it."),
 ("M","So getting cited is normal?"),
 ("T","Honestly, it's expected. What matters is how you respond. A good cap turns a bad day into a non-issue."),
 ("M","How long do I have to write this thing?"),
 ("T","Fifteen business days from the licensing report. That's the clock."),
 ("M","And if I need more time?"),
 ("T","You can ask for one extension, up to ten more business days, but you have to ask before it's due. And there's no extension for health-and-safety problems."),
 ("M","What does a good cap actually look like?"),
 ("T","Three ingredients. What you'll fix, by when, and who's responsible. Miss any one and it comes right back."),
 ("M","So vague promises don't fly."),
 ("T","Right. We'll do better is not a plan. The nurse re-trains staff by March first, and the manager audits monthly. That's a plan."),
 ("M","I submit it in the portal, and the status says Returned. Did they reject me?"),
 ("T","That's the trap everyone falls for. Returned means you returned it to them. It's with the Office of Licensing now, under review."),
 ("M","So Returned is actually good?"),
 ("T","It means it's in their court. And remember, saving is not submitting. If you only save, it never goes anywhere, and you can rack up more citations."),
 ("M","What if it's something serious. A safety issue?"),
 ("T","Then it's faster, no extension, and they always come back to check you actually did it. A follow-up inspection within thirty business days of accepting your plan."),
 ("M","And if I flat-out disagree with the citation?"),
 ("T","You can dispute it. Talk to your specialist first, then their supervisor, and the Director makes the final call. But the clock keeps ticking, so don't sit on it."),
],
"podcast-crisis": [
 ("M","Virginia rebuilt its whole crisis system. What's the big idea?"),
 ("T","Three doors. Someone to call, someone to respond, somewhere to go. A call center, a mobile team, and a place that takes you in."),
 ("M","No wrong door."),
 ("T","Exactly. However you enter, you get help."),
 ("M","Does the Office of Licensing license all of these?"),
 ("T","Most of them, but two it does not. The regional crisis call centers, and the crisis intervention team assessment centers."),
 ("M","Why not those two?"),
 ("T","They connect people to licensed services, but they're overseen differently. It's a classic trick question, so lock in the two."),
 ("M","What exactly is a crisis receiving center?"),
 ("T","A place you can walk into, get assessed and stabilized, for up to twenty-three hours and fifty-nine minutes. Center-based, with recliners instead of beds."),
 ("M","Under a day, by design."),
 ("T","Right. Short observation to head off an unnecessary hospitalization."),
 ("M","And if someone needs to stay longer than a day?"),
 ("T","That's a residential crisis stabilization unit. Short-term, a few days. But here's the number that matters. No more than sixteen beds."),
 ("M","What happens at seventeen?"),
 ("T","It crosses a federal line. It becomes an institution for mental diseases, and Medicaid won't pay for adults twenty-one to sixty-four. So sixteen is the ceiling."),
 ("M","Anything special for people with developmental disabilities?"),
 ("T","Yes, the REACH program. A statewide crisis system just for them, running since two thousand twelve. Mobile teams, community stabilization, and short crisis-home stays."),
 ("M","So crisis care isn't one-size-fits-all."),
 ("T","Never. And remember, even a licensed crisis unit still reports serious incidents within twenty-four hours, just like everyone else."),
],
"podcast-incidents": [
 ("M","Something goes wrong on a shift. What's the very first duty?"),
 ("T","Report it. Fast. Serious incidents go into the reporting system within twenty-four hours."),
 ("M","Twenty-four hours from when it happened?"),
 ("T","From when you discover it. The clock starts at discovery, not at the event."),
 ("M","Are all incidents treated the same?"),
 ("T","No, there are three levels. Level one is minor. It's not reported to the system, but you review those quarterly. Levels two and three are the ones you report within twenty-four hours."),
 ("M","So level one you track, two and three you report."),
 ("T","Exactly. Knowing which level something is. That's the whole skill."),
 ("M","What makes something a level three, the top level?"),
 ("T","Three things. A death, a sexual assault, or a suicide attempt that leads to a hospital admission."),
 ("M","Those are the heaviest."),
 ("T","And level three counts even if it happened off your premises. That's what sets it apart."),
 ("M","Where does the report actually go?"),
 ("T","A system called Chris. But to get in, you pass through a secure login portal called Delta."),
 ("M","And I heard Chris feeds two different offices?"),
 ("T","It does. Deaths and serious incidents go to the Office of Licensing. Abuse and neglect go to the Office of Human Rights. Reporting to one does not cover the other."),
 ("M","Once I've reported, am I done?"),
 ("T","Not quite. For serious ones, you do a root cause analysis. You figure out why it happened, within thirty days."),
 ("M","So report fast, then dig deep."),
 ("T","Exactly. Report in twenty-four hours, understand it within thirty days. And a team called the Incident Management Unit reviews every single one, and can follow up."),
],
"podcast-rights": [
 ("M","There's a whole office just for human rights?"),
 ("T","There is. It protects the rights of people receiving services. Freedom from abuse, dignity, choice."),
 ("M","So they swoop in and rescue people?"),
 ("T","Common misconception. They oversee and enforce. They don't provide emergency care, they don't run a hotline, and they can't remove someone from a setting."),
 ("M","If there's an abuse allegation, does that office investigate it?"),
 ("T","Usually the provider investigates its own, with a trained investigator. The office reviews it and can step in."),
 ("M","And the clock?"),
 ("T","Abuse, neglect, or exploitation gets reported within twenty-four hours. The written investigation and the director's decision come within ten working days."),
 ("M","New providers have a whole stack of human-rights policies. Are they all due at once?"),
 ("T","Just one has to be approved before you're licensed. Your complaint resolution policy. The rest, your advocate reviews after your welcome letter."),
 ("M","So don't panic about all of them up front."),
 ("T","Right. Complaint resolution first. Everything else follows."),
 ("M","Let's switch to the home side, the settings rule. What's it really about?"),
 ("T","One sentence. A person on Medicaid home-and-community services gets to live a life like anyone else's. Same rights, same freedoms."),
 ("M","Not an institution, again."),
 ("T","Always. That thread runs through everything."),
 ("M","What does that look like in a provider-run home?"),
 ("T","A lease with real eviction protections. A bedroom you can lock. A say in your roommate. Food you can get any time. Visitors whenever you want."),
 ("M","That's just a normal home."),
 ("T","That's the entire point. And one thing can never be taken away. Physical accessibility."),
 ("M","Who's behind all this. Who actually pays?"),
 ("T","Three agencies. The federal one, C M S, funds it. The state Medicaid agency, D MAS, holds the money and the agreements. And D B H D S runs the day-to-day and licenses providers."),
 ("M","Federal money, state agency, local operations."),
 ("T","And you can't bill until you're compliant with the settings rule and enrolled. Compliance isn't paperwork. It's the door to getting paid."),
],
}

def synth_openai(text, spk):
    from openai import OpenAI
    client = OpenAI()
    voice = OPENAI_VOICE_MAYA if spk == "M" else OPENAI_VOICE_THEO
    return client.audio.speech.create(model="gpt-4o-mini-tts", voice=voice, input=text).content

def synth_eleven(text, spk):
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs()
    voice = ELEVEN_VOICE_MAYA if spk == "M" else ELEVEN_VOICE_THEO
    return b"".join(client.text_to_speech.convert(voice_id=voice, model_id="eleven_multilingual_v2", text=text))

def render(base, lines, synth):
    from pydub import AudioSegment
    ep = AudioSegment.silent(duration=300); gap = AudioSegment.silent(duration=GAP_MS)
    for i,(spk,text) in enumerate(lines,1):
        print(f"  [{i:>2}/{len(lines)}] {'Maya' if spk=='M' else 'Theo'}: {text[:52]}...")
        ep += AudioSegment.from_file(io.BytesIO(synth(text,spk)), format="mp3") + gap
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), base+".mp3")
    ep.export(out, format="mp3", bitrate="128k"); print(f"  -> {out}")

def main():
    synth = synth_openai if PROVIDER=="openai" else synth_eleven
    key = "OPENAI_API_KEY" if PROVIDER=="openai" else "ELEVENLABS_API_KEY"
    if not os.environ.get(key): sys.exit(f"Set your API key first:  export {key}=...")
    want = sys.argv[1:] if len(sys.argv)>1 else list(EPISODES.keys())
    for base in want:
        if base not in EPISODES: print(f"(skipping unknown '{base}')"); continue
        print(f"\n=== {base} ==="); render(base, EPISODES[base], synth)
    print("\nAll done. Drop the .mp3 files next to the app; the studio button lights up per episode.")

if __name__ == "__main__":
    main()
