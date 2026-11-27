#!/usr/bin/env python3
"""Check the documentation against the project writing standard (docs/STYLE.md).

Run:  python docs/tools/check_docs.py            (all pages in the standard)
      python docs/tools/check_docs.py README.md  (selected pages)

The script uses only the Python standard library. It checks the rules that a
program can measure:

  length      sentence and paragraph length (STE rules 5.1 and section 6)
  word        words that the standard does not approve, with an alternative
  verb        verb forms that the standard does not approve (rules 3.2 to 3.5)
  punct       semicolons, dashes, contractions, Latin abbreviations
  link        each relative link, anchor and image must exist

It prints passive-voice candidates as notes. A person must make the decision,
because "the event is hidden" is a state and "the event is hidden by Onda" is not.

The script does not contain the ASD-STE100 dictionary. The word list below is
this project's own list of words that are frequent in software text.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PAGES = ["README.md", "docs/*.md", "docs/video/README.md", "infrastructure/README.md"]

MAX_WORDS_DESCRIPTION = 25
MAX_WORDS_PROCEDURE = 20
MAX_SENTENCES_PARAGRAPH = 6

# word -> approved alternative. Lower case. Checked as whole words.
NOT_APPROVED = {
    "utilize": "use", "utilizes": "uses", "leverage": "use", "leverages": "uses",
    "ensure": "make sure", "ensures": "makes sure", "verify": "make sure",
    "verifies": "makes sure", "confirm": "make sure", "confirms": "makes sure",
    "allow": "let", "allows": "lets", "enable": "let", "enables": "lets",
    "permit": "let", "permits": "lets",
    "provide": "give", "provides": "gives", "require": "must / is necessary",
    "requires": "must / is necessary", "need": "must / is necessary",
    "needs": "must / is necessary",
    "perform": "do", "performs": "does", "execute": "run / do", "executes": "runs / does",
    "obtain": "get", "obtains": "gets", "receive": "get", "receives": "gets",
    "retrieve": "get", "retrieves": "gets", "acquire": "get", "acquires": "gets",
    "begin": "start", "begins": "starts", "commence": "start", "terminate": "stop",
    "indicate": "show", "indicates": "shows", "demonstrate": "show",
    "demonstrates": "shows", "reveal": "show", "reveals": "shows",
    "expose": "show / give", "exposes": "shows / gives",
    "modify": "change", "modifies": "changes", "alter": "change", "alters": "changes",
    "maintain": "keep", "maintains": "keeps", "retain": "keep", "retains": "keeps",
    "preserve": "keep", "preserves": "keeps", "remain": "stay", "remains": "stays",
    "reduce": "decrease", "reduces": "decreases", "minimize": "decrease",
    "maximize": "increase",
    "determine": "find / calculate", "determines": "finds / calculates",
    "locate": "find", "choose": "select", "chooses": "selects",
    "happen": "occur", "happens": "occurs", "exist": "there is", "exists": "there is",
    "appear": "show / come into view", "appears": "shows / comes into view",
    "consist": "have / contain", "consists": "has / contains", "comprise": "contain",
    "represent": "be / show", "represents": "is / shows",
    "however": "but", "therefore": "thus", "hence": "thus", "although": "but",
    "though": "but", "whereas": "but", "since": "because", "via": "through / with",
    "per": "for each", "within": "in", "upon": "on / when", "towards": "to",
    "which": "that", "whose": "write the sentence again", "whether": "if",
    "may": "can", "might": "can / it is possible that", "could": "can",
    "should": "must", "would": "will", "shall": "must / will",
    "multiple": "many / the number", "several": "some", "various": "different",
    "numerous": "many", "both": "the two", "every": "each / all",
    "any": "a / all / each, or write the sentence again",
    "additional": "more", "extra": "more", "further": "more",
    "prior": "before", "previous": "before / last", "subsequently": "then",
    "afterwards": "then", "currently": "now", "once": "when / after / one time",
    "simply": "(delete)", "just": "(delete) / only", "basically": "(delete)",
    "actually": "(delete)", "really": "(delete)", "quite": "(delete)",
    "robust": "say what it resists", "seamless": "(delete)", "powerful": "(delete)",
    "comprehensive": "full", "regarding": "about", "concerning": "about",
    "issue": "problem", "issues": "problems", "big": "large", "tiny": "very small",
    "huge": "very large", "rather": "and not", "please": "(delete)",
    "okay": "satisfactory", "ok": "satisfactory",
}

# Phrases, checked on the cleaned text of a sentence.
NOT_APPROVED_PHRASES = {
    "in order to": "to", "prior to": "before", "due to": "because of",
    "as well as": "and", "such as": "for example", "a number of": "some",
    "a lot of": "many", "make use of": "use", "take place": "occur",
    "able to": "can", "and/or": "write the two cases", "hard to": "difficult to",
    "in case": "if", "carry out": "do", "carries out": "does", "set up": "prepare / install",
    "find out": "find", "turn on": "start", "turn off": "stop", "the following": "that follows",
    "according to": "write the source as the subject", "based on": "from",
}

LATIN = re.compile(r"\b(e\.g\.|i\.e\.|etc\.?|viz\.|cf\.|vs\.?)(?=\W|$)", re.I)
CONTRACTION = re.compile(r"\b\w+(n't|'re|'ve|'ll|'d|'m)\b|\b(it|that|there|here|what|who|let)'s\b", re.I)

# "-ing" words that are technical nouns, approved words or product labels here.
ING_ALLOWED = {
    "during", "thing", "things", "nothing", "something", "string", "strings",
    "rating", "ratings", "listing", "listings", "setting", "settings",
    "warning", "warnings", "missing", "meaning", "following", "writing",
    "pending", "opening", "king", "ring", "bring", "spring", "morning", "evening",
    "spelling", "engineering", "upcoming", "substring",
}

# Words that are not approved only in lower case. "Issue 9" is the name of a document.
LOWER_CASE_ONLY = {"issue", "issues"}

BE = r"(?:is|are|was|were|be|been|am)"
IRREGULAR_PARTICIPLES = (
    "built|broken|chosen|done|drawn|found|given|gone|held|hidden|kept|known|left|"
    "lost|made|put|read|run|seen|sent|set|shown|sorted|taken|told|written|stored"
)
PERFECT = re.compile(rf"\b(has|have|had)\s+(?:not\s+)?(\w+ed|been|{IRREGULAR_PARTICIPLES})\b", re.I)
PROGRESSIVE = re.compile(rf"\b{BE}\s+(?:not\s+)?(\w+ing)\b", re.I)
PASSIVE = re.compile(rf"\b{BE}\s+(?:not\s+|then\s+|also\s+|never\s+|always\s+)?(\w+ed|{IRREGULAR_PARTICIPLES})\b(?:\s+by\b)?", re.I)

BRITISH = {
    "colour": "color", "behaviour": "behavior", "centre": "center", "licence": "license",
    "organise": "organize", "favourite": "favorite", "favourites": "favorites",
    "neighbour": "neighbor", "catalogue": "catalog", "cancelled": "canceled",
    "authorise": "authorize", "analyse": "analyze", "grey": "gray",
}


@dataclass
class Block:
    kind: str      # paragraph | step | item | cell | heading
    line: int
    text: str


@dataclass
class Finding:
    path: Path
    line: int
    rule: str
    message: str
    note: bool = False

    def __str__(self) -> str:
        level = "note" if self.note else "error"
        return f"{self.path.relative_to(REPO)}:{self.line}: {level} [{self.rule}] {self.message}"


# ---------------------------------------------------------------- markdown

FENCE = re.compile(r"^\s*(```|~~~)")
ORDERED = re.compile(r"^\s*\d+[.)]\s+")
BULLET = re.compile(r"^\s*[-*+]\s+")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{2,}")
HTML_LINE = re.compile(r"^\s*</?(p|div|img|picture|source|table|tr|td|th|a|br|h\d|details|summary|sub|sup|video|b|kbd)\b", re.I)
# Legal text keeps its exact words. Put it between these two comment lines.
SKIP_OFF = re.compile(r"^\s*<!--\s*docs-check:\s*off\s*-->\s*$")
SKIP_ON = re.compile(r"^\s*<!--\s*docs-check:\s*on\s*-->\s*$")
ALERT = re.compile(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$")


def blocks_of(text: str) -> list[Block]:
    """Split a Markdown page into prose blocks. Code blocks and HTML are left out."""
    blocks: list[Block] = []
    current: Block | None = None
    in_fence = False

    def close():
        nonlocal current
        if current and current.text.strip():
            blocks.append(current)
        current = None

    skip = False
    for number, raw in enumerate(text.splitlines(), start=1):
        if FENCE.match(raw):
            in_fence = not in_fence
            close()
            continue
        if in_fence:
            continue
        if SKIP_OFF.match(raw) or SKIP_ON.match(raw):
            skip = bool(SKIP_OFF.match(raw))
            close()
            continue
        if skip:
            continue
        line = raw.rstrip()
        if line.lstrip().startswith(">"):
            line = re.sub(r"^\s*>\s?", "", line)
            if ALERT.match(line.strip()):
                close()
                continue
        if not line.strip() or line.strip() in ("---", "***"):
            close()
            continue
        if HTML_LINE.match(line) or line.strip().startswith("<!--"):
            close()
            continue
        heading = HEADING.match(line)
        if heading:
            close()
            blocks.append(Block("heading", number, heading.group(2)))
            continue
        if line.lstrip().startswith("|"):
            close()
            if TABLE_RULE.match(line):
                continue
            for cell in line.strip().strip("|").split("|"):
                if cell.strip():
                    blocks.append(Block("cell", number, cell.strip()))
            continue
        if ORDERED.match(line):
            close()
            current = Block("step", number, ORDERED.sub("", line))
            continue
        if BULLET.match(line):
            close()
            current = Block("item", number, BULLET.sub("", line))
            continue
        if current is None:
            current = Block("paragraph", number, line.strip())
        else:
            current.text += " " + line.strip()
    close()
    return blocks


def clean(text: str) -> str:
    """Remove Markdown markup. Code, quotes and parentheses each become one word."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)            # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)         # links -> text
    text = re.sub(r"`[^`]+`", " CODE ", text)                    # inline code
    text = re.sub(r"<[^>]+>", " ", text)                         # html tags
    text = re.sub(r"\*\*|__|(?<!\w)[*_]|[*_](?!\w)", "", text)   # emphasis marks
    text = re.sub(r"“[^”]*”|\"[^\"]*\"", " QUOTE ", text)        # quoted text
    for _ in range(2):
        text = re.sub(r"\([^()]*\)", " PAREN ", text)            # parentheses
    text = text.replace("&nbsp;", " ").replace("&amp;", "and")
    return re.sub(r"\s+", " ", text).strip()


