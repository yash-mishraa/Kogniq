from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Comment, NavigableString

from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType
from .statistics import HTMLProcessorStatistics

IGNORED_TAGS = {
    'script', 'style', 'noscript', 'svg', 'canvas', 'iframe',
    'video', 'audio', 'form', 'input', 'button', 'footer',
    'nav', 'aside'
}

def normalize_text(text: str) -> str:
    """Collapses repeated whitespace into a single space."""
    return " ".join(text.split())

def extract_blocks(
    soup: BeautifulSoup, stats: HTMLProcessorStatistics
) -> tuple[NormalizedBlock, ...]:
    normalized_blocks = []
    order = 0
    current_loose_text: list[str] = []

    for tag in soup.find_all(IGNORED_TAGS):
        tag.decompose()

    def flush_loose_text() -> None:
        nonlocal order, current_loose_text
        if current_loose_text:
            text = normalize_text(" ".join(current_loose_text))
            if text:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"html_block_{order}",
                        block_type=BlockType.PARAGRAPH,
                        text=text,
                        order=order,
                    )
                )
                order += 1
                stats.paragraphs_extracted += 1
                stats.total_blocks += 1
            current_loose_text = []

    def traverse(element: Any) -> None:
        nonlocal order

        if isinstance(element, Comment):
            return

        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                current_loose_text.append(text)
            return

        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            flush_loose_text()
            text = normalize_text(element.get_text(separator=" "))
            if text:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"html_block_{order}",
                        block_type=BlockType.HEADING,
                        text=text,
                        order=order,
                    )
                )
                order += 1
                stats.headings_extracted += 1
                stats.total_blocks += 1
            return

        if element.name == 'p':
            flush_loose_text()
            text = normalize_text(element.get_text(separator=" "))
            if text:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"html_block_{order}",
                        block_type=BlockType.PARAGRAPH,
                        text=text,
                        order=order,
                    )
                )
                order += 1
                stats.paragraphs_extracted += 1
                stats.total_blocks += 1
            return

        if element.name == 'li':
            flush_loose_text()
            text = normalize_text(element.get_text(separator=" "))
            if text:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"html_block_{order}",
                        block_type=BlockType.LIST,
                        text=text,
                        order=order,
                    )
                )
                order += 1
                stats.lists_extracted += 1
                stats.total_blocks += 1
            return

        if element.name == 'blockquote':
            flush_loose_text()
            text = normalize_text(element.get_text(separator=" "))
            if text:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"html_block_{order}",
                        block_type=BlockType.QUOTE,
                        text=text,
                        order=order,
                    )
                )
                order += 1
                stats.blockquotes_extracted += 1
                stats.total_blocks += 1
            return

        if element.name in ('pre', 'code'):
            flush_loose_text()
            # Preserve newlines for code blocks if they are preformatted
            if element.name == 'pre':
                text = "\n".join(
                    line.strip()
                    for line in element.get_text().splitlines()
                    if line.strip()
                )
            else:
                text = normalize_text(element.get_text(separator=" "))
                
            if text:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"html_block_{order}",
                        block_type=BlockType.CODE,
                        text=text,
                        order=order,
                    )
                )
                order += 1
                stats.code_blocks_extracted += 1
                stats.total_blocks += 1
            return

        if element.name == 'table':
            flush_loose_text()
            table_text = ""
            for row in element.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                row_data = [normalize_text(cell.get_text(separator=" ")) for cell in cells]
                table_text += "| " + " | ".join(row_data) + " |\n"
            table_text = table_text.strip()
            if table_text:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"html_block_{order}",
                        block_type=BlockType.TABLE,
                        text=table_text,
                        order=order,
                    )
                )
                order += 1
                stats.tables_extracted += 1
                stats.total_blocks += 1
            return

        # Not a known block element, descend into its children
        for child in element.children:
            traverse(child)

    root = soup.body if soup.body else soup
    traverse(root)
    flush_loose_text()

    return tuple(normalized_blocks)
