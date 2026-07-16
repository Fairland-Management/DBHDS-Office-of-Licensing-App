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
"podcast-m2": [
  ("M","So who actually runs licensing in Virginia?"),
  ("T","The Office of Licensing. Four verbs sum them up. They issue licenses, they monitor, they investigate, and they enforce."),
  ("M","Regulate, not provide."),
  ("T","Exactly. They're the referee, not a player."),
  ("M","Is it one office statewide?"),
  ("T","Five regions, each with a color on the map. And three rulebooks matter. One-oh-five is the general regulations, forty-six is children's residential, one-fifteen is human rights."),
  ("M","One-oh-five is the big bucket."),
  ("T","Most services live there."),
  ("M","Who does all this serve?"),
  ("T","Four categories. Developmental disability, mental illness, substance use, and brain injury. Developmental disability shows up before age twenty-two."),
  ("M","Before twenty-two. That's the line."),
  ("T","Right. A brain injury at twenty-five is not a developmental disability."),
],
"podcast-m3": [
  ("M","Where does a new applicant even start learning the rules?"),
  ("T","The Office of Licensing website. And step one, subscribe to the email list."),
  ("M","Why the list?"),
  ("T","Because if a rule changes and you didn't hear, your application can be rejected for it. Free insurance."),
  ("M","Are there specific rules everyone should know?"),
  ("T","Three to memorize. Four-fifty is training. Five-twenty is risk management. Six-twenty is quality improvement."),
  ("M","Count up. Four train, five risk, six quality."),
  ("T","That's the trick."),
  ("M","So I just copy the regulations into my policies?"),
  ("T","No. That's the classic mistake. Tailor them to your service, and be ready to show you actually follow them."),
  ("M","Written and lived."),
  ("T","Policies are working documents, not decoration."),
],
"podcast-m4": [
  ("M","Does everyone wait the same amount of time?"),
  ("T","No. There's a prioritization list. Priority one is green, pulled in five to ten business days. Priority two is blue, twenty-one business days. Non-priority can be a year or more."),
  ("M","One is fastest."),
  ("T","Right. One to about ten, two to twenty-one."),
  ("M","If they find gaps, how long do I have?"),
  ("T","For a priority application, thirty calendar days. Non-priority gets ninety. Miss it, and the application closes."),
  ("M","Priority thirty, non-priority ninety."),
  ("T","And it's calendar days, not business days."),
  ("M","Who reviews it all?"),
  ("T","Two specialists, in order. The Policy Review Specialist checks compliance and sends deficiency letters. Then a Licensing Specialist takes over."),
  ("M","Paper first, people second."),
  ("T","And you can't serve anyone until background checks are requested for direct-care staff and their supervisors."),
],
"podcast-m5": [
  ("M","What goes into an initial application?"),
  ("T","Eight documents, the same for every service. Service description, the business certificate, an org chart, ninety days of finances, a budget, a staffing plan, position descriptions, and your policies."),
  ("M","Eight documents."),
  ("T","The one that trips people is the money."),
  ("M","How much money do I have to prove?"),
  ("T","Ninety days of operating expenses, with a bank statement no older than ninety days. And a budget for the first twelve months."),
  ("M","So you won't fold in month two."),
  ("T","The money rule is really a safety rule for the people you'd serve."),
  ("M","What's the difference between closed and denied?"),
  ("T","Big difference. Miss a deadline, and it's a closure. You can reapply. But false information, or no certificate of occupancy, or co-locating the wrong services, that's a denial."),
  ("M","Deadline, close. Dishonest, deny."),
  ("T","Exactly."),
],
"podcast-m6": [
  ("M","Where do I actually do all this?"),
  ("T","A system called Connect. It went live in twenty twenty-one, and it replaced paper. You apply, you message, you submit plans, all of it, in there."),
  ("M","One portal for it all."),
  ("T","Check it daily once you're in the process."),
  ("M","Any trap in the portal?"),
  ("T","One big one. When you choose your service, choose carefully. The second you submit, that choice is locked. No changing it later."),
  ("M","Measure twice, submit once."),
  ("T","Exactly."),
  ("M","How do I talk to them?"),
  ("T","Use the messaging inside Connect, not personal email. It's the preferred method, and it's kept in your record."),
  ("M","On the record."),
  ("T","Notices land in your correspondence inbox, but you complete the actual task elsewhere in the portal."),
],
"podcast-m7": [
  ("M","Does someone inspect before I get a license?"),
  ("T","For residential, crisis receiving, and opioid-treatment services, yes. A pre-license inspection of the physical space."),
  ("M","So they walk the building."),
  ("T","Before any license is issued."),
  ("M","What are they checking?"),
  ("T","Little things that are secretly big. Air kept between sixty-five and eighty degrees. Hot water between a hundred and one-twenty, so nobody gets scalded."),
  ("M","Air low, water high."),
  ("T","Sixty-five to eighty, a hundred to one-twenty."),
  ("M","Do they always schedule inspections?"),
  ("T","Only the first ones. After your conditional period, every inspection is unannounced."),
  ("M","So stay ready."),
  ("T","Keep office hours and a main contact assigned. They can show up any time."),
],
"podcast-m10": [
  ("M","Once I'm licensed, how do I change things?"),
  ("T","Not a new application. A modification. Three kinds. Service, location, and information."),
  ("M","Add a service, add a place, or update a detail."),
  ("T","Information changes you can file any time. The bigger ones you plan ahead."),
  ("M","How far ahead?"),
  ("T","At least thirty days before the change. And the commissioner approves it at his discretion. You can't implement it until it's approved."),
  ("M","Ask early, wait for the yes."),
  ("T","Exactly."),
  ("M","Does a modification trigger another inspection?"),
  ("T","Only for residential, inpatient, and opioid-treatment. And only the physical space, before the license issues."),
  ("M","Same three kinds of services."),
  ("T","And a variance, permission to deviate from a rule, always needs the commissioner's written okay first."),
],
"podcast-m11": [
  ("M","When do staff get background-checked?"),
  ("T","Fingerprints go in within fifteen business days of hire, unless your own policy says you need the results first."),
  ("M","Fifteen business days."),
  ("T","And the name shows up in the system within twenty-four hours of the appointment."),
  ("M","Anything that bites people?"),
  ("T","The eligibility letter. It's only in the system for six months. Print it and file it, or you redo the whole check and pay again."),
  ("M","Grab it before it's gone."),
  ("T","Six months, then it vanishes."),
  ("M","Is it the same for everyone?"),
  ("T","No. At a private provider, it's direct-care staff and their supervisors, and they can start while results are pending. At a children's facility, it's everyone, and results must come back before anyone works."),
  ("M","Kids, results first."),
  ("T","Everyone, and before they start."),
],
"podcast-m16": [
  ("M","How do I actually register for the exam?"),
  ("T","Two documents, one email. The exam registration request form, and a scanned government photo ID, both to the training mailbox."),
  ("M","Together, or it's not accepted."),
  ("T","And register with the same email you put on the form."),
  ("M","What's the exam like?"),
  ("T","Twenty-five questions, ninety minutes, on Microsoft Teams, proctored, cameras on the whole time. Eighty-five percent to pass."),
  ("M","Twenty-five and ninety, cameras on."),
  ("T","And it covers all sixteen modules."),
  ("M","Anything I should not mess up on exam day?"),
  ("T","The join link comes once. Save it. Log in a few minutes early, because admission locks at the start time."),
  ("M","One link, arrive early."),
  ("T","And if you can't finish, a retake is a different version."),
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
