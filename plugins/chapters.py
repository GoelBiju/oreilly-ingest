from .base import Plugin
from core.types import ChapterInfo
import config


class ChaptersPlugin(Plugin):
    """Plugin for fetching book chapters and their content."""

    def fetch_list(self, book_id: str) -> list[ChapterInfo]:
        """Fetch list of chapters for a book."""
        url = f"{config.API_V2}/epub-chapters/?epub_identifier=urn:orm:book:{book_id}"
        chapters: list[ChapterInfo] = []

        while url:
            data = self.http.get_json(url)
            for ch in data.get("results", []):
                chapters.append(ChapterInfo(
                    ourn=ch.get("ourn", ""),
                    title=ch.get("title", ""),
                    filename=self._extract_filename(ch.get("reference_id", "")),
                    content_url=ch.get("content_url", ""),
                    images=(ch.get("related_assets") or {}).get("images", []),
                    stylesheets=(ch.get("related_assets") or {}).get("stylesheets", []),
                    virtual_pages=ch.get("virtual_pages"),
                    minutes_required=ch.get("minutes_required"),
                ))
            url = data.get("next")

        return chapters

    def fetch_toc(self, book_id: str) -> list[dict]:
        url = f"{config.API_V2}/epubs/urn:orm:book:{book_id}/table-of-contents/"
        data = self.http.get_json(url)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("results", [])
        return []

    # Front matter the TOC usually leaves out, in the order it appears in a book.
    _FRONT_MATTER_KEYWORDS = (
        "cover",
        "praise",
        "halftitle",
        "titlepage",
        "title-page",
        "copyright",
        "dedication",
        "epigraph",
        "contents",
        "toc",
        "foreword",
    )

    def reorder_by_toc(self, chapters: list[ChapterInfo], toc: list[dict]) -> list[ChapterInfo]:
        """Reorder chapters to match the TOC reading order."""
        ordered_filenames = self._flatten_toc_filenames(toc)
        if not ordered_filenames:
            return chapters

        chapter_map = {ch["filename"]: ch for ch in chapters}

        ordered = []
        for filename in ordered_filenames:
            if filename in chapter_map:
                ordered.append(chapter_map.pop(filename))

        # Split remaining into front matter (before TOC content) and back matter (after)
        front = []
        back = []
        for ch in chapters:
            if ch["filename"] not in chapter_map:
                continue
            rank = self._front_matter_rank(ch)
            if rank is not None:
                front.append((rank, ch))
            else:
                back.append(ch)

        # The chapter list has no guaranteed order, so front matter is put in
        # conventional book order rather than the order it was listed in.
        front.sort(key=lambda item: item[0])

        return [ch for _, ch in front] + ordered + back

    def _front_matter_rank(self, ch: ChapterInfo) -> int | None:
        """Return the chapter's position among front matter, or None if it is not front matter."""
        filename_lower = ch["filename"].lower()
        title_lower = ch["title"].lower()
        for rank, keyword in enumerate(self._FRONT_MATTER_KEYWORDS):
            if keyword in filename_lower or keyword in title_lower:
                return rank
        return None

    def fetch_content(self, content_url: str) -> str:
        return self.http.get_text(content_url)

    def _extract_filename(self, reference_id: str) -> str:
        if "-/" in reference_id:
            return reference_id.split("-/")[1]
        return reference_id

    def _flatten_toc_filenames(self, toc_items: list[dict]) -> list[str]:
        """Extract ordered, deduplicated filenames from the TOC tree."""
        result: list[str] = []
        seen: set[str] = set()

        def walk(items: list[dict]):
            for item in items:
                ref_id = item.get("reference_id", "")
                if ref_id:
                    filename = self._extract_filename(ref_id)
                    if filename and filename not in seen:
                        result.append(filename)
                        seen.add(filename)
                children = item.get("children", [])
                if children:
                    walk(children)

        walk(toc_items)
        return result
