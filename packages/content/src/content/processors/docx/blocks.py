from docx.document import Document as DocxDocument
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType
from .statistics import DOCXProcessorStatistics


def extract_blocks(
    doc: DocxDocument, stats: DOCXProcessorStatistics
) -> tuple[NormalizedBlock, ...]:
    normalized_blocks = []
    order = 0

    for child in doc.element.body:
        if isinstance(child, CT_P):
            p = Paragraph(child, doc)
            text = p.text.strip()

            if not text:
                continue

            style_name = p.style.name if p.style else ""
            block_type = BlockType.PARAGRAPH

            if style_name.startswith("Heading") or style_name == "Title":
                block_type = BlockType.HEADING
                stats.headings_extracted += 1
            elif "List" in style_name:
                block_type = BlockType.LIST
                stats.lists_extracted += 1
            else:
                stats.paragraphs_extracted += 1

            normalized_blocks.append(
                NormalizedBlock(
                    block_id=f"docx_block_{order}", block_type=block_type, text=text, order=order
                )
            )
            order += 1
            stats.total_blocks += 1

        elif isinstance(child, CT_Tbl):
            t = Table(child, doc)
            table_text = ""
            for row in t.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_text += "| " + " | ".join(row_data) + " |\n"

            table_text = table_text.strip()
            if table_text:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"docx_block_{order}",
                        block_type=BlockType.TABLE,
                        text=table_text,
                        order=order,
                    )
                )
                order += 1
                stats.tables_extracted += 1
                stats.total_blocks += 1

    return tuple(normalized_blocks)
