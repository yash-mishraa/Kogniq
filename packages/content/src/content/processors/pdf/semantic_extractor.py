import hashlib
import re
from collections import Counter
from typing import Any

import fitz  # type: ignore


class SemanticExtractor:
    def __init__(self, stream_bytes: bytes, document_id: str) -> None:
        self.stream_bytes = stream_bytes
        self.document_id = document_id

    def extract(self) -> dict[str, Any]:
        doc = fitz.open(stream=self.stream_bytes, filetype="pdf")

        all_spans = []
        lines_info = []
        images = []
        texts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            d = page.get_text("dict")

            for b in d["blocks"]:
                if b["type"] == 1:
                    images.append({"page": page_num + 1, "bbox": b["bbox"]})
                elif b["type"] == 0:
                    block_text = ""
                    for line in b["lines"]:
                        line_text = ""
                        line_size = 0
                        line_font = ""
                        line_bbox = line["bbox"]
                        for s in line["spans"]:
                            text = s["text"].strip()
                            if text:
                                line_text += s["text"] + " "
                                line_size = max(line_size, s["size"])
                                line_font = s["font"]
                                all_spans.append(
                                    {
                                        "size": s["size"],
                                        "text": s["text"].strip(),
                                        "page": page_num + 1,
                                    }
                                )

                        line_text = line_text.strip()
                        if line_text:
                            lines_info.append(
                                {
                                    "page": page_num + 1,
                                    "text": line_text,
                                    "size": line_size,
                                    "font": line_font,
                                    "bbox": line_bbox,
                                }
                            )
                            block_text += line_text + " "

                    block_text = block_text.strip()
                    if block_text:
                        texts.append({"page": page_num + 1, "text": block_text, "bbox": b["bbox"]})

        if not all_spans:
            return {"schema_version": 1, "sections": [], "figures": []}

        # 1. Determine dominant font size
        sizes = [round(s["size"], 1) for s in all_spans]
        dominant_size = Counter(sizes).most_common(1)[0][0]

        # Header/Footer filtering: texts that appear on >= 3 pages
        page_texts: dict[str, set[int]] = {}
        for s in all_spans:
            txt = s["text"]
            if len(txt) > 4:
                page_texts.setdefault(txt, set()).add(s.get("page", 0))
        boilerplate = {k for k, v in page_texts.items() if len(v) >= 3}

        # 2. Extract sections
        sections = []

        for idx, line in enumerate(lines_info):
            text = line["text"]
            size = round(line["size"], 1)
            font = line["font"]

            is_larger = size > dominant_size + 0.5
            has_numbering = bool(re.match(r"^(\d{1,2}(\.\d{1,2})*)\.?\s+[A-Z]", text))
            is_special = text.lower() in (
                "abstract",
                "introduction",
                "conclusion",
                "references",
                "acknowledgments",
                "background",
            )

            is_bold = any(
                x in font.lower()
                for x in ["bold", "cmbx", "cmcsc", "medi", "demi", "black", "heavy"]
            )

            if (
                (has_numbering and size >= dominant_size)
                or (is_larger and is_bold)
                or (is_special and is_bold)
            ):
                if len(text) < 3 or len(text) > 100:
                    continue
                if text in boilerplate:
                    continue

                # Exclude specific non-semantic lines
                if re.match(r"^(Figure|Fig\.|Table)\s*\d", text):
                    continue

                # Title policy: document titles (huge text) are excluded from the section hierarchy.
                if size > dominant_size + 3.0:
                    continue

                level = 1
                match = re.match(r"^(\d+(\.\d+)*)\.?\s", text)
                if match:
                    level = len(match.group(1).split("."))
                elif is_special:
                    level = 1
                else:
                    level = 2

                # Cap level to 6
                level = min(level, 6)

                stable_id_str = (
                    f"{self.document_id}_section_{line['page']}_{idx}_{text}"
                    f"_{line['bbox'][0]}_{line['bbox'][1]}"
                )
                stable_id = hashlib.md5(stable_id_str.encode()).hexdigest()

                sections.append(
                    {
                        "id": stable_id,
                        "page_number": line["page"],
                        "title": text,
                        "level": level,
                        "parent_id": None,
                        "bbox": {
                            "x0": line["bbox"][0],
                            "y0": line["bbox"][1],
                            "x1": line["bbox"][2],
                            "y1": line["bbox"][3],
                        },
                        "source_block_ids": [],
                    }
                )

        # Build hierarchy safely (no cycles, no dangling)
        stack: list[dict[str, Any]] = []
        for s in sections:
            while stack and stack[-1]["level"] >= s["level"]:
                stack.pop()
            if stack:
                s["parent_id"] = stack[-1]["id"]
            stack.append(s)

        # 3. Extract figures
        figures = []
        for idx, img in enumerate(images):
            img_bbox = img["bbox"]
            page_num = img["page"]

            best_caption = None
            best_dist = float("inf")

            for t in texts:
                if t["page"] != page_num:
                    continue
                # Captions usually start with Figure or Fig.
                if re.match(r"^(Figure|Fig\.)\s*\d+", t["text"]):
                    ix0, iy0, ix1, iy1 = img_bbox
                    tx0, ty0, tx1, ty1 = t["bbox"]

                    # Multi-column logic: Ensure caption is horizontally aligned with the image
                    overlap_x = min(ix1, tx1) - max(ix0, tx0)
                    if overlap_x > 0 or abs(ix0 - tx0) < 50:
                        # Caption is vertically near the image (usually below)
                        if ty0 > iy1 - 20 and (ty0 - iy1) < 150:
                            dist = ty0 - iy1
                            if dist < best_dist:
                                best_dist = dist
                                best_caption = t["text"]
                        # Or above
                        elif iy0 > ty1 - 20 and (iy0 - ty1) < 150:
                            dist = iy0 - ty1
                            if dist < best_dist:
                                best_dist = dist
                                best_caption = t["text"]

            figure_number = None
            if best_caption:
                m = re.match(r"^(Figure|Fig\.)\s*(\d+)", best_caption)
                if m:
                    figure_number = f"Figure {m.group(2)}"

            stable_id_str = (
                f"{self.document_id}_figure_{page_num}_{idx}_{img_bbox[0]}_{img_bbox[1]}"
            )
            stable_id = hashlib.md5(stable_id_str.encode()).hexdigest()

            figures.append(
                {
                    "id": stable_id,
                    "page_number": page_num,
                    "bbox": {
                        "x0": img_bbox[0],
                        "y0": img_bbox[1],
                        "x1": img_bbox[2],
                        "y1": img_bbox[3],
                    },
                    "figure_number": figure_number,
                    "caption": best_caption,
                    "image_bbox": {
                        "x0": img_bbox[0],
                        "y0": img_bbox[1],
                        "x1": img_bbox[2],
                        "y1": img_bbox[3],
                    },
                }
            )

        return {"schema_version": 1, "sections": sections, "figures": figures}
