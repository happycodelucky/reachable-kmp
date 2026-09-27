<!--
  Thanks for contributing to Reachable! This template is filled in the same
  way by a human or a coding agent:

  - Comments that start with "AI:" are fill-in instructions. They stay hidden
    in the rendered PR; keep or delete them.
  - A section holding an "Unfilled" callout (a `> [!IMPORTANT]` block) is
    required. Replace the whole callout with your content. No "Unfilled"
    callout should survive into a ready-for-review PR.
  - Plain bullet lists are choices: keep the line(s) that apply and delete the
    rest. Checkboxes appear only in the done-gate, so the PR list's "N of M
    tasks" counter tracks exactly that gate.
  - Delete any other section that doesn't apply, or write "N/A".

  Agents: CLAUDE.md §12 covers opening the PR (draft by default).
-->

## Summary

<!-- AI: What changed and why, in 1–3 sentences a reviewer can read before
     the diff. Lead with the behavior change, not the file list. Replace
     `Closes #` with the issue number, or delete the line. -->

> [!IMPORTANT]
> _Unfilled — what changed and why._

Closes #

## Type of change

<!-- AI: The changeset decides this, not the PR. Its `change` field is the
     source of truth for the release version (.changeset/README.md) — this
     section only restates it, naming the file. Keep the line(s) matching this
     PR's changeset(s) and delete the rest. The labels are the usual reading
     of each level, but the level is the author's call: a change can ship at
     another level for a reason, which belongs in the changeset's body. -->

- `major` — breaking change · `.changeset/<file>.md`
- `minor` — new, compatible feature · `.changeset/<file>.md`
- `patch` — bug fix · `.changeset/<file>.md`
- None — nothing here reaches consumers: no file in release scope (`.changeset/config.toml`), or labelled `no-changeset`

## Affected platforms

<!-- AI: Keep every target the change can reach and delete the rest, or
     write "None" for a docs/tooling-only change. The JVM compile hides
     Native-only bugs, so a commonMain change needs Native verification too. -->

- iOS
- macOS
- Android
- JVM
- commonMain (all targets)

## Reviewer focus

<!-- AI: Keep each area this PR touches that deserves a careful look and
     delete the rest, then name where a reviewer should start (file:line or
     symbol) and why. If nothing is risky, replace the list with
     "Routine — no hotspots." -->

- Public API — the `api/` dump diff (CLAUDE.md §10)
- Swift boundary — SKIE output, `@ObjCName`, `@Throws`, sealed → enum (§8)
- Concurrency — scope ownership, `Mutex` / `synchronized`, injected `Clock` (§3)
- New or bumped dependencies (§5)
- Build logic / CI — convention plugins, `mise.toml`, workflows

**Start here:** _…_

## Open questions

<!-- AI: Anything that needs a human decision: an ambiguous requirement, a
     trade-off you couldn't settle, a check you couldn't run (and why). Write
     "None." if there are none — an empty section is not the same as "None." -->

> [!IMPORTANT]
> _Unfilled — list open questions, or write "None."_

## Decisions & trade-offs

<!-- AI: Non-obvious choices made while implementing, each with the
     alternative you rejected and why. If a decision is load-bearing beyond
     this PR, also add it to .claude/lessons/LESSONS.md and cite its ID here.
     Delete this section if there were none. -->

## How it was verified

<!-- AI: Evidence, not assertions. List each command you actually ran with
     its result (e.g. `mise run check` → BUILD SUCCESSFUL), and name the new
     or changed tests. Never list a command you did not run; if something
     couldn't be verified, say so under Open questions. "It compiles" is not
     verification. -->

> [!IMPORTANT]
> _Unfilled — commands run and their results._

## Done-gate checklist

<!-- AI: These mirror CLAUDE.md §3–§13. Tick only what you verified for this
     PR. Leave a box unticked, and explain under Open questions, rather than
     tick it on faith. -->

- [ ] `mise run check` passes (ktlint + detekt + ABI check + every test target, both modules)
- [ ] `./gradlew :reachable:linkDebugFrameworkIosArm64` builds clean — the JVM compile alone is not a sufficient gate
- [ ] `mise run build:samples` passes if dependencies or the public API changed — `check` never builds the Android sample (LESSONS B-004)
- [ ] New/changed logic has `commonTest` coverage (`runTest` virtual time, no `Thread.sleep`)
- [ ] Public API changes follow the Swift-interop rules (§8): `@ObjCName` verbs, sealed → exhaustive enum, `@Throws` listing the domain exceptions (never `CancellationException`), no `kotlin.Result<T>` / `Pair` at the boundary
- [ ] If the public API changed intentionally, `mise run api:dump` was run and the `api/` diff is committed and reviewed (§10)
- [ ] New dependencies were sourced per §5 (Step 1 table → klibs.io → platform-native), are stable, and were added to `gradle/libs.versions.toml` only
- [ ] A changeset is committed (`mise run changeset`) with its release note written in place of the Unfilled callout, or nothing in it reaches consumers: it changes no file in release scope (`.changeset/config.toml`) or is labelled `no-changeset` (§9) — the Changeset check enforces both
- [ ] Docs updated (`docs/` + KDoc) for any public API or behavior change
- [ ] Anything non-obvious learned is recorded in `.claude/lessons/LESSONS.md` (§12)
- [ ] No hard-rule violations (§13): no Compose MP, CocoaPods, x86, `GlobalScope`, `!!` in production, `java.time` in common, `kotlin.synchronized`/`@Synchronized`/`volatile`, callback public APIs, UI deps in the library, EAP/RC/Beta deps

## AI assistance

<!-- AI: Disclosure, not a gate — the checklist above applies no matter who
     wrote the code. Keep exactly one line and delete the rest. If an agent
     wrote any of it, name the tool and model; otherwise write "N/A". Human
     review isn't recorded here: an agent opens the PR as a draft, and a human
     marking it ready is the review sign-off. -->

- None
- AI-assisted — human-written, AI suggested
- AI-authored

**Tool / model:** _…_
