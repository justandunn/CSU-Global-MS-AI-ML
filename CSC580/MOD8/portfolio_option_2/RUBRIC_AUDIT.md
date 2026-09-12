# CSC580 Final Portfolio Option 2 Rubric Audit

Audit date: September 12, 2026

This checklist records submission readiness against the 300-point Canvas rubric. It documents evidence and identifies residual grading risk; it does not guarantee an instructor-assigned score.

| Rubric criterion | Points | Evidence reviewed | Readiness |
|---|---:|---|---|
| Requirements | 60 | Option 2 is identified; the research section is three rendered body pages; four use cases are analyzed; the implementation uses six integers from 1 through 50, reverses the first three, reserves zero as the start token, and evaluates 100 new sequences. | Ready |
| Content | 60 | The report explains machine translation, conversational speech recognition, image captioning, and abstractive summarization, then connects the architecture to the implemented sequence task. | Ready |
| Problem Solving | 40 | The report explains teacher forcing, separate training and inference graphs, autoregressive decoding, acceptance criteria, the single failed test case, limitations, and practical improvements. | Ready |
| Part 2 Programming Implementation | 80 | The documented Keras source compiles; training, inference encoder, and inference decoder models are present; the runtime record reports 20,000 training, 2,000 validation, and 100 held-out test sequences; exact-match accuracy is 99/100 and final validation token accuracy is 100%. | Ready |
| Sources | 20 | Four scholarly works are included: Sutskever et al. (2014), Chan et al. (2016), Vinyals et al. (2015), and Rush et al. (2015). | Ready |
| Application of Source Material | 10 | Each source is cited in the relevant use-case analysis and used to support an architectural or application claim. | Ready |
| Organization, Grammar, and Style | 20 | The ten-page report has a clear title page, research section, implementation analysis, conclusion, references, figure sequence, and consistent academic tone. All rendered pages were visually inspected. | Ready |
| APA | 10 | The report includes an APA-style title page, page numbers, headings, matching in-text citations and references, figure numbers/titles/notes, double-spaced body text, and hanging reference indents. | Ready |

## Deliverable Integrity

- Python source passed `py_compile` on September 12, 2026.
- Runtime output contains 100 held-out prediction rows and reports 99/100 exact matches.
- The Word report renders to ten pages; the research body occupies pages 2 through 4.
- The final ZIP passed CRC validation and contains exactly the Python source, Word report, runtime output, and flowchart PNG.
- Final ZIP SHA-256: `33821FDA432157309906E10B45D5A218A7D27E8063BB286110DC402CDF259908`.

## Submission Note

The project is ready for submission. The principal residual risk is instructor judgment regarding the depth of analysis and APA interpretation; no missing rubric component or technical packaging defect was found in this audit.
