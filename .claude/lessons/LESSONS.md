# Lessons Learned — Reachable

Living document. Agents and humans add entries here whenever something is worth
remembering across sessions. Read it before planning non-trivial work and
whenever you get stuck — we may have seen the issue before.

## How to use this file

- **Before planning** a non-trivial change: skim all four sections, then grep for keywords from the task (e.g. `mutex`, `reachability`, `XCFramework`, `SKIE`, `NWPathMonitor`).
- **When stuck** for more than a few minutes: search here before going wider.
- **Add an entry as soon as you learn something** — don't batch. A terse line written now beats a polished paragraph never written.

## How to add an entry

- Pick the right section. If it fits two, pick the one a future reader would search first.
- Allocate the next sequential ID for that section (`B-002`, `D-004`, …). IDs are stable forever — never renumber.
- One to three lines per entry. Cite a file path or commit/PR when useful. No long prose. If you need more than three lines, you're explaining what, not why.
- Code comments may reference an entry by ID (e.g. `// see B-001`).
- If an entry becomes obsolete, mark it `~~B-NNN~~ (superseded by B-NNN)` — do not delete. History matters.

Date format: `YYYY-MM-DD`. Always absolute, never relative ("last week").

For build/toolchain work specifically, [`toolchain-audit.md`](toolchain-audit.md)
is a repeatable audit procedure — the recurring ways build tooling silently
stops working, each with a detection command, plus registry queries for checking
versions without trusting search.

---

## Bugs we've hit (B)

### ~~B-001~~ — Renovate's SKIE-bound Kotlin guard was silently dead (2026-07-30) — obsolete: Renovate removed 2026-09-27 (the app was never installed)
`matchPackagePrefixes` was removed in Renovate **v38**, so the rule enforcing N-006 survived only via silent config migration. It also over-matched: `org.jetbrains.kotlin` prefix-matches `org.jetbrains.kotlinx`, so it was disabling coroutines/atomicfu updates too — and v38+ auto-migration to `org.jetbrains.kotlin{/,}**` preserves that. Fixed with an anchored regex (`/^org\.jetbrains\.kotlin([.:]|$)/`). Validate config against a **current** Renovate major; older validators still accept the removed key.

### B-002 — AGP stamps the AAR's `minCompileSdk` with our compileSdk (2026-09-27)
Left unset, every consumer's `check<Variant>AarMetadata` then demands our compileSdk — raised only for the sample's AndroidX deps (B-004) — surfacing when they assemble. Fixed by `android { aarMetadata { minCompileSdk = <android-min-compile-sdk> } }` in the convention plugin: a separate catalog key (34), decoupled from compileSdk and minSdk.

### B-003 — AGP's KMP Android target is not a `KotlinJvmTarget` (2026-09-27)
It's a `DecoratedExternalKotlinTarget`, so `targets.withType<KotlinJvmTarget>()` never reaches it, and its unset `jvmTarget` follows the build JDK (JDK 25 → Java 25 bytecode in the AAR). Set `jvmTarget` explicitly on `android { compilerOptions {} }` AND `jvm { compilerOptions {} }` from the catalog's `jvm-target`. Verify with the class-file major (65 = 21).

### B-004 — AndroidX bumps can force a compileSdk bump (2026-09-27)
AndroidX AARs carry `minCompileSdk` in their aar-metadata and `checkAarMetadata` enforces it — lifecycle 2.11.0 needs 37, so `:androidApp` failed on main at compileSdk 36. `mise run check` never builds the sample; `mise run build:samples` does, and CI's fast leg runs it.

### B-005 — A custom `applyDefaultHierarchyTemplate { group("apple") }` has no iosMain/macosMain (2026-09-27)
It hangs the targets DIRECTLY off appleMain. The implicit default template has them (native → apple → ios/macos), so drop the block (its lambda form was also experimental).

### B-006 — GitHub templates apply only in the web UI (2026-09-27)
`gh pr/issue create --body` bypasses PR templates and YAML issue forms, so agents follow them only because CLAUDE.md §12 says to. A submitted form renders as `### <label>` + answer per field (`_No response_` when skipped). HTML comments don't nest: a template can't quote `<!-- AI: … -->` inside a comment.

### B-007 — Every `- [ ]` in a PR body is live (2026-09-27)
One click toggles it, and all of them feed the "N of M tasks" counter, which a pick-one group can never complete. Checkboxes appear only in the done-gate; choices are plain bullets you prune, and human review is signalled by leaving draft.

