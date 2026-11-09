---
name: mini-golf-par-mix-research
description: Evidence-gated research on mini-golf par mix and course composition. Use when comparing 18-hole reference courses (e.g. Walkabout Mini Golf), collecting hole-by-hole par sequences, summarizing par distributions or pacing, or proposing or revising our course recipe (how many par 2/3/4/5 holes and in what order). Not for building, simulating or testing holes; for that, see the playtesting docs or the hole-testing skill.
---

# Mini-golf par-mix research

This is desk research only. It produces a cited dataset and a short report. It never edits geometry, retunes holes or changes the live game. Use free, public, read-only sources: no accounts, purchases or contacting companies.

## 1. Collect: one record per course variant
Record one row per **course x mode x version**, using the complete ordered hole-par sequence:

| field | notes |
|---|---|
| course, mode (easy/regular/hard/unknown), version or date | Keep the modes separate. Never decide which variant a row is just because its total matches. |
| pars[1..18] | Copy them in order, exactly as the source gives them |
| printed_total | The total the source prints, if it has one |
| independent_total | A total from a different source, if one exists |
| source URL, access date, capture path | Save raw captures under a gitignored folder (`_raw/`, `_cache/`). See AGENTS.md "What to commit" |
| evidence tier | See section 3 |
| confidence + notes | Say what is uncertain and why |

## 2. Validate: every check is a gate
A row is **valid** only if all of these hold:
1. It has exactly 18 pars, and every par is a positive integer.
2. Its pars add up to `printed_total`, and also to `independent_total` when that exists.
3. Its histogram counts add up to 18, and the counts weighted by par add up to the same total.
4. Pars outside 2-5 are kept and flagged as exceptions, not clipped.

Rows that fail go to **quarantine** with the reason, the original values and the source. Don't fix a row by guessing. A matching sum doesn't prove each hole is right: it only shows the total is consistent.

## 3. Evidence tiers (label every row and every claim)
- **directly verified**: read from a primary source such as the in-game scorecard or official material
- **community transcribed**: hole-by-hole values from a fan or community page
- **total-only corroborated**: an independent source agrees with the total but not with each hole
- **inferred mode / unverified**: the mode or the values are an assumption

Example seed sources. Treat them as leads, not as truth:
- [bros2k WAMG2](https://www.bros2k.com/wamg2): community hole rows. Some sums are known to be wrong and some modes are unlabeled.
- [rimblas/wmgt courses-list](https://github.com/rimblas/wmgt/blob/main/docs/courses-list.md): corroborates course totals only.
- [Mighty Coconut "5 years in numbers"](https://www.mightycoconut.com/blog/5-years-numbers): raw counts and rankings, without attempt numbers.

## 4. Analyze
- Summarize the distribution per variant: histogram, mean, and the range across courses. Never pool rows whose mode is unknown with labeled modes.
- Pacing claims (openers, closers, where the long holes fall) need the **ordered sequences**. A pooled histogram can't support them.
- Keep these quantities separate and never swap one for another:
  - authored or suggested par
  - minimum strokes found
  - how hard the hole is for players
  - ace fraction over the input domain (simulated shots)
  - actual player ace rate
- A raw ace count without the number of attempts is not a rate.

## 5. Recommend, separately from the facts
Label each statement as either an **empirical fact** (cited, with its tier) or a **recommended composition** (a design choice, with its reasoning). An unverified fixed par mix never becomes a project rule. Research doesn't trigger geometry edits or retuning on its own. Any change goes to Chase as a proposal.

## Output template
```markdown
# Par-mix research: <scope> (<date>)
## Question
## Coverage    N valid variants / M collected; modes covered; known gaps
## Data        table: course | mode | version | pars 1-18 | total | tier | source
## Quarantine  table: row | failed check | original values | source
## Findings    per-variant distributions and variation; pacing from ordered sequences only. Cite every claim with its tier
## Limitations and uncertainty
## Recommendation (design choice, not fact)   proposed mix/ordering + rationale; status: proposal
```
Put long reports in `games/<game>/` or Notion. Commit only the final cited report, never the raw captures. The historical research report is in Notion: https://app.notion.com/p/412ee84e79fc81de86cbfdd865b176e2
