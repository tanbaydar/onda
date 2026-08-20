#!/usr/bin/env python3
"""Convert Onda DBML into deterministic Graphviz ER diagrams."""

from __future__ import annotations

import argparse
import html
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Column:
    name: str
    data_type: str
    attrs: str
    pk: bool = False
    fk: bool = False

    @property
    def nullable(self) -> bool:
        return "null" in self.attrs and "not null" not in self.attrs

    @property
    def unique(self) -> bool:
        return "unique" in self.attrs


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)


@dataclass
class Ref:
    child_table: str
    child_column: str
    parent_table: str
    parent_column: str


ZONE_COLORS = {
    "INGESTION": ("#e8f1fb", "#2f6690"),
    "CANONICAL_IDENTITY": ("#ecf6ed", "#3a7d44"),
    "APP": ("#fff0e5", "#b85c24"),
}


def parse_dbml(path: Path) -> tuple[dict[str, Table], list[Ref], dict[str, list[str]]]:
    text = path.read_text()
    tables: dict[str, Table] = {}
    groups: dict[str, list[str]] = {}
    for match in re.finditer(r"^Table\s+(\w+)\s*\{(.*?)^\}", text, re.M | re.S):
        name, body = match.group(1), match.group(2)
        table = Table(name)
        in_note = in_indexes = False
        composite_pks: set[str] = set()
        for raw in body.splitlines():
            line = raw.strip()
            if "'''" in line:
                in_note = not in_note
                continue
            if in_note or not line:
                continue
            if line == "indexes {":
                in_indexes = True
                continue
            if in_indexes:
                if line == "}":
                    in_indexes = False
                elif "[pk" in line:
                    cols = re.match(r"\(([^)]+)\)", line)
                    if cols:
                        composite_pks.update(x.strip() for x in cols.group(1).split(","))
                continue
            col = re.match(r"(\w+)\s+([^\s\[]+(?:\([^)]*\))?)\s*(?:\[(.*)\])?$", line)
            if col:
                attrs = col.group(3) or ""
                table.columns.append(Column(col.group(1), col.group(2), attrs, "pk" in attrs))
        for column in table.columns:
            column.pk = column.pk or column.name in composite_pks
        tables[name] = table
    refs = [Ref(*m.groups()) for m in re.finditer(
        r"^Ref:\s+(\w+)\.(\w+)\s+>\s+(\w+)\.(\w+)", text, re.M
    )]
    for table_name, body in re.findall(r"^Table\s+(\w+)\s*\{(.*?)^\}", text, re.M | re.S):
        for match in re.finditer(r"^\s*(\w+)\s+[^\n]*?\bref:\s*>\s*(\w+)\.(\w+)", body, re.M):
            refs.append(Ref(table_name, match.group(1), match.group(2), match.group(3)))
    for ref in refs:
        next(c for c in tables[ref.child_table].columns if c.name == ref.child_column).fk = True
    for match in re.finditer(r"^TableGroup\s+(\w+)\s*\{(.*?)^\}", text, re.M | re.S):
        groups[match.group(1)] = [x.strip() for x in match.group(2).splitlines() if x.strip()]
    return tables, refs, groups


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def displayed_columns(table: Table, mode: str) -> list[Column]:
    return [
        c for c in table.columns
        if mode == "full" or (mode == "pkfk" and (c.pk or c.fk)) or (mode == "pk" and c.pk)
    ]


