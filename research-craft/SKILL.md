---
name: research-craft
description: Apply deliberate research craft — the trainable stack of sub-skills behind good research (after Hamming, Schulman, Shannon, Feynman, Karpathy, Ng, Sutton, Olah). Pick your own problems by reasoning backward from a desired outcome; train taste by predicting results before running; upgrade inputs (read primary sources and old/cross-field work, not threads); write everything down in a log and publish; tighten the experimental loop with tooling and overfit-one-batch; stare at raw outputs and failures; wander across subfields and tune baselines until they hurt; keep an open door. Use when doing or planning research, choosing a research problem or direction, designing or debugging experiments/evals/models, building a research log, deciding what to read, or trying to improve research quality and speed.
---

# Research Craft

Research ability is not a gift; it is a **stack of smaller skills, almost every one of which can be deliberately trained**. Most people reverse-engineer the job from papers and threads and learn to *look* like a researcher rather than *be* one. The single governing idea: **research speed is the speed at which you discover you are wrong** — so optimize every habit for faster, cheaper error discovery.

Use this when you are doing research yourself, or guiding/assisting someone's research. Apply the relevant moves; don't recite the list.

## 1. Pick your own problems

- **Run Hamming's question** on the work: what are the important problems here, and why am I *not* working on them? An absorbed problem hands you a conclusion without the reasoning — you won't see the pivot coming and you're racing people who started earlier with more compute.
- **Reason backward, not forward** (Schulman): instead of scanning the literature for things to improve, choose an outcome you genuinely want to exist and derive the experiments that would produce it. Backward-from-a-goal manufactures originality; it drags you into territory no survey covers.
- **Train taste like a muscle, not a gift**: predict the result of every experiment *before* running it; cover a paper's results and guess the numbers from the method alone; record which current releases will matter in two years and check your hit rate. Forecast → correction, repeated, is how the model in your head gets trained.

## 2. Upgrade your inputs

- Shared reading lists produce shared, worthless-because-simultaneous conclusions. **Diversify the diet beyond the trending feed.**
- **Old material is underpriced** — the field reruns its past on a delay (MoE 1991, LSTM 1997, backprop 1986). A short deep classic (e.g. Sutton's *Bitter Lesson*) often predicts the field better than a survey ten times its length.
- **Shrink-then-grow** (Shannon): reduce a problem until it's nearly trivial, solve the small version, then reintroduce difficulty one piece at a time.
- **Range beats pure depth**: borrow across fields (interpretability ← neuroscience; eval design ← mechanism design; architecture sense ← how GPUs move memory). Honest statistics is rare and high-value.
- **Read the paper, not the thread.** The appendix is where the bodies are buried; the limitations section is usually the most honest paragraph.

## 3. Write everything down

- Writing finds the gaps your head papers over (Graham): the untested assumption, the step that doesn't follow, the two claims that contradict. If it won't go cleanly onto the page, it isn't finished.
- **Don't fool yourself** (Feynman) — you're the easiest target. Record disconfirming evidence *on the spot* (Darwin), because memory deletes inconvenient results faster than convenient ones.
- **Keep a log per experiment: hypothesis · setup · expectation · result · updated belief.** Rereading last month's entries is the most honest review you'll get.
- **Publish some of it** (Olah & Carter, *research debt*): a clear explanation is a real contribution, and a body of public writing is the strongest, unfakeable credential for how you think.

## 4. Tighten the loop

- The edge is **volume** (Radford): more runs/day, more wrong ideas discarded/week, a reality-model that updates faster.
- **Tooling is a first-class research activity**: launch a run in one command, plot in one more, reproduce any run from its config, compare two runs in seconds. 
- **Overfit a single batch before training at scale** (Karpathy): ~30 seconds, half your bugs gone. Shrink everything until it's cheap, get it right, then spend compute.
- **Engineering = research at the frontier.** Whoever can build the harness, eval, and data pipeline is the one whose hypotheses actually get tested; everyone else waits in the queue.

## 5. Stare at the outputs

- A descending loss curve is reassurance, not analysis. Experiments emit far more than you read — transcripts, failure cases, the strange tail.
- **Look at the raw data by hand** *before* writing training code (Karpathy): most ML bugs live in the data and fail silently — no crash, just a mediocre model and a wrong theory.
- **Error analysis** (Ng): pull ~100 failures, read all of them, sort into piles, attack the biggest pile. Works on models and on evals — a benchmark whose transcripts you've never read is one you don't understand. One transcript of genuinely strange behavior teaches more than the next decimal of accuracy.

## 6. Wander on purpose

- Your first subfield is an accident of timing — pay tuition in several (interp, evals, RL, systems) before deciding where your specific weirdness is an unfair advantage.
- **Run the disposable version of every idea first; let most die young.**
- **Tune baselines until it hurts** — the graveyard is full of gains that evaporate against a properly tuned baseline. **Ablate** until you know which single component carries the result (usually not the one in the title).
- **Breadth is insurance**: subfields saturate, usually right after they peak on social media; the people who keep producing already know the neighboring territory.

## 7. Find your people

- **Keep the open door** (Hamming): closed-door people get more done in a year; open-door people do the work that matters, because interruptions carry information about what the world needs. Your open door is your inbox.
- **Generosity compounds**: replicate and publish what you find, release your tools, explain hard things plainly. Returns arrive sideways, months later, as a collaboration / citation / role.
- **Float half-formed ideas in public** — being wrong on the timeline is far cheaper than being wrong in print. A collaborator who kills a bad idea before you sink three months into it is worth more than compute, and can't be bought, only earned.

## 8. The long game

Luck favors the prepared mind (Pasteur); knowledge and productivity compound like interest (Hamming). The daily edges — what you read, what you record, how fast your loop runs, who you argue with — look trivial in isolation and produce careers that look like luck from outside. **Start compounding earlier than feels necessary.**

## Quick self-audit

When stuck or starting, ask: Am I working *my* problem or an absorbed one? Did I predict before I ran? Am I reading primary sources? Is it in the log? Have I looked at 100 actual failures? Is my baseline honestly tuned? Can I launch+compare a run in seconds? Am I floating this idea where someone can kill it cheaply?

## Source

Distilled from Vivek (@itsreallyvivek), "how to be good at research" (2026-06-10). Full Chinese translation: `references/how-to-be-good-at-research-zh.md`.
