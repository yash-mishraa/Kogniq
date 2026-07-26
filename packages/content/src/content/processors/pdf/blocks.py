import re

import fitz  # type: ignore

from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType


def _clean_block_text(text: str) -> str:
    # 1. Join hyphenated words across lines
    text = re.sub(r'([a-zA-Z])-\n([a-zA-Z])', r'\1\2', text)
    
    # 2. Join lines inside paragraphs while preserving logical breaks
    lines = text.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        if i == 0:
            cleaned_lines.append(line)
        else:
            prev_line = cleaned_lines[-1]
            # Keep line breaks for end of sentences, bullet points,
            # or short lines (often headers/equations)
            if (
                re.search(r'[.!?:]$', prev_line) 
                or prev_line.startswith(('-', '*')) 
                or len(prev_line) < 40
            ):
                cleaned_lines.append(line)
            else:
                # Append to previous line with a space
                cleaned_lines[-1] = f"{prev_line} {line}"
                
    return '\n'.join(cleaned_lines)


def extract_blocks(page: fitz.Page) -> tuple[NormalizedBlock, ...]:
    blocks_raw = page.get_text("blocks")
    normalized_blocks = []

    for i, b in enumerate(blocks_raw):
        # PyMuPDF get_text("blocks") returns: (x0, y0, x1, y1, "text", block_no, block_type)
        if len(b) >= 7 and b[6] == 0:
            raw_text = b[4].strip()
            if not raw_text:
                continue

            clean_text = _clean_block_text(raw_text)
            
            # Discard blocks that are purely meaningless isolated numbers or symbols
            # (e.g., page numbers "12", "42", or stray punctuation)
            stripped = clean_text.strip()
            if len(stripped) <= 4 and re.fullmatch(r'^[\W\d]+$', stripped):
                continue

            normalized_blocks.append(
                NormalizedBlock(
                    block_id=f"b_{page.number}_{i}",
                    block_type=BlockType.PARAGRAPH,
                    text=clean_text,
                    bbox=(b[0], b[1], b[2], b[3]),
                    order=i,
                )
            )

    return tuple(normalized_blocks)
