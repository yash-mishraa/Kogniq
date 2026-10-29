# Document Datasets & Corpus Specifications

This directory defines the supported corpus specifications, benchmark documents, and ground-truth evaluation datasets for Kogniq.

---

## Supported Ingestion Formats

| Format | MIME Types | Processing Engine | Features |
| :--- | :--- | :--- | :--- |
| **PDF** | `application/pdf` | `PdfContentProcessor` via `pypdf` | Page-aware text extraction, structured section segmentation, metadata recovery. |
| **Markdown** | `text/markdown`, `.md` | `MarkdownContentProcessor` | Header-based hierarchy (`#`, `##`, `###`), list parsing, code-block preservation. |
| **LaTeX** | `application/x-tex`, `text/x-tex`, `.tex` | `TexContentProcessor` | Mathematical formula handling, KaTeX-compatible expressions, theorem demarcation. |
| **Plain Text** | `text/plain`, `.txt` | `PlainTextContentProcessor` | Normalization, paragraph tokenization, UTF-8 cleanup. |

---

## Benchmark Corpus & Sample Documents

A governed sample set of academic research papers is stored in [`dev/sample_documents/`](../dev/sample_documents/) to serve as reproducible ground-truth inputs for retrieval and question-answering benchmarks:
- **`2014_Sequence_to_Sequence_Learning.pdf`**: Foundational seq2seq architecture paper (Sutskever et al.).
- **`2017_Convolutional_Sequence_to_Sequence.pdf`**: Convolutional sequence modeling architecture (Gehring et al.).
- **`fairseq_overview.md`**: Modular toolkit documentation for sequence modeling.
