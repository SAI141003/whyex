# whyex — launch content (ready-to-post)

> **Before posting:** replace every `https://github.com/SAI141003/whyex` with the real repo URL, and swap the illustrative demo transcripts below for real captures from the current build.
>
> Verified facts used (keep accurate everywhere): offline, zero dependencies, pure Python stdlib · 144 curated rules across 27 categories · covers git, Python, Node/TS, Go, Rust, Java, Ruby, C/C++, Docker, Kubernetes, shell, network, databases · safe auto-fixes via `whyex fix`, always confirmed first · severity + confidence on every diagnosis · structured `--json` · extensible via `whyex contribute` · ~70 ms per diagnosis, ~39 ms cold start · MIT · installs via pip, pipx, Homebrew, installer script.

---

## Show HN

**Title**

```
Show HN: Whyex – explain any terminal error offline, no API key
```

**Body**

I built a CLI that explains terminal errors — locally, instantly, and without sending anything anywhere. Feed it an error message (pasted or piped) and it returns a plain-language explanation of what went wrong and, for many cases, a suggested fix. If you want, `whyex fix` applies the fix, but only after showing it to you and getting a yes.

How it works:

- ~144 hand-curated diagnostic rules across 27 categories. Each rule pairs one or more patterns with an explanation, a severity, a confidence level, and optionally a fix template.
- Matching is prioritized — specific patterns outrank generic ones — so the same error always produces the same explanation. Deterministic and testable.
- No AI, no model downloads, no network calls, no telemetry. Pure Python standard library, zero third-party dependencies. That's also why it's quick: ~39 ms cold start, ~70 ms per diagnosis on my machine.

Stacks covered today: git, Python, Node/TypeScript, Go, Rust, Java, Ruby, C/C++, Docker, Kubernetes, shell, networking, and databases.

What it can't do yet:

- Anything outside the 144 rules gets no explanation — there is no fallback that improvises an answer.
- It knows error classes, not your codebase. Logic bugs in your own code are out of scope.
- Fixes are deliberately conservative: mechanical, well-understood changes only, always confirmed before anything happens.
- Long logs where the real failure sits far above the final error line remain hard.

Install (MIT): pip, pipx, Homebrew, or the installer script — https://github.com/SAI141003/whyex

If you hit an error it doesn't recognize, please open an issue — or run `whyex contribute`, which scaffolds a rule file for you. The format is intentionally small, so a useful contribution is a short, reviewable diff.

Questions welcome, especially on the curated-rules-versus-LLM tradeoff.

---

## Product Hunt

**Tagline** (47 characters)

```
Explain any terminal error offline — no API key
```

**Description** (one paragraph)

Whyex is an open-source CLI that turns cryptic terminal errors into plain-English explanations — entirely offline. It checks your error against 144 curated diagnostic rules spanning git, Python, Node/TypeScript, Go, Rust, Java, Ruby, C/C++, Docker, Kubernetes, shell, networking, and databases, then explains what happened with a severity and a confidence rating. For well-understood mistakes it proposes a safe auto-fix that is never applied without your confirmation. Built purely on the Python standard library: zero dependencies, no account, no telemetry, ~70 ms per diagnosis. MIT-licensed and free.

**Highlights**

- Fully offline and private — pure Python stdlib, zero dependencies, nothing leaves your machine
- 144 curated rules across 27 categories, from everyday git traps to Kubernetes failures
- Safe auto-fixes: `whyex fix` previews the change and always asks before applying it
- Severity + confidence on every diagnosis, plus structured `--json` for editors and CI
- Small and fast: ~39 ms cold start, ~70 ms per diagnosis

**Maker's first comment**

Hi everyone — I built this. It started as a notes file: I kept leaving the terminal to search for the same recurring errors and kept finding the same answers. The notes became rules, the rules became a matcher, and eventually the matcher became a CLI. Everything shipped today is deliberately unglamorous: 144 curated rules, deterministic prioritized matching, severity and confidence on every result, JSON output for tooling, and a `whyex fix` mode that treats your filesystem as something it needs permission to touch. Next up: broader framework coverage driven by contributors (`whyex contribute` scaffolds a rule file for you), editor integrations built on the JSON output, and more safe-fix recipes. I'll say plainly where an AI assistant is still the better choice: brand-new framework errors and anything tangled in your own application logic. Whyex is for the repeat offenders — answered offline, in milliseconds, the same way every time. Tell me which errors interrupt you most and I'll turn them into rules.

---

## Reddit

### r/commandline

**Title**

```
I kept googling the same terminal errors, so I built an offline CLI that explains them (demo inside)
```

**Body**

That's whyex. Details for the technically inclined:

- Offline, no API keys, no telemetry. Pure Python stdlib, zero third-party dependencies.
- 144 curated rules across 27 stacks: git, Python, Node/TS, Go, Rust, Java, Ruby, C/C++, Docker, K8s, shell, network, databases.
- Prioritized pattern matching — specific beats generic, output is deterministic.
- `whyex fix` applies the suggested fix after you confirm. Always confirm, no exceptions.
- `--json` mode with severity/confidence, for wiring into editors or CI.
- ~39 ms cold start, ~70 ms per diagnosis. MIT license.

I'm the author. Install via pip, pipx, Homebrew, or the installer script: https://github.com/SAI141003/whyex

