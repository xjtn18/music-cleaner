import json
import os
import re
import sys
from dataclasses import dataclass, field


GENERIC_REMIX_TAGS = {"Segue", "Mash", "Remix"}


@dataclass
class FilenameState:
    artist: str
    song: str
    main_tags: list[str] = field(default_factory=list)
    edit_kind: str | None = None
    edit_tone: str | None = None


def normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


def strip_outer_parens(text):
    text = text.strip()
    if text.startswith("(") and text.endswith(")"):
        return text[1:-1].strip()
    return text


def remove_noise_tokens(text):
    text = re.sub(r"\bClub\s+Killers\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bCK\b(?!\s+Cut\b)\s*", " ", text)
    return normalize_spaces(text)


def normalize_artist_names(text):
    replacements = [
        (r"\bAAP\s+Rocky\b", "A$AP Rocky"),
        (r"\bASAP\s+Rocky\b", "A$AP Rocky"),
        (r"\bTy\s+Dolla\s+Sign\b", "Ty Dolla $ign"),
        (r"\bToo\s+Short\b", "Too $hort"),
        (r"\bSchoolboy\s+Q\b", "ScHoolboy Q"),
        (r"\bJayZ\b", "Jay-Z"),
        (r"\bBiggie\s+Smalls\b", "The Notorious B.I.G."),
        (r"\bBiggie\b", "The Notorious B.I.G."),
        (r"\bDr\s+Dre\b", "Dr. Dre"),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return normalize_spaces(text)


def normalize_artist_segment(artist):
    artist = re.sub(r"\bfeat\.?\b", "ft", artist, flags=re.IGNORECASE)
    artist = re.sub(r"\s*,\s*", " x ", artist)
    artist = re.sub(r"\s*&\s*", " x ", artist)
    artist = normalize_artist_names(artist)
    return normalize_spaces(artist)


def normalize_song_text(song):
    song = re.sub(r"\bvs\.\b", "vs", song, flags=re.IGNORECASE)
    song = re.sub(r"\bvs\.?(?=\s)", "vs", song, flags=re.IGNORECASE)
    song = normalize_artist_names(song)
    return normalize_spaces(song)


def split_filename(filename):
    if " - " not in filename:
        cleaned = normalize_artist_names(normalize_spaces(filename))
        return FilenameState(artist=cleaned, song="")

    artist, rest = filename.split(" - ", 1)
    artist = normalize_artist_segment(artist)

    chunk_matches = list(re.finditer(r"\([^()]*\)", rest))
    chunks = []
    loose_parts = []

    if chunk_matches:
        song = rest[:chunk_matches[0].start()].strip()
        cursor = chunk_matches[0].start()
        for match in chunk_matches:
            loose_parts.append(rest[cursor:match.start()])
            chunks.append(match.group(0)[1:-1].strip())
            cursor = match.end()
        loose_parts.append(rest[cursor:])
    else:
        song = rest.strip()

    return FilenameState(
        artist=artist,
        song=normalize_song_text(song),
        main_tags=chunks + ([normalize_spaces(" ".join(loose_parts))] if chunk_matches else []),
    )


def remove_kbpm_from_text(text):
    text = re.sub(r"\b\d{1,2}[AB]\b\s+\d{2,3}\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d{1,2}[AB]\b", " ", text, flags=re.IGNORECASE)
    return normalize_spaces(text)


def add_main_tag(state, text):
    text = strip_outer_parens(normalize_spaces(text))
    if text:
        state.main_tags.append(text)


def set_edit(state, kind=None, tone=None):
    priority = {None: 0, "plain": 1, "quick_hit": 2, "intro": 3}
    if kind and priority[kind] >= priority[state.edit_kind]:
        state.edit_kind = kind
    if tone:
        state.edit_tone = tone


def parse_tone(text):
    lower = text.lower()
    if "clean" in lower:
        return "Clean"
    if "dirty" in lower:
        return "Dirty"
    return None


def apply_edit_from_text(state, text):
    lower = text.lower()
    tone = parse_tone(text)

    if re.search(r"\bintro\s*-?\s*(clean|dirty)\b", lower):
        set_edit(state, kind="intro", tone=tone)
        return True

    if re.search(r"\b(clean|dirty)\s+extended\b", lower):
        set_edit(state, kind="intro", tone=tone)
        return True

    if re.search(r"\b(clean|dirty)\s+(short\s+edit|ck\s+cut)\b", lower):
        set_edit(state, kind="quick_hit", tone=tone)
        return True

    if re.search(r"\bquick\s+hit\s+(clean|dirty)\b", lower):
        set_edit(state, kind="quick_hit", tone=tone)
        return True

    if re.search(r"\b(clean|dirty)\s+radio\s+edit\b", lower):
        set_edit(state, kind="plain", tone=tone)
        return True

    if re.fullmatch(r"(clean|dirty)", lower):
        set_edit(state, kind="plain", tone=tone)
        return True

    return False


def normalize_range_text(range_text):
    match = re.search(r"(\d{2,3})\s*-\s*(\d{2,3})", range_text)
    if not match:
        return None
    return f"{match.group(1)} - {match.group(2)} Transition"


def split_prefix_and_suffix(text, suffix_pattern):
    match = re.match(rf"^(.*?)(?:\s+)?{suffix_pattern}$", text, flags=re.IGNORECASE)
    if not match:
        return None, None
    prefix = normalize_spaces(match.group(1))
    return prefix, True


def extract_transition_tags(state, text):
    match = re.match(
        r"^(.*?)(\d{2,3}\s*-\s*\d{2,3})\s*(trans|transition)$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        prefix = normalize_spaces(match.group(1))
        transition = normalize_range_text(match.group(2))
        if prefix:
            add_main_tag(state, prefix)
        add_main_tag(state, transition)
        return True

    match = re.match(
        r"^(.*?)\b(trans|transition)\s+(\d{2,3}\s*-\s*\d{2,3})$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        prefix = normalize_spaces(match.group(1))
        transition = normalize_range_text(match.group(3))
        if prefix:
            add_main_tag(state, prefix)
        add_main_tag(state, transition)
        return True

    return False


def normalize_acapella_tag(state, text):
    lower = text.lower()

    both_pattern = r"\b(?:acapella|acap)\s+(?:intro|in)\s*(?:and|&)\s*(?:outro|out)\b"
    if re.search(both_pattern, lower):
        prefix = re.sub(both_pattern, "", text, flags=re.IGNORECASE)
        prefix = normalize_spaces(prefix)
        if prefix:
            add_main_tag(state, prefix)
        add_main_tag(state, "Acapella In & Out")
        return True

    for pattern, replacement in [
        (r"\b(?:acapella|acap)\s+intro\b", "Acapella In"),
        (r"\b(?:acapella|acap)\s+outro\b", "Acapella Out"),
        (r"\bacap\b", "Acapella"),
    ]:
        match = re.search(pattern, lower)
        if match:
            prefix = re.sub(pattern, "", text, flags=re.IGNORECASE)
            prefix = normalize_spaces(prefix)
            if prefix:
                add_main_tag(state, prefix)
            add_main_tag(state, replacement)
            return True

    return False


def normalize_special_intro_tag(state, text):
    for pattern, replacement in [
        (r"\bparty\s+starter\b", "Clapapella"),
        (r"\bclap\s+intro\b", "Clapapella"),
        (r"\bslam\s+(?:intro|in)\b", "Slam Edit"),
    ]:
        if re.search(pattern, text, flags=re.IGNORECASE):
            prefix = re.sub(pattern, "", text, flags=re.IGNORECASE)
            prefix = normalize_spaces(prefix)
            if prefix:
                add_main_tag(state, prefix)
            add_main_tag(state, replacement)
            return True

    match = re.match(r"^(.*?)\b(?:epic|hype|break)\s+intro$", text, flags=re.IGNORECASE)
    if match:
        prefix = normalize_spaces(match.group(1))
        if prefix:
            add_main_tag(state, prefix)
        return True

    return False


def normalize_quick_hitter_tag(state, text):
    match = re.match(r"^(.*?)\bquick\s+hitter\s+edit$", text, flags=re.IGNORECASE)
    if not match:
        return False

    prefix = normalize_spaces(match.group(1))
    if prefix:
        add_main_tag(state, prefix)
    set_edit(state, kind="quick_hit")
    return True


def normalize_jump_off_tag(state, text):
    match = re.match(r"^(.*?)\bjump\s+off\s+edit$", text, flags=re.IGNORECASE)
    if not match:
        return False

    prefix = normalize_spaces(match.group(1))
    if prefix:
        add_main_tag(state, prefix)
    add_main_tag(state, "Jump Off Edit")
    return True


def normalize_extended_mix_tag(state, text):
    if re.fullmatch(r"extended\s+mix", text, flags=re.IGNORECASE):
        add_main_tag(state, "Ext")
        return True
    return False


def normalize_generic_remix_tag(state, text):
    text = re.sub(r"\bsegway\b", "Segue", text, flags=re.IGNORECASE)
    text = re.sub(r"\bblend\b|\bmashup\b", "Mash", text, flags=re.IGNORECASE)
    text = normalize_spaces(text)

    if re.fullmatch(r"segue|mash|remix", text, flags=re.IGNORECASE):
        add_main_tag(state, text.title() if text.lower() != "remix" else "Remix")
        return True

    match = re.match(r"^(.*?)(?:\s+)(Segue|Mash)$", text, flags=re.IGNORECASE)
    if match:
        prefix = normalize_spaces(match.group(1))
        if prefix:
            add_main_tag(state, prefix)
        add_main_tag(state, match.group(2).title())
        return True

    add_main_tag(state, text)
    return True


def normalize_parenthetical_chunk(state, chunk):
    text = remove_noise_tokens(remove_kbpm_from_text(strip_outer_parens(chunk)))
    if not text:
        return

    text = re.sub(r"(\d)\s*-\s*(\d)", r"\1 - \2", text)

    if apply_edit_from_text(state, text):
        return
    if normalize_extended_mix_tag(state, text):
        return
    if extract_transition_tags(state, text):
        return
    if normalize_acapella_tag(state, text):
        return
    if normalize_special_intro_tag(state, text):
        return
    if normalize_quick_hitter_tag(state, text):
        return
    if normalize_jump_off_tag(state, text):
        return
    normalize_generic_remix_tag(state, text)


def consume_free_text(state, text):
    text = remove_kbpm_from_text(remove_noise_tokens(text))
    text = re.sub(r"\bvs\.?(?=\s)", "vs", text, flags=re.IGNORECASE)
    text = normalize_spaces(text)
    if not text:
        return

    if apply_edit_from_text(state, text):
        return

    transition = normalize_range_text(text)
    if transition and re.search(r"\b(trans|transition)\b", text, flags=re.IGNORECASE):
        add_main_tag(state, transition)
        return

    add_main_tag(state, text)


def derive_state(filename):
    parsed = split_filename(filename)
    state = FilenameState(artist=parsed.artist, song=parsed.song)

    tags = parsed.main_tags
    paren_count = len(re.findall(r"\([^()]*\)", filename.split(" - ", 1)[1] if " - " in filename else ""))
    paren_tags = tags[:paren_count]
    loose_text = tags[paren_count] if len(tags) > paren_count else ""

    if not paren_tags and not re.search(r"\([^()]*\)", filename):
        song_text, trailing_text = split_song_and_loose(parsed.song)
        state.song = song_text
        consume_free_text(state, trailing_text)
    else:
        for chunk in paren_tags:
            normalize_parenthetical_chunk(state, chunk)
        consume_free_text(state, loose_text)

    state.artist = normalize_artist_names(state.artist)
    state.song = normalize_song_text(state.song)
    return state


def split_song_and_loose(text):
    working = remove_kbpm_from_text(text)
    patterns = [
        r"\bintro\s*-?\s*(?:clean|dirty)\b",
        r"\b(?:clean|dirty)\s+extended\b",
        r"\b(?:clean|dirty)\s+short\s+edit\b",
        r"\b(?:clean|dirty)\s+radio\s+edit\b",
        r"\b(?:clean|dirty)\s+ck\s+cut\b",
        r"\bquick\s+hit\s+(?:clean|dirty)\b",
        r"\b(?:clean|dirty)\b",
    ]

    trailing_parts = []
    changed = True
    while changed:
        changed = False
        for pattern in patterns:
            match = re.search(rf"(.*?)(?:\s+)({pattern})$", working, flags=re.IGNORECASE)
            if match:
                working = normalize_spaces(match.group(1))
                trailing_parts.insert(0, match.group(2))
                changed = True
                break

    return normalize_song_text(working), normalize_spaces(" ".join(trailing_parts))


def apply_vs_rule(state):
    if not re.search(r"\bvs\b", f"{state.artist} {state.song}", flags=re.IGNORECASE):
        return

    new_tags = []
    for tag in state.main_tags:
        if tag in GENERIC_REMIX_TAGS:
            continue
        new_tags.append(tag)

    new_tags.append("Segue")
    state.main_tags = new_tags


def finalize_main_tags(state):
    seen = set()
    unique = []
    for tag in state.main_tags:
        cleaned = normalize_spaces(strip_outer_parens(tag))
        if not cleaned:
            continue
        if cleaned not in seen:
            seen.add(cleaned)
            unique.append(cleaned)
    state.main_tags = unique


def render_edit_tag(state):
    if not state.edit_tone:
        return ""
    if state.edit_kind == "intro":
        return f"Intro - {state.edit_tone}"
    if state.edit_kind == "quick_hit":
        return f"Quick Hit {state.edit_tone}"
    return state.edit_tone


def clean_filename(filename):
    state = derive_state(filename)
    apply_vs_rule(state)
    finalize_main_tags(state)

    parts = [state.artist]
    if state.song:
        parts[0] = f"{state.artist} - {state.song}"

    for tag in state.main_tags:
        parts.append(f"({tag})")

    edit_tag = render_edit_tag(state)
    if edit_tag:
        parts.append(f"({edit_tag})")

    cleaned = normalize_spaces(" ".join(parts))
    cleaned = cleaned.replace("(())", "")
    cleaned = re.sub(r"\(\s*\(", "(", cleaned)
    cleaned = re.sub(r"\)\s*\)", ")", cleaned)
    return cleaned.strip()


def process_directory(directory, dry_run=True):
    changes_made = 0
    for root, _, files in os.walk(directory):
        for filename in files:
            original_path = os.path.join(root, filename)
            cleaned = clean_filename(filename)
            if cleaned != filename:
                new_path = os.path.join(root, cleaned)
                mode = "[DRY RUN] " if dry_run else ""
                print(f"{mode}{filename} -> {cleaned}")
                if not dry_run:
                    os.rename(original_path, new_path)
                changes_made += 1
    return changes_made


def run_tests(test_file):
    passed = 0
    failed = 0
    failed_tests = []

    with open(test_file, "r") as f:
        tests = json.load(f)

    for test in tests:
        result = clean_filename(test["input"])
        if result == test["expected"]:
            passed += 1
        else:
            failed += 1
            failed_tests.append((test["name"], test["input"], test["expected"], result))

    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'=' * 50}")

    if failed_tests:
        print("\nFailed tests:")
        for name, input_name, expected, result in failed_tests:
            print(f"\n  Test: {name}")
            print(f"  Input:    {input_name}")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")

    return failed == 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t"):
        test_file = sys.argv[2] if len(sys.argv) > 2 else "tests.json"
        success = run_tests(test_file)
        sys.exit(0 if success else 1)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  py clean.py --test [file]     Run tests")
        print("  py clean.py <dir>             Dry run (preview changes)")
        print("  py clean.py <dir> --run      Actually rename files")
        sys.exit(1)

    target_dir = sys.argv[1]
    dry_run = "--run" not in sys.argv

    if dry_run:
        print("[DRY RUN] No changes will be made. Use --run to apply changes.")
        print()

    changes = process_directory(target_dir, dry_run=dry_run)

    if dry_run:
        print(f"\n{changes} files would be renamed. Run with --run to apply.")


if __name__ == "__main__":
    main()