def label(table: Table, mode: str, *, stub: bool = False) -> str:
    join = sum(c.pk for c in table.columns) > 1
    header = "#17242a" if table.name == "ONDA_USER" else "#78909c" if stub or join else "#263238"
    size = ' POINT-SIZE="12"' if table.name == "ONDA_USER" else ""
    rows = [f'<TR><TD BGCOLOR="{header}" COLSPAN="5"><FONT COLOR="white"{size}><B>{table.name}</B></FONT></TD></TR>']
    columns = displayed_columns(table, mode)
    for c in columns:
        tags = " ".join(x for x, yes in (("PK", c.pk), ("FK", c.fk)) if yes) or "&#160;"
        rows.append(
            f'<TR><TD BGCOLOR="#ffffff" PORT="{esc(c.name)}_l" WIDTH="28">&#160;</TD>'
            f'<TD BGCOLOR="#ffffff" ALIGN="LEFT"><B>{tags}</B></TD>'
            f'<TD BGCOLOR="#ffffff" ALIGN="LEFT">{esc(c.name)}</TD>'
            f'<TD BGCOLOR="#ffffff" ALIGN="LEFT"><FONT COLOR="#546e7a">{esc(c.data_type)}</FONT></TD>'
            f'<TD BGCOLOR="#ffffff" PORT="{esc(c.name)}_r" WIDTH="28">&#160;</TD></TR>'
        )
    return '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5">' + "".join(rows) + "</TABLE>>"


