# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in week 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next week costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

Four questions ask for facts that are clearly stated in one place: bakery hours, accessibility barriers, eating patterns, walk time. One question asks about winter + weekend + food + shopping together. That one requires the system to pull information from multiple documents and combine it. I expect that harder question might not retrieve well. Getting 4 of 5 is more realistic.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

The grounding instruction explicitly asks the model to "name the document your answer came from." The model always has chunks with source metadata, so this should be 5 of 5. If any answer doesn't name a source, that's a sign the model isn't following instructions.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that".

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

Out-of-scope questions (about mongolia, programming, sports, dosages) should have very high distances since the embeddings are about city guides. A threshold of 0.6 should catch most of them, but one might slip through due to random semantic noise. 4 of 5 is a realistic target for a well-defined boundary between in-scope and out-of-scope.

---

## 4. Something about your chunks

When I sample 5 chunks at random, at least 4 are complete thoughts with no sentence cuts at either edge — each contains at least one full sentence and doesn't trail off mid-paragraph.

**Why this target:**

The city guides are written in complete paragraphs and structured sections. A chunk that cuts a sentence in half breaks the meaning and makes it hard to judge if an answer was actually retrieved.

---

## 5. Your choice

Answers include specific details (times, distances, place names) rather than vague generalizations. For at least 4 of 5 test questions, the answer mentions at least one specific fact like a number or name.

**Why this target:**

These test questions all ask for concrete facts: "11am," "35 minutes," "Marchwood," specific accessibility barriers. Vague answers like "the bakery is popular" or "towns are different" don't satisfy the questions. This criterion tests whether the model pulls actual details from the chunks.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     WEEK 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in week 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
