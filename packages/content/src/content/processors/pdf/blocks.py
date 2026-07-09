import fitz  # type: ignore

from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType


def extract_blocks(page: fitz.Page) -> tuple[NormalizedBlock, ...]:
    blocks_raw = page.get_text("blocks")
    normalized_blocks = []

    for i, b in enumerate(blocks_raw):
        # PyMuPDF get_text("blocks") returns: (x0, y0, x1, y1, "text", block_no, block_type)
        if len(b) >= 7 and b[6] == 0:
            text = b[4].strip()
            if not text:
                continue

            normalized_blocks.append(
                NormalizedBlock(
                    block_id=f"b_{page.number}_{i}",
                    block_type=BlockType.PARAGRAPH,
                    text=text,
                    bbox=(b[0], b[1], b[2], b[3]),
                    order=i,
                )
            )

    return tuple(normalized_blocks)