def sentences_of(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?:])\s+(?=[A-Z0-9“\"(\[]|CODE|QUOTE|PAREN)", text)
    return [part.strip() for part in parts if part.strip()]


def words_of(sentence: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’./_%-]*", sentence)


# ------------------------------------------------------------------ checks

def check_prose(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []

    def add(line, rule, message, note=False):
        findings.append(Finding(path, line, rule, message, note))

    for block in blocks_of(text):
        raw = block.text
        if ";" in re.sub(r"`[^`]+`", "", raw):
            add(block.line, "punct", "semicolon (rule 8.1): make two sentences")
        if re.search(r"[—–]", re.sub(r"`[^`]+`", "", raw)):
            add(block.line, "punct", "dash: use a comma, a full stop or parentheses")
        cleaned = clean(raw)
        match = CONTRACTION.search(cleaned)
        if match:
            add(block.line, "punct", f"contraction '{match.group(0)}' (rule 4.2)")
        match = LATIN.search(cleaned)
        if match:
            add(block.line, "punct", f"Latin abbreviation '{match.group(0)}' (rule GR-6)")
        lowered = cleaned.lower()
        for phrase, better in NOT_APPROVED_PHRASES.items():
            if re.search(rf"\b{re.escape(phrase)}\b", lowered):
                add(block.line, "word", f"'{phrase}' -> {better}")
        sentences = sentences_of(cleaned)
        if block.kind == "paragraph" and len(sentences) > MAX_SENTENCES_PARAGRAPH:
            add(block.line, "length",
                f"paragraph has {len(sentences)} sentences (maximum {MAX_SENTENCES_PARAGRAPH})")
        limit = MAX_WORDS_PROCEDURE if block.kind == "step" else MAX_WORDS_DESCRIPTION
        for sentence in sentences:
            words = words_of(sentence)
            if block.kind != "heading" and len(words) > limit:
                add(block.line, "length",
                    f"sentence has {len(words)} words (maximum {limit}): '{sentence[:60]}...'")
            for word in words:
                token = word.lower().strip(".'’")
                if token in NOT_APPROVED and not (token in LOWER_CASE_ONLY and word[0].isupper()):
                    add(block.line, "word", f"'{word}' -> {NOT_APPROVED[token]}")
                elif token in BRITISH and not word[0].isupper():   # a product label keeps its spelling
                    add(block.line, "word", f"'{word}' -> {BRITISH[token]} (rule 1.14)")
                elif (token.endswith("ing") and len(token) > 4 and token not in ING_ALLOWED
                      and not word[0].isupper() and word not in ("CODE",)):
                    add(block.line, "verb", f"'-ing' form '{word}' (rule 3.5)")
            match = PERFECT.search(sentence)
            if match:
                add(block.line, "verb", f"perfect tense '{match.group(0)}' (rule 3.2)")
            match = PROGRESSIVE.search(sentence)
            if match and match.group(1).lower() not in ING_ALLOWED:
                add(block.line, "verb", f"progressive tense '{match.group(0)}' (rule 3.2)")
            match = PASSIVE.search(sentence)
            if match:
                add(block.line, "passive", f"'{match.group(0)}': use the active voice if the agent is known",
                    note=True)
    return findings


def slug(heading: str, seen: dict[str, int]) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text).replace(" ", "-")
    count = seen.get(text, 0)
    seen[text] = count + 1
    return text if count == 0 else f"{text}-{count}"


def anchors_of(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    anchors: set[str] = set()
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = HEADING.match(line)
        if heading:
            anchors.add(slug(heading.group(2), seen))
        anchors.update(re.findall(r'(?:id|name)="([^"]+)"', line))
    return anchors


def check_links(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        targets = re.findall(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", line)
        targets += re.findall(r'(?:src|href|srcset|poster)="([^"]+)"', line)
        for target in targets:
            if re.match(r"^(https?:|mailto:)", target):
                continue
            file_part, _, anchor = target.partition("#")
            destination = path if not file_part else (path.parent / file_part).resolve()
            if not destination.exists():
                findings.append(Finding(path, number, "link", f"missing file: {target}"))
                continue
            if anchor and destination.suffix == ".md" and anchor not in anchors_of(destination):
                findings.append(Finding(path, number, "link", f"missing anchor: {target}"))
    return findings


def main(argv: list[str]) -> int:
    patterns = argv or DEFAULT_PAGES
    pages: list[Path] = []
    for pattern in patterns:
        pages.extend(sorted(REPO.glob(pattern)))
    findings: list[Finding] = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        findings += check_prose(page, text)
        findings += check_links(page, text)
    errors = [finding for finding in findings if not finding.note]
    notes = [finding for finding in findings if finding.note]
    for finding in errors + notes:
        print(finding)
    print(f"\n{len(pages)} pages, {len(errors)} errors, {len(notes)} notes")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
