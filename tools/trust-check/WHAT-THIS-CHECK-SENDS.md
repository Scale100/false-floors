# What this check sends

The default Stage 1 scan reads files and Git metadata in the repository you choose. It writes its two assessment files into that same repository. It does not upload source files, file paths, branch names, repository names, findings, or assessment results.

By default, it makes one unauthenticated HTTPS request to GitHub's public False Floors release-tag feed. That request is used only to tell you whether the bundled catalogue is older than a published catalogue release. It sends no GitHub credential and no repository-specific value. A three-second timeout, response-size limit, pagination cap, and disabled redirects/proxies bound that request. If it fails, the check uses its bundled catalogue and says that freshness could not be checked.

Run with `--offline` to make no network request at all.

The optional `--allow-github OWNER/REPO --github-branch BRANCH` mode is different. It makes bounded, read-only GitHub API requests through your `gh` login to inspect that named repository's policy settings. It sends the repository identity and uses your existing GitHub authentication; it does not send local source content.

The check prints a compact summary for the assistant that invoked it. Anything else an assistant receives depends on what you choose to paste or ask it to read. The scanner itself is local and does not operate a hosted service or collect telemetry.
