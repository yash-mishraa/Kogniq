from bs4 import BeautifulSoup

from ...normalized.metadata import DocumentMetadata
from ...resource.handle import ResourceHandle
from .statistics import HTMLProcessorStatistics


def extract_metadata(
    soup: BeautifulSoup, handle: ResourceHandle, stats: HTMLProcessorStatistics
) -> tuple[str, DocumentMetadata]:
    title = ""
    subject: str | None = None
    keywords: tuple[str, ...] | None = None

    # 1. <title> tag
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    if not title:
        # 2. First h1
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            title = h1.get_text(strip=True)

    if not title:
        # 3. First heading
        first_heading = soup.find(["h2", "h3", "h4", "h5", "h6"])
        if first_heading and first_heading.get_text(strip=True):
            title = first_heading.get_text(strip=True)

    if not title:
        # 4. Filename
        title = handle.filename

    if title and title != handle.filename and stats.metadata_availability is not None:
        stats.metadata_availability["title"] = True

    description_meta = soup.find("meta", attrs={"name": "description"})
    if description_meta and description_meta.get("content"):
        content = description_meta["content"]
        if isinstance(content, str):
            subject = content.strip()
            if stats.metadata_availability is not None:
                stats.metadata_availability["description"] = True

    keywords_meta = soup.find("meta", attrs={"name": "keywords"})
    if keywords_meta and keywords_meta.get("content"):
        content = keywords_meta["content"]
        if isinstance(content, str):
            kw_list = [k.strip() for k in content.split(",") if k.strip()]
            if kw_list:
                keywords = tuple(kw_list)
                if stats.metadata_availability is not None:
                    stats.metadata_availability["keywords"] = True

    return title, DocumentMetadata(subject=subject, keywords=keywords)
