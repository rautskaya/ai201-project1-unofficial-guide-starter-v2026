# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none, because the grader can't
> read it.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Week 1

## What This Does

A retrieval-based question-answering system that searches city guides to answer user queries. The user asks about topics such as restaurants, accessibility, travel times, or attractions. The system retrieves relevant information from the guide corpus and provides grounded answers with source attribution. When sufficient information is not available, the system returns a refusal rather than generating unsupported answers.

## Chunking Strategy

**Chunk size:** 800 characters  
**Overlap:** 120 characters  
**Strategy:** Hierarchical chunking that respects document structure

The city guides are structured with section headings (##) and complete paragraphs. A naive fixed-size chunker would cut sentences in half, breaking meaning. This chunker:
1. Splits on section boundaries (## headings)
2. Keeps sections ≤800 chars as one chunk
3. Splits larger sections by paragraph boundaries
4. Only uses fixed-size overlap (120 chars) for oversized individual paragraphs

This preserves complete thoughts. For example, the "Straightforward" accessibility section (3 towns, 420 chars) stays as one chunk instead of being split mid-paragraph.

## Sample Chunks

**Chunk 1** — source: guide_accessibility.md#0  |  produced by: chunker.py::split_documents
======================================================================
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.

**Chunk 2** — source: guide_corry_vale.md#5  |  produced by: chunker.py::split_documents
======================================================================
# Corry Vale

## Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.

**Chunk 3** — source: guide_givens_mill.md#2  |  produced by: chunker.py::split_documents
======================================================================
# Givens Mill

## Getting around

Everything is on one street along the river. The mill is at one end and the church at the other, eight minutes apart. The riverside path continues in both directions for as far as you want to walk.

**Chunk 4** — source: guide_kestrelford.md#4  |  produced by: chunker.py::split_documents
======================================================================
# Kestrelford

## What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.

**Chunk 5** — source: guide_pellew_sands.md#6  |  produced by: chunker.py::split_documents
======================================================================
# Pellew Sands

## When to go

June and September for the beach without the crowds. July and August are busy and the town is at its most itself, for better and worse. Winter is bleak, largely closed, and has a following among people who like that sort of thing.

## Sample Answer

**Question:** How long does it take to walk across Brightwater from one end to the other?

**Answer:**

```
(best distance 0.307, cutoff 0.6)

It takes about 35 minutes to walk across Brightwater from end to end (source: guide_brightwater.md).

Sources retrieved: guide_brightwater.md, guide_pellew_sands.md, guide_regional_transport.md, guide_thornby_wells.md, guide_walking.md
```

**My relevance cutoff:** 0.6

In-scope questions landed between 0.31 and 0.57. Out-of-scope questions landed around 0.80+. There's a clear gap between the two groups, and 0.6 sits in that gap.

| Question | In corpus? | Best distance |
|---|---|---|
| How long to walk across Brightwater? | Yes | 0.307 |
| What's the main accessibility challenge in Halden Bay? | Yes | 0.385 |
| When does Kestrelford's bakery sell out? | Yes | 0.402 |
| Winter weekend, best town for food + shopping? | Yes | 0.574 |
| What is the capital of Mongolia? | No | 0.803 |
| How do I change the oil in a diesel engine? | No | 0.888 |
| Who won the 1994 World Cup? | No | 0.975 |
| Recommended dosage of ibuprofen? | No | 0.798 |
| How do I write a for loop in Rust? | No | 0.836 |

## How I Used AI

**1.** I described my chunking strategy (split on ## headings, keep sections under 800 chars, split larger sections by paragraph) and asked Claude to implement it in chunker.py. The first version had a bug: it treated the single # document title as the heading for the first section, so chunks from that section showed the title twice. It now stores the title separately from section headings.

**2.** My winter-weekend question got a best distance of 0.574, under the 0.6 cutoff, but the system still refused to answer. It explained there are two checks: the gate only looks at distance, and the model separately decides if the chunks actually answer the question. That told me the real issue was retrieval — it never pulled in guide_marchwood.md, which has the answer.

# Week 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     week 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

Produced by `run_eval.py::main`. Corpus: `city_guides`, top-k 5, cutoff 0.6, 3 runs per question, caching off. Full output in `results/run_2026-09-20_1546_before.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks are complete thoughts | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Answers include specific facts | 4 of 5 | 4/5 | 5/5 | 4/5 | MET |

**Criterion 1** — produced by `generate.py::answer_from_chunks`. The one question that pulled this criterion down — retrieved from `guide_corry_vale.md`, `guide_eating.md`, `guide_halden_bay.md`, `guide_kestrelford.md` (never `guide_marchwood.md`, which has the actual answer):

**Question:** If you're visiting on a winter weekend and need both good food options and shopping, which town is the best choice?

```
I do not have enough information to answer this question. The provided documents mention when places are open or busy, but they do not compare towns to determine which one is the "best choice" for a winter weekend with both good food options and shopping.

Sources: `guide_corry_vale.md`, `guide_eating.md`, `guide_halden_bay.md`, and `guide_kestrelford.md`.
```

**Criterion 2** — produced by `generate.py::answer_from_chunks`. Every answer names its source, including this one:

**Question:** When does Kestrelford's bakery typically sell out?

```
Kestrelford's bakery typically sells out by 11am (from `guide_kestrelford.md` and `guide_eating.md`).
```

**Criterion 3** — produced by `gate.py::check`, run by `run_eval.py::check_out_of_scope`. Exact row from `results/run_2026-09-20_1546_before.md`:

```
| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.803 | refused |
```

**Criterion 4** — this criterion is about chunk quality, which `run_eval.py` doesn't measure — `results/run_2026-09-20_1546_before.md` has no chunk data in it. This evidence instead comes from `chunker.py::split_documents`, printed by `app.py chunks -n 5` (Milestone 3):

```
Chunk 4 | source: guide_kestrelford.md#4 | produced by: chunker.py::split_documents
# Kestrelford

## What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

**Criterion 5** — produced by `generate.py::answer_from_chunks`. Answer includes concrete facts, not vague generalizations:

**Question:** How long does it take to walk across Brightwater from one end to the other?

```
It takes about 35 minutes to walk across Brightwater from end to end (Source: guide_brightwater.md).
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     week — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | Target was 4 of 5. Got exactly 4/5 in all three runs — the winter-weekend question failed every time because `guide_marchwood.md` was never retrieved. |
| 2 | Every answer names a source | MET | Target was 5 of 5. Got 5/5 in all three runs, including the one refused answer, which still listed the sources it checked. |
| 3 | Gate stops out-of-corpus questions | MET | Target was 4 of 5. Got 5/5 — the gate is a single deterministic pass against a fixed threshold, so this doesn't vary by run. All five out-of-scope questions had distances well above 0.6 (0.80–0.98). |
| 4 | Chunks are complete thoughts | MET | Target was 4 of 5 sampled. Checked the 5 chunks pasted in Sample Chunks — all 5 end with proper sentence punctuation and none cut off mid-thought. |
| 5 | Answers include specific facts | MET | Target was 4 of 5. Got 4/5, 5/5, 4/5 across the three runs. The winter-weekend answer was the one that stayed vague in two of three runs; in the third it at least named a place and a date range. |

## Diagnoses

**The winter-weekend question was missed every run, at retrieval.** The correct chunk (`guide_marchwood.md`: "nothing closes seasonally") never made the top 5. Mechanism: embedding similarity matches wording, not meaning — the question's words ("winter weekend," "shopping") don't overlap with the answer's words ("seasonal," "indoors," "covered market"), so it ranked 6th-8th while less-relevant but more word-similar chunks took the top 5. Didn't break Criterion 1 (4/5 still met the target exactly), but it's the same question failing all three runs.

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
