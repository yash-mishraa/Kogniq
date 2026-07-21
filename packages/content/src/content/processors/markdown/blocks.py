from markdown_it.token import Token

from ...normalized.block import NormalizedBlock
from ...normalized.enums import BlockType
from .statistics import MarkdownProcessorStatistics


def extract_blocks(
    tokens: list[Token], stats: MarkdownProcessorStatistics
) -> tuple[NormalizedBlock, ...]:
    normalized_blocks = []

    i = 0
    n = len(tokens)
    order = 0

    while i < n:
        token = tokens[i]

        # Heading
        if token.type == "heading_open":
            i += 1
            content = ""
            while i < n and tokens[i].type != "heading_close":
                if tokens[i].type == "inline":
                    content += tokens[i].content
                i += 1

            content = content.strip()
            if content:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"md_block_{order}",
                        block_type=BlockType.HEADING,
                        text=content,
                        order=order,
                    )
                )
                order += 1
                stats.headings_extracted += 1

        # Paragraph
        elif token.type == "paragraph_open":
            i += 1
            content = ""
            while i < n and tokens[i].type != "paragraph_close":
                if tokens[i].type == "inline":
                    content += tokens[i].content
                i += 1

            content = content.strip()
            if content:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"md_block_{order}",
                        block_type=BlockType.PARAGRAPH,
                        text=content,
                        order=order,
                    )
                )
                order += 1
                stats.paragraphs_extracted += 1

        # Fenced code
        elif token.type == "fence":
            content = token.content.strip()
            if content:
                text_content = f"```{token.info}\n{content}\n```" if token.info else content
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"md_block_{order}",
                        block_type=BlockType.CODE,
                        text=text_content,
                        order=order,
                    )
                )
                order += 1
                stats.code_blocks_extracted += 1

        # Blockquote
        elif token.type == "blockquote_open":
            i += 1
            content = ""
            while i < n and tokens[i].type != "blockquote_close":
                if tokens[i].type == "inline" or tokens[i].type == "fence":
                    content += tokens[i].content + "\n"
                i += 1

            content = content.strip()
            if content:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"md_block_{order}",
                        block_type=BlockType.QUOTE,
                        text=content,
                        order=order,
                    )
                )
                order += 1

        # Lists (ul, ol)
        elif token.type in ("bullet_list_open", "ordered_list_open"):
            list_type = token.type
            i += 1
            content = ""
            list_close_type = (
                "bullet_list_close" if list_type == "bullet_list_open" else "ordered_list_close"
            )

            item_count = 1
            while i < n and tokens[i].type != list_close_type:
                if tokens[i].type == "list_item_open":
                    content += f"{item_count}. " if list_type == "ordered_list_open" else "- "
                    item_count += 1
                elif tokens[i].type == "inline":
                    content += tokens[i].content + "\n"
                i += 1

            content = content.strip()
            if content:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"md_block_{order}",
                        block_type=BlockType.LIST,
                        text=content,
                        order=order,
                    )
                )
                order += 1
                stats.lists_extracted += 1

        # Tables
        elif token.type == "table_open":
            i += 1
            content = ""
            while i < n and tokens[i].type != "table_close":
                if tokens[i].type == "tr_open":
                    content += "| "
                elif tokens[i].type in ("th_open", "td_open"):
                    pass
                elif tokens[i].type == "inline":
                    content += tokens[i].content + " | "
                elif tokens[i].type == "tr_close":
                    content += "\n"
                i += 1

            content = content.strip()
            if content:
                normalized_blocks.append(
                    NormalizedBlock(
                        block_id=f"md_block_{order}",
                        block_type=BlockType.TABLE,
                        text=content,
                        order=order,
                    )
                )
                order += 1
                stats.tables_extracted += 1

        # Horizontal rule
        elif token.type == "hr":
            normalized_blocks.append(
                NormalizedBlock(
                    block_id=f"md_block_{order}",
                    block_type=BlockType.UNKNOWN,
                    text="---",
                    order=order,
                )
            )
            order += 1

        else:
            # Code_block (indented code block)
            if token.type == "code_block":
                content = token.content.strip()
                if content:
                    normalized_blocks.append(
                        NormalizedBlock(
                            block_id=f"md_block_{order}",
                            block_type=BlockType.CODE,
                            text=content,
                            order=order,
                        )
                    )
                    order += 1
                    stats.code_blocks_extracted += 1

        i += 1

    return tuple(normalized_blocks)
