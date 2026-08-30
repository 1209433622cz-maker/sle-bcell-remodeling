# QiTeng Figure Object Persistence Gate v1.0

Compatible core: `QiTeng Academic Writing Skill v0.3.21`

Calibration source: same-case v0.3.20 release regression.

## 1. The failure

A manuscript can preserve:
- Figure 1/2/3 captions;
- figure callouts;
- legends;
- citation integrity;

while the actual embedded figures are gone.

Hard:

> **FIGURE CAPTION COUNT != FIGURE OBJECT COUNT.**

> **TEXT QA PASS != ARTIFACT OBJECT PASS.**

## 2. Protected scientific objects

Before any bulk manuscript edit, inventory:
- inline/anchored images;
- figure paragraphs;
- tables;
- equations;
- text boxes;
- captions;
- cross-references.

Surface or language edits must not alter this inventory unless the task explicitly changes those objects.

## 3. Pre/post object checksum

For each protected object record:
`OBJECT_ID -> TYPE -> COUNT -> LOCATION -> CAPTION/OWNER -> SIZE/RELATIONSHIP`.

After editing:
- object count must match expected count;
- every Figure caption must have its actual object;
- every actual figure must have the correct caption;
- no duplicate or orphaned media relationships.

## 4. Dangerous operations

High-risk operations include:
- assigning `paragraph.text = ...` on paragraphs that may contain drawings;
- deleting a paragraph range without checking for image-only paragraphs;
- rebuilding sections from text extraction only;
- replacing entire body XML while keeping only paragraph text;
- copying captions without copying relationships/media.

Hard:

> **DO NOT TREAT AN EMPTY-TEXT PARAGRAPH AS EMPTY CONTENT.**

An empty paragraph may own a figure, field, bookmark, or other non-text object.

## 5. Release gate

For any DOCX with figures:
1. run structural image audit;
2. compare expected figure count to actual drawings;
3. compare caption count to actual drawings;
4. render DOCX;
5. visually inspect every page;
6. verify every figure appears at readable size and next to the correct caption.

No release if any of these fail.

## 6. Same-case regression

v0.3.20 house-review copy:
- Figure captions = 3;
- actual drawing objects = 0.

This was a genuine false PASS from caption/text-based QA.

v0.3.21 repaired copy:
- Figure captions = 3;
- actual drawing objects = 3;
- 34/34 pages rendered and visually inspected;
- scientific text, 140-reference system, citation order, abbreviation and surface rules preserved.

Core formula:

> **SCIENTIFIC OBJECTS ARE FIRST-CLASS MANUSCRIPT CONTENT, EVEN WHEN THEIR PARAGRAPHS CONTAIN NO TEXT.**