Tell me the errors that bite you most often and I'll write the rules — contributions via `whyex contribute` are small diffs by design.

### r/Python

**Title**

```
Whyex: diagnosing terminal errors offline with a stdlib-only rules engine (144 rules, zero dependencies)
```

**Body**

Author here. whyex takes an error message and returns a human-readable diagnosis: what happened, how severe it is, how confident the matcher is, and usually a safe suggested fix it can apply after confirmation.

Why it might interest this crowd, implementation-first:

- Zero dependencies — the entire tool is Python standard library. Cold start stays around 39 ms and nothing breaks when third-party ecosystems shift underneath you.
- Diagnoses come from ~144 declarative rules across 27 categories: patterns with priorities, plus severity/confidence metadata and optional fix templates. Specific patterns outrank generic ones, which makes results deterministic and unit-testable.
- Extending it is a supported workflow, not a fork request: `whyex contribute` scaffolds a new rule file, so covering an error you know well doesn't require reading the codebase.
- `--json` exposes stable keys (category, severity, confidence, explanation, fix) for building editor or CI tooling on top.

The design argument I keep having with myself is curated rules versus an LLM. Rules lose on novelty: an unknown error gets silence, not a plausible-sounding guess. They win on latency (~70 ms), determinism, privacy, and working air-gapped. For the errors people hit every week, that trade seems right — and the rule format is small enough that coverage is a community task rather than a training run.

Repo: https://github.com/SAI141003/whyex — pip/pipx/Homebrew/installer, MIT. Critiques of the rule schema and matching approach particularly welcome.

---

## dev.to / blog outline

**Working title:** Explaining terminal errors offline: why I shipped 144 curated rules instead of calling a model

**Intro (before first H2)**

- Open on the loop every reader knows: a one-line error, a browser tab, a decade-old forum thread, ten lost minutes.
- Thesis: most terminal errors are repeats; repeats can be encoded; encoding them costs milliseconds, not API credits.

## The problem: debugging by context switch

- Narrate one concrete incident end-to-end (use a real one from your own history).
- The expense is interruption, not difficulty: each lookup breaks flow, and the answer is usually the same one as last time.
- Observation that started the project: a few dozen recurring error shapes accounted for nearly all of these interruptions.

## The design: curated rules, prioritized matching, no network

- Anatomy of a rule: patterns, category, severity, confidence, explanation, optional fix template.
- Prioritized matching: specific patterns outrank generic ones; identical input yields identical output; every diagnosis reports its own confidence.
- Offline by construction: no API key, no model download, no telemetry — works on planes and in locked-down CI runners.
- Honest limits, stated plainly — when an LLM assistant is the better tool:
  - errors from libraries or frameworks the rule set doesn't cover yet;
  - problems rooted in your application logic rather than in the error text;
  - messy multi-cause logs that need reasoning across many lines.
- Positioning sentence to land: whyex answers the repeat offenders instantly and privately; save the LLM for the genuinely novel.

Demo 1 — a basic diagnosis:

```console
$ whyex "ModuleNotFoundError: No module named 'requests'"
python · missing third-party module
severity: medium · confidence: high

The interpreter couldn't find 'requests' on its import path — either
it isn't installed in the active environment or the wrong environment
is active.

Suggested fix:
  pip install requests

Apply this fix? [y/N]
```

## The auto-fix safety model

- Principle: diagnose generously, mutate reluctantly.
- `whyex fix` proposes only mechanical, well-understood changes; every proposal is shown in full and applied only after explicit confirmation.
- Nothing writes in the background, ever; declining a fix changes nothing.
- Out of scope on purpose: multi-file rewrites, destructive commands, anything requiring judgment about your intent.

Demo 2 — the confirmed fix:

```console
$ whyex fix
1 proposed fix pending:
  pip install requests
Apply? [y/N] y
Applied. Re-run your original command to verify.
```

## Structured output: --json for editors and CI

- Stable schema: category, severity, confidence, summary, fix object.
- Three consumers worth showing: an editor plugin rendering the diagnosis inline, a CI step annotating failed jobs, a shell wrapper capturing stderr automatically.
- Why determinism pays downstream: same input, same JSON — snapshot-testable and cacheable.

Demo 3 — JSON mode:

```json
$ whyex --json "fatal: not a git repository"
{
  "category": "git",
  "severity": "low",
  "confidence": "high",
  "summary": "This directory is not a git repository; no .git was found here or in any parent.",
  "fix": { "command": "git init", "note": "only if you intend to track this directory" }
}
```

## Growing the rule base with contributors

- 144 rules across 27 categories so far, nearly all from real errors that actually interrupted someone.
- `whyex contribute` scaffolds the rule file; a good contribution is a short, reviewable diff plus the exact error string that triggers it.
- Call to action: reply with the most recent error that sent you to a browser.

## Roadmap

- Near term: coverage growth through contributor rules; editor integrations on top of `--json`.
- Later: a wider catalog of safe fixes under the same confirm-first policy.
- Non-goals, framed as commitments: no chatbot mode, no network-dependent features, no telemetry.

## Closing

- Two-sentence recap: deterministic, offline, millisecond-scale help for known error shapes — and honest silence otherwise.
- Repo link, one-line install command, invitation to contribute a rule.
