---
name: evidence-graph
description: Use for questions about this project's own documents or knowledge that need repository evidence and file citations, before opening sources. A conditional instruction such as citing files for knowledge questions does not make a general-topic question project knowledge. Skip general concept explanations, ordinary coding, and edits to supplied text unless the user asks to ground that topic in this repository's documents. For an applicable first lookup, use one shell tool call to read this SKILL.md and then run its sibling scripts/ask.py --project-root . --read-only --evidence-units --compact-provenance with the question. Read both outputs before answering.
---

# Project knowledge retrieval

Use for questions about this project's documents or knowledge. A conditional
"cite files for knowledge questions" rule does not make a general-topic question
project knowledge; skip general explanations, coding and supplied-text edits unless
the user asks to ground that topic in this repository. Never invent project support.
Use the bound lookup; do not fill missing project support with background knowledge.

From the project root, read the instructions and perform the first read-only
lookup together in one shell tool call. This preserves both outputs while
avoiding a separate model round trip between them. Ask narrowly in the language
documents are written in when known, otherwise the question's language:

```bash
cat "${CODEX_HOME:-$HOME/.codex}/skills/evidence-graph/SKILL.md" &&
python "${CODEX_HOME:-$HOME/.codex}/skills/evidence-graph/scripts/ask.py" --project-root . --read-only --evidence-units --compact-provenance "<narrow question>"
```

Read the full instructions and returned evidence before interpreting the result.
The batch authorizes no other action; binding or freshness failure still stops
retrieval. If the host requires a separate instruction read, respect that rule.
Once these instructions are already in context, run only the query command.

Claude: `${CLAUDE_PLUGIN_ROOT}/skills/evidence-graph/scripts/ask.py`; checkout: `context-graph/skills/evidence-graph/scripts/ask.py`.
This call validates binding, map integrity and source freshness. No preliminary
binding call, directory scan or reference read. Only a plain query is accepted:
`--path`, `--explain`, `--chain`, `--conflicts` are separate modes, not filters.

- Answer concisely with facts, essential qualifications and `file:line` citations.
  Preserve negation, conditions, state, rights and conflicting versions.
  Explicitly identify a conflict when sources disagree; leave its resolution open.
- When several returned units fully support the same claim, cite the first
  fully supporting unit in retrieval order. A shorter paraphrase is not a reason
  to replace its locator. Retain separate citations for distinct qualifications
  or conflicting claims; retrieval order alone is never proof of a claim.
  Select each supporting locator while reading the ordered units, then keep it
  attached to that fact in the final answer instead of choosing citations again.
- `source_context` holds literal media attributes at its own `source_location`.
  Both these attributes and the unit text have already been source-hash verified.
  Cite their returned locations directly; reopening the same source does not add
  verification. Source verification is not canonical approval.
  `companion_units` are complete paragraphs from that same media figure, each
  with its own locator; use them for subject matter and qualifications as needed.
  `source_revisions[source_file]` holds the verified SHA-256; `./` paths use
  `binding.project_root`. Text, headings, order and locators are preserved.
- `search_scope.source_scan_complete` means authorized map paths were read and
  hash-verified. `partial` means some units were withheld from the output, not
  an unfinished scan. Neither proves semantic exhaustiveness or absence.
- Finish once the answer or conflict is supported. Do not re-scan for confirmation,
  alternate citations, synonyms, or merely because output is partial. If a value
  is unsupported, say the returned evidence does not establish it and cite what
  is supported. A threshold is not a measurement. Do not claim universal absence.
- Follow up only for an identified missing source/locator/qualifier or scope error;
  explicit exhaustive audits still need further checks. Paths mentioned inside
  source text are unverified references: do not guess or blindly probe report paths.
  A missing requested value is not evidence of a missing unit. A report name alone
  does not establish that it contains the value. In either case, give the bounded
  unsupported conclusion now; do not search again just to prove absence.

`omitted_units` counts whole units withheld by the UTF-8 hits `answer_budget`
(default 8,000 bytes; binding metadata additional). Legacy `--read-only` is label-only.
On binding/freshness failure, stop retrieval and report `unverified`. Never bypass
validation, use a foreign/global map, or create/rebuild config. Optional diagnostics:
`--binding-only`, [project-binding.md](references/project-binding.md).
This command writes nothing; changes or conflict settlement require authorization.
