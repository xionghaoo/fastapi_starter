#!/usr/bin/env python3
import argparse
import fnmatch
import os
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


def parse_patterns(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    patterns: List[str] = []
    for v in values:
        if not v:
            continue
        # support comma-separated
        items = [x.strip() for x in v.split(",") if x.strip()]
        patterns.extend(items if items else [v])
    return patterns


def should_include(path: Path, include_patterns: List[str], exclude_patterns: List[str]) -> bool:
    rel = str(path)
    if include_patterns:
        in_any = any(fnmatch.fnmatch(rel, pat) for pat in include_patterns)
        if not in_any:
            return False
    if exclude_patterns:
        if any(fnmatch.fnmatch(rel, pat) for pat in exclude_patterns):
            return False
    return True


def iter_files(root: Path, include_patterns: List[str], exclude_patterns: List[str], exts: List[str]) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        # skip hidden dirs by default
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if filename.startswith("."):
                continue
            file_path = Path(dirpath) / filename
            if exts and file_path.suffix not in exts:
                continue
            if should_include(file_path.relative_to(root), include_patterns, exclude_patterns):
                yield file_path


def replace_in_file(path: Path, pairs: List[Tuple[str, str]], dry_run: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    content = original
    for frm, to in pairs:
        content = content.replace(frm, to)
    if content != original:
        if not dry_run:
            path.write_text(content, encoding="utf-8")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Find files under a directory and perform text replacements.")
    parser.add_argument("--root", required=True, help="Root directory to search")
    parser.add_argument("--from", dest="from_values", action="append", required=True, help="Text to replace (can repeat, supports comma-separated)")
    parser.add_argument("--to", dest="to_values", action="append", required=True, help="Replacement text (can repeat, supports comma-separated)")
    parser.add_argument("--include", dest="include_patterns", action="append", help="Include glob(s), relative to root (can repeat)")
    parser.add_argument("--exclude", dest="exclude_patterns", action="append", help="Exclude glob(s), relative to root (can repeat)")
    parser.add_argument("--ext", dest="extensions", action="append", help="File extensions to include, like .py,.toml (can repeat)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes, only report")

    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory does not exist: {root}")

    from_values = parse_patterns(args.from_values)
    to_values = parse_patterns(args.to_values)
    if len(from_values) != len(to_values):
        raise SystemExit(f"--from count ({len(from_values)}) must match --to count ({len(to_values)})")
    pairs: List[Tuple[str, str]] = list(zip(from_values, to_values))

    include_patterns = parse_patterns(args.include_patterns)
    exclude_patterns = parse_patterns(args.exclude_patterns)
    extensions = parse_patterns(args.extensions)
    if extensions:
        extensions = [e if e.startswith(".") else f".{e}" for e in extensions]

    changed_files: List[Path] = []
    for f in iter_files(root, include_patterns, exclude_patterns, extensions):
        if replace_in_file(f, pairs, args.dry_run):
            changed_files.append(f)

    if args.dry_run:
        print(f"[DRY RUN] {len(changed_files)} file(s) would be modified:")
    else:
        print(f"{len(changed_files)} file(s) modified:")
    for f in changed_files:
        print(f"- {f.relative_to(root)}")


if __name__ == "__main__":
    main()


