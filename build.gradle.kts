/*
 * Reachable — root build script.
 *
 * Plugins are declared here with `apply false`; they're applied in :reachable.
 * This keeps `gradle/libs.versions.toml` as the single source of truth for
 * versions (CLAUDE.md §10).
 */

plugins {
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.android.kotlin.multiplatform.library) apply false
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.skie) apply false
    alias(libs.plugins.kmmbridge.github) apply false
    alias(libs.plugins.ktlint) apply false
    alias(libs.plugins.detekt) apply false
    // KSP is not used in v1 (no Koin Annotations, no codegen). Add when needed.

    // Dokka v2: Kotlin API doc generator. Produces HTML for the public API of
    // every source set. The HTML is copied into docs/api/ for mkdocs to bundle.
    alias(libs.plugins.dokka)
}

allprojects {
    group = "com.happycodelucky.reachable"
    // `version` lives in gradle.properties: the last version released from
    // main, bumped only by the release PR (scripts/changeset.py). CI stamps
    // non-release builds with `-Pversion=…-ci.N`; a pre-release passes its own
    // `-Pversion`. Nothing ever writes an override back.
    version = providers.gradleProperty("version").get()
}

subprojects {
    // ktlint + detekt wire onto the KMP plugin — i.e. onto the published
    // library modules only. CLAUDE.md §3: "ktlint + detekt must pass."
    //
    // Deliberate scope: the sample apps (`:androidApp` here; /apps/ios and
    // /apps/macos outside this Gradle build) are demo scaffolding, not shipped
    // code, and are intentionally excluded from Kotlin lint and from CI's
    // check task. Don't "fix" that by widening this hook — if a sample stops
    // compiling, the fix is in the sample, not the gate.
    pluginManager.withPlugin("org.jetbrains.kotlin.multiplatform") {
        apply(plugin = "org.jlleitschuh.gradle.ktlint")
        apply(plugin = "io.gitlab.arturbosch.detekt")
    }

    plugins.withId("org.jlleitschuh.gradle.ktlint") {
        configure<org.jlleitschuh.gradle.ktlint.KtlintExtension> {
            version.set(libs.versions.ktlint.cli.get())
            android.set(false)
            outputToConsole.set(true)
            ignoreFailures.set(false)
            filter {
                exclude { element -> element.file.path.contains("/build/generated/") }
                exclude("**/build/**")
                exclude("**/generated/**")
            }
        }

        tasks.withType<org.jlleitschuh.gradle.ktlint.tasks.BaseKtLintCheckTask>().configureEach {
            exclude { element -> element.file.path.contains("/build/generated/") }
        }
    }

    plugins.withId("io.gitlab.arturbosch.detekt") {
        configure<io.gitlab.arturbosch.detekt.extensions.DetektExtension> {
            buildUponDefaultConfig = true
            // Project overrides layered on the defaults live in config/detekt.
            config.setFrom(rootProject.files("config/detekt/detekt.yml"))
            // detekt's default source resolution only knows JVM layouts
            // (src/main/kotlin); point it at the module root so every KMP
            // source set (commonMain, appleMain, androidHostTest, …) is
            // scanned. The task itself filters to *.kt, and build/ output
            // is excluded by default.
            source.setFrom(files("src"))
        }
    }
}

// Apply Dokka to the :reachable module and aggregate into docs/api/.
dokka {
    moduleName.set("Reachable")
}

dependencies {
    // Aggregate Dokka HTML from the published modules into the root build
    // (Dokka v2 pattern). `:reachable-testing` is a public-API module too —
    // consumers writing tests want to see the FakeReachability /
    // withFakeReachability surface documented next to the main library.
    dokka(project(":reachable"))
    dokka(project(":reachable-testing"))
}

/**
 * Copies Dokka v2 HTML output into docs/api/, where mkdocs picks it up.
 *
 * The aggregated HTML lives at build/dokka/html after dokkaGeneratePublicationHtml.
 * mkdocs looks at docs/api/ when it builds the site; CI runs Dokka before mkdocs.
 */
tasks.register<Copy>("copyDokkaToDocs") {
    group = "documentation"
    description = "Copies aggregated Dokka HTML into docs/api/ for mkdocs."

    dependsOn("dokkaGeneratePublicationHtml")
    from(layout.buildDirectory.dir("dokka/html"))
    into(layout.projectDirectory.dir("docs/api"))
}
