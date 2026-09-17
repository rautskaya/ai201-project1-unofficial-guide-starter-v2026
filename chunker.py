"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in week 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents hierarchically by section headings, then by paragraph.

    Strategy:
    1. Split on ## headings (section boundaries)
    2. Keep sections <= 800 chars as one chunk
    3. Split larger sections by paragraph, combining until ~800 chars
    4. For individual paragraphs > 800 chars, use fixed-size overlap fallback

    Preserves document title and section heading in each chunk for context.
    """
    chunk_size = config.CHUNK_SIZE  # 800
    overlap = config.CHUNK_OVERLAP  # 120
    chunks: list[Chunk] = []

    for doc in documents:
        # Parse document into sections (returns dict with doc_title and sections list)
        parsed = _parse_sections(doc.text)
        doc_title = parsed["title"]
        sections = parsed["sections"]

        chunk_index = 0
        for section in sections:
            section_heading = section["heading"]
            section_text = section["text"].strip()

            if not section_text:
                continue

            # If section is small enough, keep as one chunk
            if len(section_text) <= chunk_size:
                chunk_text = _format_chunk(doc_title, section_heading, section_text)
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        source=doc.source,
                        index=chunk_index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                chunk_index += 1
            else:
                # Split by paragraphs
                paragraphs = [p.strip() for p in section_text.split("\n\n") if p.strip()]
                current_chunk_text = ""

                for para in paragraphs:
                    # If paragraph itself is too large, use fixed-size fallback
                    if len(para) > chunk_size:
                        # Flush current chunk first
                        if current_chunk_text:
                            chunk_text = _format_chunk(
                                doc_title, section_heading, current_chunk_text
                            )
                            chunks.append(
                                Chunk(
                                    text=chunk_text,
                                    source=doc.source,
                                    index=chunk_index,
                                    produced_by="chunker.py::split_documents",
                                )
                            )
                            chunk_index += 1
                            current_chunk_text = ""

                        # Apply fixed-size overlap to the large paragraph
                        para_chunks = _fixed_size_split(para, chunk_size, overlap)
                        for para_chunk in para_chunks:
                            chunk_text = _format_chunk(
                                doc_title, section_heading, para_chunk
                            )
                            chunks.append(
                                Chunk(
                                    text=chunk_text,
                                    source=doc.source,
                                    index=chunk_index,
                                    produced_by="chunker.py::split_documents",
                                )
                            )
                            chunk_index += 1
                    else:
                        # Try to add paragraph to current chunk
                        potential = (
                            (current_chunk_text + "\n\n" + para)
                            if current_chunk_text
                            else para
                        )
                        if len(potential) <= chunk_size:
                            current_chunk_text = potential
                        else:
                            # Paragraph doesn't fit; start new chunk
                            if current_chunk_text:
                                chunk_text = _format_chunk(
                                    doc_title, section_heading, current_chunk_text
                                )
                                chunks.append(
                                    Chunk(
                                        text=chunk_text,
                                        source=doc.source,
                                        index=chunk_index,
                                        produced_by="chunker.py::split_documents",
                                    )
                                )
                                chunk_index += 1
                            current_chunk_text = para

                # Flush final chunk
                if current_chunk_text:
                    chunk_text = _format_chunk(
                        doc_title, section_heading, current_chunk_text
                    )
                    chunks.append(
                        Chunk(
                            text=chunk_text,
                            source=doc.source,
                            index=chunk_index,
                            produced_by="chunker.py::split_documents",
                        )
                    )
                    chunk_index += 1

    return chunks


def _parse_sections(text: str) -> dict:
    """Parse markdown into document title and sections by ## headings.

    Returns dict with:
      'title': document title from # line
      'sections': list of dicts with 'heading' and 'text' keys

    Treats # (single hash) as document title, ## as section boundaries.
    """
    lines = text.split("\n")
    doc_title = ""
    sections = []
    current_heading = ""
    current_text = []

    for line in lines:
        if line.startswith("##"):
            # Save previous section
            if current_heading or current_text:
                sections.append(
                    {"heading": current_heading, "text": "\n".join(current_text)}
                )
                current_text = []
            current_heading = line.lstrip("# ").strip()
        elif line.startswith("#") and not line.startswith("##"):
            # Document title (single #)
            if not doc_title:
                doc_title = line.lstrip("# ").strip()
        else:
            current_text.append(line)

    # Save final section
    if current_heading or current_text:
        sections.append({"heading": current_heading, "text": "\n".join(current_text)})

    return {"title": doc_title, "sections": sections}


def _format_chunk(doc_title: str, section_heading: str, content: str) -> str:
    """Format a chunk with document title and section heading for context."""
    parts = []
    if doc_title:
        parts.append(f"# {doc_title}")
    if section_heading:
        parts.append(f"## {section_heading}")
    parts.append(content.strip())
    return "\n\n".join(parts)


def _fixed_size_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Fixed-size splitting with overlap for oversized paragraphs."""
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
