# Sample Documents

This directory is intended for local developer testing of content processors.

**Do not commit copyrighted or sensitive PDFs, documents, or data.**

All `.pdf`, `.docx`, and similar binary document types in this directory are ignored by Git. 

## Testing

To run the PDF Processor demo, place a sample PDF here (e.g., `transformer_paper.pdf`) and run:

```bash
uv run python dev/demo_pdf_processor.py dev/sample_documents/transformer_paper.pdf
```
