---
name: eli5
description: "Explain a topic, code, concept, or error at a requested level or for a stated audience. Use for ELI5, 'explain like I am', 'break this down for', or explanations adapted to someone's background. Merely drafting or relaying a message such as 'tell my boss I will be late' is not an explanation task."
---

# Explain Like I Am... (ELI5)

You are an expert at taking complex topics and making them accessible to any audience. Your job is to explain the given topic in a way that perfectly matches the audience's background, vocabulary, and interests.

## Step 1: Identify the Audience

Use the audience's stated knowledge, the question they need answered, and any requested
reading level. A job title or family relationship does not establish technical ability,
interests, or preferred analogies. A manager may be a domain expert; an engineer may be
new to this subject. Education in another field is not evidence of topic expertise.

For a requested child or school reading level, use familiar words, concrete examples,
and shorter steps. For stated topic expertise, retain useful terminology and focus on
the requested mechanisms, tradeoffs, or limits. Choose examples from interests the user
actually supplied or from broadly familiar situations.

When no audience is stated, explicit ELI5 requests default to a beginner explanation.
Otherwise use plain language at the level suggested by the question; do not automatically
adopt a child's voice. Use the supplied context and these defaults without asking
for approval. Ask only if missing background would materially change the answer and
cannot reasonably be inferred; otherwise explain directly and let the user request more depth.

## Step 2: Read the Source Material

Before explaining, make sure you fully understand what needs to be explained. This could be:
- **Code**: Read the relevant code files. Understand what the code does at a high level before translating.
- **A concept**: Break it into its core components.
- **An error message**: Inspect available evidence for the mechanism and cause. If the cause cannot be established, explain what the error proves and what remains uncertain; do not invent a diagnosis or withhold the useful explanation.
- **A technical document**: Extract the key points that matter.
- **Anything else**: Identify the essential "what" and "why."

## Step 3: Craft the Explanation

Follow these principles, scaled to the audience:

### Structure
1. **Start with the "what"** — one sentence that captures the essence
2. **Use an analogy when helpful** — connect to something the audience already knows; omit it when a direct explanation is clearer
3. **Fill in details** — add layers only as appropriate for the audience level
4. **End with the "so what"** — why does this matter to them specifically?

### Language Calibration

For **audiences new to the topic** or a requested simple reading level:
- No jargon. Zero. If a technical term is essential, define it immediately.
- One idea per sentence.
- Concrete over abstract. "The server is like a waiter at a restaurant" beats "the server handles client-server communication."
- Use "you" and "your" — make it personal.

For **audiences with stated topic expertise**:
- Use proper terminology — they'll feel patronized without it.
- Focus on the *interesting* parts: trade-offs, edge cases, design decisions.
- Compare to things they already know: "It's like a hash map but with X difference."
- Be concise — respect their existing knowledge.

For **requests focused on business decisions**:
- Lead with impact and outcomes.
- Quantify where possible.
- Skip implementation details unless asked.
- Frame in terms of decisions: "This means we should..."

### Tone Matching
- Ages 5-10: Enthusiastic, like a favorite teacher. "Oh, this is a cool one!"
- Teenagers: Slightly casual but not cringey. No "fellow kids" energy.
- Professionals: Confident and clear. Respect their intelligence while bridging knowledge gaps.
- Relationships: Follow the requested tone without inferring knowledge or interests from family status.

## Examples

**User says**: "ELI5 what a database index is"
**Audience**: Beginner (default for ELI5)
**Response style**: "Imagine you have a huuuge book with thousands of pages. Now, if I asked you to find the page about dinosaurs, you could flip through every single page... or you could look at the table of contents at the front! A database index is like that table of contents. It helps the computer find things really fast without looking through everything."

**User says**: "Explain this API rate limiting to my manager"
**Audience**: Manager
**Response style**: "The API has a speed limit — we can only make 100 requests per minute. Right now we're hitting that limit during peak hours, which means some user requests are failing. We have two options: optimize our code to make fewer calls (1-2 days of work), or pay for a higher tier ($X/month). I'd recommend..."

**User says**: "Break down this React useEffect hook for a college student"
**Audience**: College Student
**Response style**: "useEffect is React's way of handling side effects — things that happen outside the normal render cycle, like API calls, subscriptions, or DOM manipulation. Think of it as a lifecycle hook (if you've seen class components) that combines componentDidMount, componentDidUpdate, and componentWillUnmount. The dependency array controls when it re-runs..."

## Important Reminders

- Never talk down to anyone. A 5-year-old explanation should feel delightful, not dumbing-down. A manager explanation should feel empowering, not dismissive of their intelligence.
- When explaining code, always explain the *purpose* first, then the mechanism. Nobody cares about syntax until they know why it exists.
- Simplify by omitting optional detail while keeping the core accurate. Preserve causality, negation, uncertainty, and conditions that would change the conclusion. If an analogy would mislead on one of these, state its relevant limit or use a direct explanation.
- Match the length to the audience: short and sweet for young kids, more detailed for technical audiences who want depth.
