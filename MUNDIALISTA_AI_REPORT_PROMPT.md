# 🧠 MUNDIALISTA AI — AI Assistant Onboarding Prompt

You are resuming work on the Mundialista AI project. Below is the complete project
context. After reading it, please generate a:

📋 MUNDIALISTA AI — Project Update Report #[NEXT NUMBER]

The report MUST follow this exact structure (matching Reports #1-#5 format):

1. EXECUTIVE SUMMARY (2-3 paragraphs: what happened, key discoveries, current health)
2. WHAT WAS ACCOMPLISHED THIS SESSION (numbered subsections with details, code blocks, tables)
3. CURRENT FILE INVENTORY (full directory tree with version and status per file)
4. GIT HISTORY (all commits, most recent first, with pending commits noted)
5. WHAT WORKS RIGHT NOW (table: Feature | Status | Previous Status | Notes)
6. DEPLOYMENT QUEUE — UPDATED (table: Priority | Item | Dependency | Impact | Status)
7. KNOWN BUGS — CURRENT (table: # | Bug | Severity | File | Status) + Resolved this session
8. FILES NOT YET REVIEWED (table: File | Priority | Notes)
9. TECHNICAL DEBT (table: Item | Severity | Description)
10. EXTERNAL DEPENDENCIES (tables: packages + Kaggle datasets)
11. NEXT SESSION PRIORITIES (numbered list with effort estimates)
12. SESSION METRICS (table: Metric | Value)
13. TECHNICAL REFERENCE (any new system built this session — architecture, function maps, data flows)
14. HOW-TO GUIDES (any new workflows created or changed this session)
15. IMPORTANT NOTES FOR FUTURE AI ASSISTANTS (updated with any new discoveries)

Rules:
- Use tables wherever possible (markdown format)
- Include code blocks for all file changes, commands, and data flows
- Mark completed items with ✅ and strikethrough ~~like this~~
- Mark broken items with ❌ or ⚠️
- Track ALL bugs: new, existing, and resolved
- Track ALL files: active, deprecated, backup, unreviewed
- Include PowerShell commands (user works in PowerShell on Windows)
- When writing patches, use separate .py patch scripts — NOT inline Python -c with complex strings
- Always note what changed since the PREVIOUS report

The previous report number was: #5
The previous report date was: June 2025

---

[PASTE THE COMPLETE PROJECT BIBLE / CONTEXT BELOW THIS LINE]
---

[THEN DESCRIBE WHAT YOU DID THIS SESSION BELOW THIS LINE]
---
