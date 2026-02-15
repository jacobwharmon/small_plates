# CLAUDE.md

## Project Overview

This project generates a **dynamic Markdown document** that can be viewed in a web browser (desktop or mobile).
The Markdown content is **derived entirely from a Google Sheet** and regenerated automatically.

The document is **read-only**, **single-user**, and optimized for **simplicity, longevity, and zero-cost hosting**.

---

## Core Principles

1. Simple is better than clever
2. Prefer free hosting
3. Python-first implementation
4. Static output whenever possible
5. Markdown is the source of truth
6. No authentication
7. Only one viewer (the project owner)

---

## High-Level Architecture

Google Sheet  
↓  
Python fetch + transform script  
↓  
Generated Markdown (.md)  
↓  
Static Markdown rendering  
↓  
Free hosting (e.g., GitHub Pages)

---

## Hosting Framework

### Preferred Stack

| Layer | Choice | Rationale |
|---|---|---|
| Data | Google Sheets | Free, structured, editable |
| Language | Python | Readable, minimal dependencies |
| Output | Markdown | Human-readable, portable |
| Hosting | GitHub Pages | Free, static, HTTPS |
| Automation | GitHub Actions | Free CI for regeneration |

No backend servers.  
No databases.  
No paid services.

---

## Data Source: Google Sheets

### Required Columns

| Column | Type | Notes |
|---|---|---|
| topic | varchar | Not unique |
| body | varchar | One or more sentences |
| sources | varchar | Semicolon-separated list |
| timestamp | timestamp | Auto-generated on row creation |

### Data Rules

- Each row represents a single atomic statement
- Ordering is determined only by timestamp
- Topic grouping is case-insensitive
- Original text casing is preserved for display

---

## Dynamic Markdown Specification

### Global Structure

# Table of Contents  
- Topic A  
- Topic B  

## Topic A  
* Paragraph text¹²  

### Topic A Sources  
1) Source  
2) Source

---

## Table of Contents Rules

- Appears at the top of the document
- Contains all unique topic values
- Topics are alphabetically sorted (A → Z)
- Topics are hyperlinked to section anchors
- Topic titles are consistently title-cased

---

## Topic Sections

For each unique topic:

- Create a second-level header (## Topic Name)
- Include all rows matching that topic
- Sort rows by timestamp (oldest → newest)
- Render each row as:
  - A Markdown bullet
  - The body text
  - Superscript source references at the end

---

## Source Parsing and Superscripts

### Parsing Rules

- Split the sources column on semicolons
- Trim whitespace
- Preserve original order per row

### Numbering Rules

- Source numbering resets per topic
- Numbers increment across paragraphs in the topic
- Identical sources are not deduplicated
- Superscripts reflect exact numbering

### Superscript Format

Use inline HTML:

<sup>1</sup>  
<sup>1,2</sup>

---

## Sources Subsection

Each topic ends with a sources subsection:

### Topic Name Sources

- Ordered list
- Numbers must match superscripts exactly
- Format:

1) Source text or URL  
2) Source text or URL

---

## Python Implementation Guidance

### Data Fetching (Preferred Order)

1. Public Google Sheets CSV export
2. gspread with service account
3. Google Sheets API v4

Prefer CSV when possible for simplicity.

---

## Transformation Steps

1. Fetch sheet data
2. Normalize topics
3. Group rows by topic
4. Sort topics alphabetically
5. Sort rows by timestamp
6. Generate:
   - Table of contents
   - Topic sections
   - Superscripts
   - Sources subsections

---

## File Structure

/
├─ generate.py  
├─ small_plates.md  
├─ README.md  
└─ CLAUDE.md

---

## Rendering Strategy

### Option A

View Markdown directly on GitHub

### Option B

Render Markdown to HTML and host on GitHub Pages

---

## Automation (Optional)

- GitHub Actions on schedule or manual trigger
- Regenerates Markdown
- Commits updated output

---

## Non-Goals

- Authentication
- Multiple viewers
- Real-time updates
- Inline editing
- JavaScript-heavy UI

---

## Success Criteria

- Updating the Google Sheet updates the document
- Readable on phone and laptop
- Hosting costs $0
- Understandable in one sitting
- Works unattended for years

---

## Final Instruction

Choose the simplest solution that satisfies the requirements.
Prefer static over dynamic.
Prefer boring over fancy.