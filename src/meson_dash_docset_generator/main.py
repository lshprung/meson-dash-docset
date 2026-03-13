#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup, Tag
from importlib import resources
from pathlib import Path
import plistlib
import re
import shutil
import typing

from dash_docset_builder import (
        DB,
        DocsetSkeleton, 
        get_argparse_template, 
        get_title,
)

class Index:
    def __init__(self, db: DB, html_path: Path) -> None:
        self.db: DB = db
        self.html_path: Path = html_path

    def insert_index_terms(self, index_entry_class: str | None = None) -> int:
        count: int = 0
        soup: BeautifulSoup = BeautifulSoup(
                open(self.html_path), 'html.parser'
        )
        terms: list[Tag] = soup.find_all("a")
        for term in terms:
            self._insert_term(term)
            count += 1

        return count

    def _insert_term(self, term: Tag) -> None:
        name: str
        name = term.get_text()
        name = name.replace('"', '""')
        name = name.replace('\n', '')
        name = name.lstrip()
        name = re.sub(r'\s{3,}', ' ', name)

        if not term.has_key("href"):
            return

        page_path: Path = self.html_path.parent.joinpath(
                str(term['href'])
        ).resolve()
        # remove part of path leading up to actual interest
        for i in range(len(page_path.parts)):
            if page_path.parts[i:i+3] == (
                    "Contents", "Resources", "Documents"
            ):
                page_path = Path(*page_path.parts[i+3:])
                break

        # determine type
        type: str | None = None
        for i in (
                ("Type",     "elementary"),
                ("Function", "functions"),
                ("Builtin",  "builtin"),
                ("Object",   "returned")
        ):
            if f"Reference-manual_{i[1]}" in str(page_path):
                type = i[0]

        if not type is None:
            self.db.insert(name, type, str(page_path))

def insert_page(db: DB, html_path: Path) -> None:
    page_name: str = get_title(html_path)

    page_type: str = "Guide"

    if page_name:
        db.insert(page_name, page_type, str(html_path.name))

def main() -> None:
    parser: argparse.ArgumentParser = get_argparse_template()
    args: argparse.Namespace = parser.parse_args()
    index_path: str = "Reference-manual.html"
    index: Index
    count: int

    if not args.MANUAL_SOURCE.exists():
        print(f"Error: invalid MANUAL_SOURCE '{str(args.MANUAL_SOURCE)}'")
        exit(1)

    docset_skeleton: DocsetSkeleton = DocsetSkeleton(
            "Meson", args.builddir
    )
    # docset_skeleton will exit if it encounters issues, so no need to handle 
    # it here

    db: DB = DB(docset_skeleton.index_file)
    
    # copy files from manual source to builddir
    _ = shutil.copytree(
            args.MANUAL_SOURCE, 
            docset_skeleton.documents_dir, 
            dirs_exist_ok=True
        )

    # insert pages
    for html_path in docset_skeleton.documents_dir.glob("*.html"):
        insert_page(db, html_path)

    # insert terms
    index = Index(
            db, 
            Path(docset_skeleton.documents_dir, index_path)
    )
    count = index.insert_index_terms()
    if count == 0:
        # still couldn't find anything: warn the user
        print(f"Warning: couldn't find any index terms in '{index_path}'")

    # generate plist
    plist: dict[str, typing.Any] = {
            "CFBundleIdentifier": "meson",
            "CFBundleName": "Meson",
            "DocSetPlatformFamily": "meson",
            "isDashDocset": True,
    }
    with open(docset_skeleton.info_plist_file, mode='wb') as f:
        plistlib.dump(plist, f)

    # add icon
    with resources.path(
            "meson_dash_docset_generator",
            Path("resources", "icon.png")
    ) as fspath:
        _ = shutil.copy2(fspath, docset_skeleton.icon_file)

if __name__ == '__main__':
    main()
