---
title: Changelog
# Changeset bodies are arbitrary Markdown; don't let mkdocs-macros read a
# `{{ … }}` in one as template syntax.
render_macros: false
---

# Changelog

Every release of Reachable, newest first. Versions follow
[SemVer](https://semver.org/); each release is published to Maven Central
and tagged on GitHub. Pin to a tag, never to `branch: "main"`. Each entry is
assembled from the changesets merged since the previous release, when its
release PR is opened.

<!-- changesets: the Release PR workflow inserts each new release below this line. Keep it. -->

## 0.15.0 — 2026-09-29

### Breaking changes

#### Rename the Swift module to ReachableKit; lower the AAR's compileSdk floor ([#16](https://github.com/happycodelucky/reachable-kmp/pull/16))

Swift consumers now import ReachableKit from the reachable-kmp package. Android consumers need compileSdk 34 or later instead of 36.

###### Swift: the module is now `ReachableKit`

The XCFramework, its Swift module and the SPM product are renamed from
`Reachable` to `ReachableKit`, following the `<Name>Kit` convention that keeps
the module name distinct from the library's public types. The repository is
now `happycodelucky/reachable-kmp` (the old URL redirects), so SPM's package
identity changes too.

```swift
// Before
.package(url: "https://github.com/happycodelucky/reachable.git", from: "0.14.0")
.product(name: "Reachable", package: "reachable")
import Reachable

// After
.package(url: "https://github.com/happycodelucky/reachable-kmp.git", from: "0.15.0")
.product(name: "ReachableKit", package: "reachable-kmp")
import ReachableKit
```

The Swift API itself is unchanged. Kotlin consumers are unaffected: the Maven
coordinates stay `com.happycodelucky.reachable:reachable`.

###### Android: a lower compileSdk floor

The AAR used to require consumers to compile against the SDK the library was
built with (36). It now declares a deliberate floor of **34**, so the library
no longer forces a compileSdk bump on your app when ours moves.

###### JVM bytecode

The Android and JVM artifacts now pin Java 21 bytecode explicitly, rather than
following the JDK the release happened to be built on.

## 0.14.0 and earlier

### Public API

- **`Reachability.shared`** — process-lifetime singleton on the
  `Reachability` interface's `companion object`. Callable from anywhere
  at any time, with no Context plumbing required. Replaces the pattern of
  constructing `Reachability(context)` in `Application.onCreate` and
  threading it through your DI graph.
    - `close()` on `Reachability.shared` is an intentional **no-op** —
      the singleton lives for the process; the OS reaps the platform
      observer at process exit.
    - From Swift: `Reachability.shared` via an in-framework Swift
      extension (`src/appleMain/swift/Reachability+Shared.swift`); the
      raw `ReachabilityCompanion` call is hidden.
- `interface Reachability : AutoCloseable` exposing
  `val status: StateFlow<ReachabilityStatus>` and `fun close()`.
- Single-axis shortcuts on `Reachability`:
    - `val isReachable: Boolean` — synchronous online check.
    - `val isDataMetered: Boolean` — synchronous metered-path check
      (cellular, hotspot, or Apple Low Data Mode).
    - `val reachable: StateFlow<Boolean>` — reactive variant of
      `isReachable`, conflated so transport and metering changes don't emit.
    - `val dataMetered: StateFlow<Boolean>` — reactive variant of
      `isDataMetered`.
- `data class ReachabilityStatus(isReachable, transport, isDataMetered)`.
  Boolean fields are `is`-prefixed; the unprefixed names are reserved for
  the `StateFlow<Boolean>` shortcuts on `Reachability`. Invariant:
  `!isReachable ⇒ !isDataMetered` — unreachable paths never report
  metered, so callers can read `isDataMetered` without first checking
  reachability.
- `enum class Transport { Wifi, Cellular, Ethernet, Other, None }`.
- **No separate `Metering` axis.** Apple's `nw_path_is_constrained` (Low
  Data Mode) folds into `isDataMetered` alongside `nw_path_is_expensive`;
  Android's metered/unmetered capability bits map to the same boolean.
  Consumers who want the cellular-vs-Wi-Fi distinction read `transport`;
  consumers who want "should I defer this transfer" read `isDataMetered`.
  The Apple-only Low Data Mode signal is not separately exposed in the
  public API.
- Top-level factories: `Reachability()` on Apple, `Reachability(context)` on
  Android. Still available for explicit-lifecycle use (tests, per-feature
  observers). For general use, prefer `Reachability.shared`.

### Implementation

- **`androidx.startup` integration (Android)**: `ReachabilityInitializer`
  (an `androidx.startup.Initializer`) is registered in the library's
  `AndroidManifest.xml` under `InitializationProvider` with
  `tools:node="merge"`. It attaches `Reachability.shared` to the
  application `Context` during the ContentProvider startup pass — before
  `Application.onCreate`. Consumers get auto-init for free; no manifest
  changes required. `androidx.startup:startup-runtime:1.2.0` is a new
  `implementation` dependency of the library.
- **Two-phase Android construction**: `AndroidReachability` now has a
  zero-arg primary constructor (no OS calls, no Context) and an
  `internal fun attach(context)` that is idempotent (first-call-wins via
  CAS). The existing `Reachability(context)` factory still calls
  `attach()` immediately. The singleton path defers `attach()` to the
  `ReachabilityInitializer`.
- Apple: `nw_path_monitor` via `platform.Network` cinterop, on a
  per-instance serial dispatch queue.
- Android: `ConnectivityManager.NetworkCallback` against
  `NET_CAPABILITY_INTERNET + NET_CAPABILITY_VALIDATED`. `status.value` is
  seeded synchronously from `connectivityManager.activeNetwork` so it's
  meaningful immediately after construction.
- Shared base class owns a `SupervisorJob`-rooted scope and an atomic close
  latch. `close()` is idempotent.

### Distribution

- Published to Maven Central as
  `com.happycodelucky.reachable:reachable` via
  [vanniktech maven-publish](https://github.com/vanniktech/gradle-maven-publish-plugin).
  Includes the Android AAR plus the `kotlinMultiplatform` metadata and
  the `iosArm64`, `iosSimulatorArm64`, `macosArm64` klibs, all signed.
- Companion artifact `com.happycodelucky.reachable:reachable-testing`
  published alongside the main artifact. Provides `FakeReachability` and
  `withFakeReachability { }` for installing a scriptable fake as
  `Reachability.shared` for the duration of a test. Add as
  `testImplementation` / `commonTest` — see
  [Installation → Testing support](installation.md#testing-support).
- A native Swift Package Manager artifact is **not** published in v0.1.
  (Added in a later release — see
  [Installation → Swift Package Manager](installation.md#swift-package-manager).)

### Known limitations

- VPN-over-Wi-Fi resolves to `Transport.Wifi` (the underlying physical
  transport). No separate `VPN` value.
- No captive-portal detection callback. Apple and Android both handle
  captive-portal flow at the OS level; the library surfaces the resolved
  `isReachable` boolean only.
- No `androidHostTest` for `AndroidReachability`'s deferred-attach path.
  Blocked on adding Robolectric or a `ConnectivityManager` wrapper interface.
  End-to-end coverage currently provided by the Android sample app.