### B-008 — `GITHUB_TOKEN` pushes and PRs trigger no workflows (2026-09-27)
(workflow_dispatch excepted), and creating a PR with it needs "Allow GitHub Actions to create and approve pull requests". release-pr.yml therefore dispatches ci.yml + changeset.yml on `release/next` itself — unless a GitHub App token (`RELEASE_APP_CLIENT_ID`) is configured.

### B-009 — Dokka 2 has no Gradle switch for Markdown output (2026-09-27)
It still ships the `gfm-plugin`: register a `DokkaFormatPlugin(formatName = "markdown")` subclass (an `@InternalDokkaGradlePluginApi` opt-in — re-check on Dokka bumps) for `dokkaGenerate*Markdown` (`gradle/plugins/…/LlmsTxt.kt`). Applying it in the modules only leaves the root's HTML aggregation working.

---

## Novel design decisions (D)

### D-001 — Sealed result types over `kotlin.Result<T>` at the Swift boundary
`kotlin.Result<T>` doesn't bridge to Swift — SKIE has no special mapping, and K/N erases the payload. Use a project-defined `sealed interface`; SKIE renders it as an exhaustive Swift enum via `onEnum(of:)`. Same rule applies to `Pair<A,B>` / `Triple<…>` at public boundaries.

### D-002 — Apple platform-name casing rule overrides Kotlin acronym convention
`iOS`, `macOS`, `tvOS`, `watchOS` are brand names; they stay cased as Apple spells them in all identifiers, file names, and comments we author. JetBrains-supplied identifiers (`iosArm64`, `iosMain`, etc.) are the allowed exception.

### D-003 — `expect`/`actual` cap ~20 lines, otherwise refactor to interface
If an `actual` implementation grows past ~20 lines, refactor to a `commonMain` interface and inject platform implementations at the entrypoint. Keeps the `expect`/`actual` surface minimal and testable.

### D-004 — JVM backend polls `NetworkInterface`; `isReachable` is best-effort, not validated
The JDK has no connectivity callback and no validation probe (unlike Apple's `nw_path_monitor` / Android's `NET_CAPABILITY_VALIDATED`), so `JvmReachability` polls `java.net.NetworkInterface` on the base-class scope (default 5s) and maps via the pure `mapJvmInterfaces`. Consequences baked into the public KDoc + docs: captive portals are invisible, `isDataMetered` is always `false`, transport is name-inferred (`Transport.Other` when ambiguous, e.g. macOS `en0`). Host-only bridges (`docker0`, `vmnet*`, …) are filtered so a Docker-running laptop reads offline in airplane mode; VPN tunnels (`utun*`) count. No HTTP probe by design — a library phoning home by default is worse than an honest weak signal.

### D-005 — Adding a KMP target touched zero common code
Adding `jvm` needed only: `jvm()` in the convention plugin (the existing `targets.withType<KotlinJvmTarget>` JVM_21 block, written for Android, covered it), a one-line `createSharedReachability()` actual, and the platform impl. The `expect` seam being a single function (see D-003) is what made a third platform a pure addition.

### D-004 — JVM backend polls `NetworkInterface`; reachability there is best-effort by design (2026-06-11)
The JDK has no connectivity callback and no validation probe, so `JvmReachability` polls `java.net.NetworkInterface` (default 5 s), filters loopback / link-local / host-only bridges (`docker0` etc.), infers `Transport` from interface names (`Other` when ambiguous, e.g. macOS `en0`), and always reports `isDataMetered = false`. A built-in HTTP probe was rejected: a library phoning a hardcoded endpoint by default is worse than an honest weaker signal. See `Mapping.jvm.kt` and `docs/platforms/jvm.md`.

### D-006 — Releases are changeset-driven (2026-09-27)
`version=` in gradle.properties is the single source of the version, bumped only by the rolling release PR (`scripts/changeset.py`); release.yml publishes when a push to main CHANGES it. A changeset's `change` is the author's call and the source of truth; while 0.x a `major` bumps the minor, and only a `version:` pin leaves 0.x. A PR needs a changeset only when it touches a file in release scope (`.changeset/config.toml`); `no-changeset` covers the rest. Stable versions never come from a manual dispatch (pre-releases / retries only), so main, the changelog and Maven Central can't drift.

### D-007 — The released Package.swift lives only on the tag (2026-09-27)
main is branch-protected (1 approving review), so no workflow pushes to it — the old "commit Package.swift to main" step would have failed after the irreversible Maven Central publish. The release commit carrying the remote-binary Package.swift is a detached commit on its `vX.Y.Z` tag; main keeps the local-dev form. SPM resolves the manifest from the tag.