def write_dot(path: Path, tables: dict[str, Table], refs: list[Ref], groups: dict[str, list[str]], zones: list[str], mode: str, boundary: set[str]) -> None:
    native = {name for zone in zones for name in groups[zone]}
    selected = native | boundary
    selected_refs = [
        ref for ref in refs
        if ref.child_table in selected and ref.parent_table in selected
        and not (ref.child_table in boundary and ref.parent_table in boundary)
    ]
    incoming: dict[str, list[Ref]] = {name: [] for name in selected}
    for ref in selected_refs:
        incoming[ref.parent_table].append(ref)
    lines = [
        "digraph ERD {",
        '  graph [rankdir=LR, splines=ortho, overlap=false, outputorder=edgesfirst, bgcolor="white", pad="0.12", nodesep="0.32", ranksep="0.72", fontname="Helvetica", newrank=true];',
        '  node [shape=plain, fontname="Helvetica", fontsize=10];',
        '  edge [dir=both, color="#607d8b", penwidth=1.2, arrowsize=0.75];',
    ]
    for zone in zones:
        fill, stroke = ZONE_COLORS[zone]
        title = "CANONICAL + IDENTITY" if zone == "CANONICAL_IDENTITY" else zone
        lines.extend([f"  subgraph cluster_{zone.lower()} {{", f'    label="{title}"; color="{stroke}"; bgcolor="{fill}"; penwidth=1.5; margin=12;'])
        for name in groups[zone]:
            lines.append(f"    {name} [label={label(tables[name], mode)}];")
        if zone == "APP":
            columns = [
                ["REVIEW_LIKE", "NOTIFICATION", "REPORT"],
                ["REVIEW", "DIARY_ENTRY", "FOLLOW"],
                ["USERNAME_HOLD", "RECENT_SEARCH", "ONDA_USER", "ACCOUNT_CODE"],
                ["WILL_BE_THERE", "FAVORITE_EVENT", "FAVORITE_ARTIST", "FAVORITE_VENUE"],
            ]
            for column in columns:
                lines.append("    { rank=same; " + "; ".join(column) + "; }")
                lines.append("    " + " -> ".join(column) + ' [style=invis, weight=20];')
            lines.append('    REVIEW_LIKE -> REVIEW -> ONDA_USER -> WILL_BE_THERE [style=invis, weight=80, minlen=1];')
        lines.append("  }")
    if boundary:
        for name in sorted(boundary):
            lines.append(f"  {name} [label={label(tables[name], 'pk', stub=True)}];")
        if zones == ["CANONICAL_IDENTITY"]:
            lines.append('  FAVORITE_ARTIST -> FAVORITE_VENUE -> ONDA_USER [style=invis, weight=12];')
            lines.append('  FAVORITE_EVENT -> WILL_BE_THERE -> DIARY_ENTRY [style=invis, weight=12];')
    for ref in refs:
        if ref.child_table not in selected or ref.parent_table not in selected:
            continue
        if ref.child_table in boundary and ref.parent_table in boundary:
            continue
        child = next(c for c in tables[ref.child_table].columns if c.name == ref.child_column)
        tail = "odottee" if child.unique else "crowodot"
        head = "odottee" if child.nullable else "tee"
        child_endpoint = (
            f"{ref.child_table}:e" if ref.child_table in boundary
            else f"{ref.child_table}:{ref.child_column}_r:e"
        )
        incoming_index = incoming[ref.parent_table].index(ref)
        incoming_side = "l" if incoming_index % 2 == 0 else "r"
        incoming_compass = "w" if incoming_side == "l" else "e"
        parent_mode = "pk" if ref.parent_table in boundary else mode
        parent_columns = displayed_columns(tables[ref.parent_table], parent_mode)
        parent_column = parent_columns[(incoming_index // 2) % len(parent_columns)].name
        parent_endpoint = (
            f"{ref.parent_table}:{parent_column}_{incoming_side}:{incoming_compass}"
        )
        boundary_edge = ref.child_table in boundary or ref.parent_table in boundary
        content_edge = ref.parent_table in {"DIARY_ENTRY", "REVIEW"}
        color = "#7c9273" if boundary_edge else "#8a6f47" if content_edge else "#57758d"
        style = ", style=dashed" if boundary_edge else ""
        lines.append(
            f'  {child_endpoint} -> {parent_endpoint} '
            f'[arrowtail="{tail}", arrowhead="{head}", color="{color}"{style}, tooltip="{ref.child_table}.{ref.child_column} -> {ref.parent_table}.{ref.parent_column}"];'
        )
    lines.append("}")
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dbml", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    tables, refs, groups = parse_dbml(args.dbml)
    canonical = set(groups["CANONICAL_IDENTITY"])
    app = set(groups["APP"])
    app_boundary = {r.parent_table for r in refs if r.child_table in app and r.parent_table in canonical}
    canonical_boundary = {r.child_table for r in refs if r.child_table in app and r.parent_table in canonical}
    specs = [
        ("onda-erd-ingestion", ["INGESTION"], "full", set()),
        ("onda-erd-canonical-identity", ["CANONICAL_IDENTITY"], "full", canonical_boundary),
        ("onda-erd-app", ["APP"], "full", app_boundary),
        ("onda-erd-overview", ["INGESTION", "CANONICAL_IDENTITY", "APP"], "pkfk", set()),
    ]
    for name, zones, mode, boundary in specs:
        source, target = args.output / f"{name}.dot", args.output / f"{name}.svg"
        write_dot(source, tables, refs, groups, zones, mode, boundary)
        subprocess.run(["dot", "-Tsvg", str(source), "-o", str(target)], check=True)
        width = "2000" if name == "onda-erd-overview" else "1200"
        subprocess.run(["rsvg-convert", "-w", width, str(target), "-o", str(args.output / f"{name}.png")], check=True)
        selected = {table for zone in zones for table in groups[zone]} | boundary
        expected_edges = sum(
            ref.child_table in selected and ref.parent_table in selected
            and not (ref.child_table in boundary and ref.parent_table in boundary)
            for ref in refs
        )
        svg = target.read_text()
        actual_edges = svg.count('class="edge"')
        actual_nodes = svg.count('class="node"')
        if actual_edges != expected_edges or actual_nodes != len(selected):
            raise RuntimeError(
                f"{name}: expected {len(selected)} nodes/{expected_edges} edges, "
                f"rendered {actual_nodes} nodes/{actual_edges} edges"
            )
    zone_edges = []
    for _, zones, _, boundary in specs[:3]:
        selected = {table for zone in zones for table in groups[zone]} | boundary
        zone_edges.append(sum(
            r.child_table in selected and r.parent_table in selected
            and not (r.child_table in boundary and r.parent_table in boundary)
            for r in refs
        ))
    boundary_refs = sum(r.child_table in app and r.parent_table in canonical for r in refs)
    if sum(zone_edges) - boundary_refs != len(refs):
        raise RuntimeError(
            f"zone edge coverage mismatch: {zone_edges} - {boundary_refs} != {len(refs)}"
        )
    print(
        f"Rendered {len(specs)} diagrams from {len(tables)} tables and {len(refs)} references; "
        f"zone edge coverage {zone_edges} - {boundary_refs} duplicated boundaries = {len(refs)}."
    )


if __name__ == "__main__":
    main()
