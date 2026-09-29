// swift-tools-version:6.0
import PackageDescription

// ReachableKit is the XCFramework's Swift module name (the :reachable module +
// "Kit"). This committed form points at the debug XCFramework Gradle builds, and
// stays that way on main. Each release tags a commit whose Package.swift is the
// remote `.binaryTarget(url:checksum:)` for that version's GitHub Release asset
// — SPM consumers pin a tag and get that form (.github/PUBLISHING.md).
//
//   mise run spm:dev      — rebuild the debug XCFramework + point this file at it
//   mise run spm:restore  — restore the committed form
let packageName = "ReachableKit"

let package = Package(
    name: packageName,
    platforms: [
        .iOS(.v18),
        .macOS(.v15),
    ],
    products: [
        .library(
            name: packageName,
            targets: [packageName]
        ),
    ],
    targets: [
        .binaryTarget(
            name: packageName,
            path: "./reachable/build/XCFrameworks/debug/ReachableKit.xcframework"
        ),
    ]
)
