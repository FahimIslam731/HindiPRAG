HindiPRAG: Revised Project Proposal (B2/M1/M2 comparison)

Includes the official course ACL-style PDF, editable .tex, bibliography, and provided ACL style assets.

Implemented revisions:
- Added author Fahim Abrar Islam, University of California, Davis, faislam@ucdavis.edu.
- Replaced two-way B2 vs M with nested three-way B2/M1/M2 objectives.
- Defined M1 as pairwise + reversal-margin; M2 as pairwise + reversal-margin + paraphrase-invariance.
- Added hyperparameter selection on validation families and exclusion of ambiguous/tied labels.
- Primary comparison: M2 vs M1 on selective consistency, with JRA checked for tradeoffs.
- Exact McNemar and family-cluster bootstrap 95% confidence intervals.
- Generated-response check: direct Qwen vs M1 vs M2 on the same response pools.
- Narrowed novelty claim to benefit of paraphrase consistency beyond matched reversal-margin training.

Remaining author detail: The course requires groups of three; the third author's name, affiliation, and email are not supplied and have not been invented. Add them when known.

To compile on Overleaf: upload HindiPRAG_Revised_Proposal.tex, references.bib, acl.sty, and acl_natbib.bst. Set the main file to HindiPRAG_Revised_Proposal.tex and compile with pdfLaTeX + BibTeX.
