---
title: Rename the Swift module to ReachableKit; lower the AAR's compileSdk floor
change: major
description: Swift consumers now import ReachableKit from the reachable-kmp package. Android consumers need compileSdk 34 or later instead of 36.
---

### Swift: the module is now `ReachableKit`

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

### Android: a lower compileSdk floor

The AAR used to require consumers to compile against the SDK the library was
built with (36). It now declares a deliberate floor of **34**, so the library
no longer forces a compileSdk bump on your app when ours moves.

### JVM bytecode

The Android and JVM artifacts now pin Java 21 bytecode explicitly, rather than
following the JDK the release happened to be built on.
