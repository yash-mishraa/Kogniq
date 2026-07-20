from pathlib import Path
from typing import ClassVar

from backend.core.exceptions import BackendError
from fastapi import UploadFile


class DocumentValidator:
    """
    Centralized validation for document uploads.
    """

    ALLOWED_EXTENSIONS: ClassVar[set[str]] = {".pdf", ".txt", ".md"}
    MAX_SIZE_BYTES: ClassVar[int] = 10 * 1024 * 1024  # 10 MB

    @classmethod
    def validate(cls, file: UploadFile) -> None:
        if not file.filename:
            raise BackendError("invalid_upload", "Filename is missing", status_code=400)

        ext = Path(file.filename).suffix
        if ext.lower() not in cls.ALLOWED_EXTENSIONS:
            raise BackendError(
                "unsupported_extension", f"Extension {ext} is not supported", status_code=400
            )

        if file.size is not None:
            if file.size > cls.MAX_SIZE_BYTES:
                raise BackendError(
                    "file_too_large",
                    f"File size exceeds maximum allowed of {cls.MAX_SIZE_BYTES} bytes",
                    status_code=400,
                )
            if file.size == 0:
                raise BackendError("empty_file", "Uploaded file is empty", status_code=400)