### D-008 — The Apple framework / Swift module is `ReachableKit` (2026-09-27)
`<PascalName>Kit`, derived in the convention plugin and matched by KMMBridge's `frameworkName`. A module named like one of its public types makes SKIE rename the type in Swift (`Reachable_`) and lets the bare type shadow the module qualifier in SKIE's generated Swift. Renamed from `Reachable` in 0.15.0 (breaking `import`); don't rename it again.

### D-009 — Line length is set once, in `.editorconfig` (120) (2026-09-27)
Editors show it, ktlint enforces it and `mise run format` wraps to it; detekt's `MaxLineLength` is off (`config/detekt/detekt.yml`) so no second copy can drift. ktlint ignores `max_line_length` in EVERY rule when its `max-line-length` rule is disabled, so that rule stays on. ktlint_official's parameter-count forced-multiline signatures are `unset` (it otherwise wraps a 1-param constructor).

### D-010 — The repo is `happycodelucky/reachable-kmp` (2026-09-27)
Renamed from `reachable`. github.com URLs redirect but GitHub Pages does not (the site is `happycodelucky.github.io/reachable-kmp/`), and SPM's package identity is the URL's last component (`package: "reachable-kmp"`). Maven coordinates stay `com.happycodelucky.reachable:reachable`.

### D-011 — Every published jar and the AAR carry llms.txt + llms-full.txt (2026-09-27)
Under `META-INF/<groupId>/<artifactId>/` — namespaced because a bare `META-INF/llms.txt` from two libraries fails a consumer's Android packaging (duplicate java resource). In the AAR they sit at the archive root, not in classes.jar, so they never reach an APK. Klibs hold no resources; native targets ship them in their sources jars and host-specific `-metadata.jar`s (KGP's `<target>MetadataElements` Jar task). Packed only when the requested tasks include a publish task — packing always would run Dokka on every check. `mise run llms:check` verifies the published set.

---

## NEVER DO (N)

### N-001 — Never include `CancellationException` in `@Throws` on SKIE-bridged APIs
SKIE bridges `suspend fun` as Swift `async throws` and routes cancellation through Swift's `Task.cancel()` / `CancellationError`. Adding `CancellationException::class` pollutes the generated signature and forces callers to write a meaningless `catch is CancellationError` arm.

### N-002 — Never call `suspend` functions inside a `kotlinx.atomicfu.locks.synchronized` block
`synchronized` on K/N is a non-reentrant spin-wait; suspending inside it can deadlock the coroutine dispatcher. If the body needs to suspend, use a `Mutex` instead.

### N-003 — Never use `kotlin.synchronized`, `@Synchronized`, `java.util.concurrent.locks.*`, or `volatile`
None are portable to K/N or wasm. Use `kotlinx.atomicfu.locks.synchronized` (non-suspending) or `kotlinx.coroutines.sync.Mutex` (suspending).

### N-004 — Never use `kotlin.Result<T>` / `Pair<…>` / `Triple<…>` in public Swift-facing signatures
See D-001. Use a named `sealed interface` instead.

### N-005 — Never add CocoaPods, Compose Multiplatform, x86/x86_64, watchOS, or tvOS
See CLAUDE.md §13 hard rules.

### N-006 — Never bump Kotlin past SKIE's supported range
SKIE lags Kotlin by a few days after each release. If SKIE doesn't yet support the new Kotlin version, wait — don't force-bump.

### N-007 — Never read wall-clock time inside dispatcher / scheduler logic
Direct `Clock.System.now()` reads make test virtual time lie. Inject the clock or compute delays from injected timestamps.

### N-008 — Never call ObjC/Foundation APIs while holding a Kotlin-side lock
ObjC/Foundation can invoke callbacks re-entrantly on the same thread; acquiring a Kotlin lock before crossing the ObjC boundary risks deadlock.

---

## Troubleshooting (T)

### T-001 — Tests pass but production timing behaviour drifts
Root cause is almost always a wall-clock read inside production logic (see N-007). Verify that all time sources are injected and that tests drive virtual time via `runTest`.

### T-002 — "SDK location not found" in a git worktree (2026-09-27)
A worktree doesn't carry the gitignored `local.properties`, so AGP fails at task-graph time. Copy it in (`cp local.properties.example local.properties`, or from the main checkout).

### T-003 — Build JDK stays 21 (2026-09-27)
detekt 1.23.8's embedded Kotlin compiler crashes on JDK 25 (detekt/detekt#8714), and it's also the remaining Gradle 10 blocker (`ReportingExtension.file(String)`). Both are fixed in detekt 2.x — revisit when it's stable. Check `build/reports/problems/` after Gradle bumps.
