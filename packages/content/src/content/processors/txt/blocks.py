from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType
from .statistics import TXTProcessorStatistics


def is_underline_line(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) >= 3:
        return all(c in ("=", "-") for c in stripped)
    return False


def is_markdown_heading(line: str) -> bool:
    stripped = line.lstrip()
    if not stripped.startswith("#"):
        return False
    count = 0
    for c in stripped:
        if c == "#":
            count += 1
        else:
            break
    return 1 <= count <= 6 and len(stripped) > count and stripped[count].isspace()


def is_all_caps_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) >= 100:
        return False

    alpha_chars = [c for c in stripped if c.isalpha()]
    if not alpha_chars:
        return False

    uppercase_chars = [c for c in alpha_chars if c.isupper()]

    if len(uppercase_chars) / len(alpha_chars) <= 0.8:
        return False

    non_space_chars = [c for c in stripped if not c.isspace()]
    if not non_space_chars:
        return False
    return len(alpha_chars) / len(non_space_chars) >= 0.5


def extract_blocks(
    lines: list[str], stats: TXTProcessorStatistics
) -> tuple[NormalizedBlock, ...]:
    normalized_blocks = []
    order = 0

    def add_heading(text: str) -> None:
        nonlocal order
        normalized_blocks.append(
            NormalizedBlock(
                block_id=f"txt_block_{order}",
                block_type=BlockType.HEADING,
                text=text.strip(),
                order=order,
            )
        )
        order += 1
        stats.headings_extracted += 1
        stats.total_blocks += 1

    def add_paragraph(text: str) -> None:
        nonlocal order
        normalized_blocks.append(
            NormalizedBlock(
                block_id=f"txt_block_{order}",
                block_type=BlockType.PARAGRAPH,
                text=text.strip(),
                order=order,
            )
        )
        order += 1
        stats.paragraphs_extracted += 1
        stats.total_blocks += 1

    i = 0
    while i < len(lines):
        line = lines[i]
        stats.line_count += 1
        stats.character_count += len(line)
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if is_markdown_heading(stripped):
            add_heading(stripped)
            i += 1
            continue

        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if is_underline_line(next_line):
                add_heading(stripped)
                stats.line_count += 1
                stats.character_count += len(lines[i + 1])
                i += 2
                continue

        if is_all_caps_heading(stripped):
            add_heading(stripped)
            i += 1
            continue

        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line_raw = lines[i]
            stripped_next = next_line_raw.strip()

            if not stripped_next:
                break

            if is_underline_line(stripped_next):
                last_line = para_lines.pop()
                if para_lines:
                    add_paragraph("\n".join(para_lines))
                add_heading(last_line)
                stats.line_count += 1
                stats.character_count += len(next_line_raw)
                i += 1
                para_lines = []
                break

            if is_markdown_heading(stripped_next):
                break

            if is_all_caps_heading(stripped_next):
                break

            para_lines.append(stripped_next)
            stats.line_count += 1
            stats.character_count += len(next_line_raw)
            i += 1

        if para_lines:
            add_paragraph("\n".join(para_lines))

    return tuple(normalized_blocks)
