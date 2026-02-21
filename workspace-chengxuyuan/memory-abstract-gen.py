#!/usr/bin/env python3
"""
memory-abstract-gen.py — Extractive summarizer for Markdown files.

Scans a directory of .md files, generates per-file .abstract (JSON) summaries
and a directory-level INDEX.abstract index.  Incremental: only regenerates
when source content changes (based on SHA-256 hash).

Zero external dependencies — Python 3.8+ standard library only.

Inspired by https://github.com/tobi/qmd's contextual indexing approach.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import List, Dict, Optional

# ---------------------------------------------------------------------------
# Extractive summarisation helpers
# ---------------------------------------------------------------------------

_SENTENCE_RE = re.compile(
    r"""
    (?<=[.!?。！？])   # lookbehind: sentence-ending punctuation
    \s+                # whitespace gap
    |
    (?<=\n)            # or after a newline (markdown paragraph boundary)
    """,
    re.VERBOSE,
)

_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```")
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
_BOLD_ITALIC_RE = re.compile(r"[*_]{1,3}([^*_]+)[*_]{1,3}")
_BULLET_RE = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)
_NUMBERED_RE = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_markdown(text: str) -> str:
    """Remove common Markdown formatting, keeping readable text."""
    text = _CODE_BLOCK_RE.sub("", text)
    text = _IMAGE_RE.sub(r"\1", text)
    text = _LINK_RE.sub(r"\1", text)
    text = _INLINE_CODE_RE.sub("", text)
    text = _BOLD_ITALIC_RE.sub(r"\1", text)
    text = _BULLET_RE.sub("", text)
    text = _NUMBERED_RE.sub("", text)
    return text


def _extract_headings(text: str) -> List[str]:
    """Pull heading text out of Markdown."""
    return [m.group(1).strip() for m in _HEADING_RE.finditer(text)]


def _sentences(text: str) -> List[str]:
    """Split text into sentence-like segments."""
    parts = _SENTENCE_RE.split(text)
    out: List[str] = []
    for p in parts:
        p = p.strip()
        if p:
            out.append(p)
    return out


def _rough_token_count(text: str) -> int:
    """Approximate token count (English ≈ words × 1.3, CJK ≈ chars × 0.6)."""
    # count CJK characters
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff"
              or "\u3400" <= ch <= "\u4dbf"
              or "\uf900" <= ch <= "\ufaff")
    words = len(text.split())
    return int(words * 1.3 + cjk * 0.6)


def _score_sentence(sent: str, heading_tokens: set, position: int, total: int) -> float:
    """
    Heuristic score for a sentence.
    Higher is more important.
    """
    score = 0.0
    words = set(re.findall(r"\w+", sent.lower()))

    # Overlap with headings
    overlap = words & heading_tokens
    score += len(overlap) * 2.0

    # Position bias: first and last 20 % of the document get a bonus
    rel_pos = position / max(total, 1)
    if rel_pos < 0.2:
        score += 3.0 - rel_pos * 10  # 3→1 over first 20%
    elif rel_pos > 0.8:
        score += 1.0

    # Length preference: not too short, not too long
    wc = len(sent.split())
    if 8 <= wc <= 40:
        score += 1.0
    elif wc < 5:
        score -= 1.0

    return score


def extractive_summary(text: str, target_tokens: int = 100) -> str:
    """
    Produce a short extractive summary of *text* aiming for ~target_tokens.

    Strategy:
    1. Extract headings as topic indicators.
    2. Split the cleaned body into sentences.
    3. Score sentences by heading overlap + position + length.
    4. Greedily pick top sentences (in original order) until budget.
    """
    headings = _extract_headings(text)
    heading_tokens: set = set()
    for h in headings:
        heading_tokens.update(re.findall(r"\w+", h.lower()))

    clean = _strip_markdown(text)
    sents = _sentences(clean)

    if not sents:
        # Fallback: just truncate
        flat = _WHITESPACE_RE.sub(" ", clean).strip()
        return textwrap.shorten(flat, width=400, placeholder="…")

    total = len(sents)
    scored = [
        (idx, _score_sentence(s, heading_tokens, idx, total), s)
        for idx, s in enumerate(sents)
    ]
    scored.sort(key=lambda t: t[1], reverse=True)

    # Greedily pick sentences up to budget
    picked: List[tuple] = []
    budget = target_tokens
    for idx, sc, s in scored:
        tc = _rough_token_count(s)
        if tc > budget:
            continue
        picked.append((idx, s))
        budget -= tc
        if budget <= 0:
            break

    if not picked:
        # If nothing fit, take the best one truncated
        best = scored[0][2]
        return textwrap.shorten(best, width=400, placeholder="…")

    # Restore original order
    picked.sort(key=lambda t: t[0])
    return " ".join(s for _, s in picked)


# ---------------------------------------------------------------------------
# File hashing & incremental logic
# ---------------------------------------------------------------------------

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_abstract(path: Path) -> Optional[dict]:
    """Read an existing .abstract JSON file, or None."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def process_file(md_path: Path, target_tokens: int = 100, force: bool = False) -> dict:
    """
    Generate or update the .abstract for a single .md file.
    Returns the abstract dict.
    """
    abstract_path = md_path.with_suffix(".abstract")
    content = md_path.read_text(encoding="utf-8")
    content_hash = _sha256(content.encode("utf-8"))

    existing = _read_abstract(abstract_path)

    if not force and existing and existing.get("source_hash") == content_hash:
        return existing  # up-to-date

    summary = extractive_summary(content, target_tokens=target_tokens)
    headings = _extract_headings(content)

    abstract: dict = {
        "source": md_path.name,
        "source_hash": content_hash,
        "headings": headings,
        "summary": summary,
        "tokens_approx": _rough_token_count(summary),
    }

    abstract_path.write_text(
        json.dumps(abstract, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return abstract


def build_index(directory: Path, abstracts: Dict[str, dict]) -> dict:
    """
    Build INDEX.abstract — a directory-level index summarising all files.
    """
    entries: List[dict] = []
    all_headings: List[str] = []

    for name in sorted(abstracts):
        ab = abstracts[name]
        entries.append({
            "file": name,
            "headings": ab.get("headings", []),
            "summary": ab.get("summary", ""),
        })
        all_headings.extend(ab.get("headings", []))

    # Build a concise directory-level overview
    if all_headings:
        topics = list(dict.fromkeys(all_headings))  # dedupe, preserve order
        overview = "Topics covered: " + "; ".join(topics[:30])
        if len(topics) > 30:
            overview += f" … and {len(topics) - 30} more"
    else:
        overview = f"Directory contains {len(entries)} Markdown file(s)."

    index: dict = {
        "directory": str(directory),
        "file_count": len(entries),
        "overview": overview,
        "files": entries,
    }

    # Compute a composite hash so we can skip rewriting if nothing changed
    composite = _sha256(json.dumps(index, sort_keys=True).encode())
    index["index_hash"] = composite

    index_path = directory / "INDEX.abstract"
    existing = _read_abstract(index_path)
    if existing and existing.get("index_hash") == composite:
        return existing  # no change

    index_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return index


def run(directory: Path, target_tokens: int = 100, force: bool = False, quiet: bool = False) -> dict:
    """
    Main entry point.
    Scans *directory* for .md files, generates per-file abstracts, then INDEX.
    Returns the index dict.
    """
    md_files = sorted(directory.glob("*.md"))

    if not md_files:
        if not quiet:
            print(f"No .md files found in {directory}", file=sys.stderr)
        return {}

    abstracts: Dict[str, dict] = {}
    updated = 0

    for md in md_files:
        abstract_path = md.with_suffix(".abstract")
        old_hash = None
        existing = _read_abstract(abstract_path)
        if existing:
            old_hash = existing.get("source_hash")

        ab = process_file(md, target_tokens=target_tokens, force=force)
        abstracts[md.name] = ab

        if ab.get("source_hash") != old_hash:
            updated += 1
            if not quiet:
                print(f"  ✓ {md.name} → {abstract_path.name}")

    index = build_index(directory, abstracts)

    if not quiet:
        total = len(md_files)
        skipped = total - updated
        print(f"\nDone: {total} file(s), {updated} updated, {skipped} skipped (unchanged).")
        print(f"Index: {directory / 'INDEX.abstract'}")

    return index


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate extractive .abstract summaries for Markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s                       # scan ./memory/
              %(prog)s -d ~/notes            # scan custom directory
              %(prog)s --tokens 150 --force  # regenerate all, longer summaries
              %(prog)s --json                # print INDEX to stdout as JSON
        """),
    )
    parser.add_argument(
        "-d", "--directory",
        type=Path,
        default=Path("./memory"),
        help="Directory to scan (default: ./memory/)",
    )
    parser.add_argument(
        "-t", "--tokens",
        type=int,
        default=100,
        help="Target summary length in approximate tokens (default: 100)",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force regeneration even if content unchanged",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Print the INDEX as JSON to stdout (quiet mode)",
    )
    args = parser.parse_args()

    if not args.directory.is_dir():
        print(f"Error: {args.directory} is not a directory.", file=sys.stderr)
        sys.exit(1)

    quiet = args.json_output
    index = run(args.directory, target_tokens=args.tokens, force=args.force, quiet=quiet)

    if args.json_output:
        json.dump(index, sys.stdout, ensure_ascii=False, indent=2)
        print()  # trailing newline


if __name__ == "__main__":
    main()
