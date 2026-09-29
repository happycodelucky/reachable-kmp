---
title: API reference
---

# API reference

Every public declaration of `reachable` and `reachable-testing`, read from the
ABI dumps committed with the source. The build fails whenever the code and its
dump disagree, so this page always matches the released code. It's built for
scanning; the site's `/llms-full.txt` inlines it.

It lists signatures only. Doc comments, and declarations that exist only on
Android or the JVM, are in the [Dokka reference]({{ config.site_url }}api/).
From Swift, `StateFlow`s arrive as `AsyncSequence`s and enums `switch`
exhaustively (see [iOS](platforms/ios.md)).

Reading the dumps: `com.example/Type` is the type `Type` in package
`com.example`, `<init>` is a constructor, and `= ...` marks a parameter with a
default value.

{{ api_reference() }}
