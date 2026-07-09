import fitz  # type: ignore

from ...normalized.metadata import DocumentMetadata


def extract_metadata(doc: fitz.Document) -> tuple[str, DocumentMetadata]:
    meta = doc.metadata or {}
    title = meta.get("title", "")
    author = meta.get("author", "")

    return title, DocumentMetadata(
        author=author if author else None,
    )
