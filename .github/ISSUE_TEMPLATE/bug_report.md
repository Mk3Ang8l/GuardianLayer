---
name: Bug report
about: Create a report to help us improve GuardianLayer
title: ''
labels: bug
assignees: ''
---

**Summary**
A clear and concise description of the bug. What did you expect to happen, and what happened instead?

**To Reproduce**
Steps to reproduce the behavior:
1. Install GuardianLayer using: `pip install GuardianLayer` (or describe how you installed it)
2. Run the following minimal example (adjust as needed):
   ```python
   # paste a minimal reproducible snippet here
   from GuardianLayer import LoopDetector
   detector = LoopDetector()
   result = detector.check({"tool": "search", "query": "test"})
   print(result)
   ```
3. Describe any specific configuration, inputs, or runtime commands you used.

**Expected behavior**
Describe what you expected to happen.

**Actual behavior**
Describe what actually happened. Include the full error message and stack trace if available.

**Minimal reproducible example**
Provide a minimal, self-contained snippet that reliably demonstrates the issue. Prefer a short example that others can copy/paste and run.

**Environment**
Please fill in the relevant environment information:
- GuardianLayer version: `2.0.0` (or the version you have installed)
- Python version: e.g. `Python 3.10.8`
- Installation method: `pip install GuardianLayer`, `pip install -e .`, from git, etc.
- OS: e.g. `Ubuntu 22.04`, `macOS 12.6`, `Windows 10`
- Additional relevant packages and versions (if relevant): e.g. `aiosqlite 0.19.0`
- If applicable, database or backend used (e.g. SQLite, aiosqlite)

**Logs / Tracebacks**
If available, paste full logs or tracebacks here. Use code blocks to preserve formatting.

```
Paste full traceback and logs here
```

**Screenshots**
If helpful, attach screenshots illustrating the issue.

**Severity**
How severe is the bug?
- [ ] Critical (data loss, crash on startup)
- [ ] Major (core functionality broken)
- [ ] Minor (non-critical bug or incorrect behavior)
- [ ] Cosmetic (typo or UI/problem that doesn't affect functionality)

**Additional context**
Add any other context about the problem here, including:
- Workarounds you found (if any)
- Links to related issues or PRs (if any)
- Which branch or commit you tested (for development versions)

**Checklist before filing**
- [ ] I have searched for existing issues and did not find a duplicate.
- [ ] I can reproduce this bug with the latest release or main branch.
- [ ] I included a minimal reproducible example and environment information.

Thank you for taking the time to report this. We appreciate clear, minimal repro cases — they help us fix issues faster.