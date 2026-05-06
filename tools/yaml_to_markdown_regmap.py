#!/usr/bin/env python3
"""Generate a readable Markdown register map from a YAML description.

YAML schema is intended to match `tools/yaml_to_verilog_regbank.py`.
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: PyYAML. Install with: pip install -r tools/requirements.txt"
    ) from exc

VALID_ACCESS = {"rw", "ro", "wo", "rw1c"}


@dataclass(frozen=True)
class FieldSpec:
    name: str
    bit_offset: int
    bit_width: int
    access: str
    description: str
    pulse: bool


@dataclass(frozen=True)
class RegisterSpec:
    name: str
    source: str
    offset: int
    width: int
    access: str
    reset: int
    description: str
    fields: list[FieldSpec]


def parse_int(value: Any, key: str) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    raise ValueError(f"{key} must be an integer or int-like string")


def load_yaml(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    fixed = raw.replace("\t", "  ")
    data = yaml.safe_load(fixed)
    if not isinstance(data, dict):
        raise ValueError("Top-level YAML must be a mapping")
    return data


def parse_registers(
    data: dict[str, Any],
) -> tuple[str, str, str, list[RegisterSpec], dict[str, Any] | None]:
    module_name = data.get("module")
    if not isinstance(module_name, str) or not module_name.strip():
        raise ValueError("Top-level 'module' is required and must be a string")

    bus_name = data.get("bus", "wishbone")
    if not isinstance(bus_name, str):
        raise ValueError("Top-level 'bus' must be a string")

    description = str(data.get("description", "")).strip()

    regs_raw = data.get("registers")
    if not isinstance(regs_raw, list) or not regs_raw:
        raise ValueError("Top-level 'registers' must be a non-empty list")

    seen_offsets: set[int] = set()
    out: list[RegisterSpec] = []

    for idx, rr in enumerate(regs_raw):
        if not isinstance(rr, dict):
            raise ValueError(f"registers[{idx}] must be a mapping")

        for key in ["name", "offset", "width", "access", "description", "reset"]:
            if key not in rr:
                raise ValueError(f"register '{rr.get('name', idx)}' missing required key: {key}")

        name = str(rr["name"]).strip()
        source = str(rr.get("source", "internal")).strip().lower()
        if source not in {"internal", "external"}:
            raise ValueError(
                f"register '{name}' has invalid source '{source}', expected internal|external"
            )

        offset = parse_int(rr["offset"], f"register {name}.offset")
        width = parse_int(rr["width"], f"register {name}.width")
        access = str(rr["access"]).strip().lower()
        reset = parse_int(rr["reset"], f"register {name}.reset")
        reg_desc = str(rr["description"]).strip()

        if access not in VALID_ACCESS:
            raise ValueError(f"register '{name}' has invalid access '{access}'")
        if width <= 0:
            raise ValueError(f"register '{name}' width must be > 0")
        if reset < 0 or reset >= (1 << width):
            raise ValueError(f"register '{name}' reset {reset:#x} does not fit width {width}")
        if offset in seen_offsets:
            raise ValueError(f"register '{name}' has duplicate offset {offset:#x}")
        seen_offsets.add(offset)

        fields_raw = rr.get("fields", [])
        fields: list[FieldSpec] = []
        covered: set[int] = set()

        if fields_raw:
            if not isinstance(fields_raw, list):
                raise ValueError(f"register '{name}' fields must be a list")
            for fidx, fr in enumerate(fields_raw):
                if not isinstance(fr, dict):
                    raise ValueError(f"register '{name}' field[{fidx}] must be a mapping")
                for key in ["name", "bit_offset", "bit_width", "access", "description"]:
                    if key not in fr:
                        raise ValueError(f"register '{name}' field missing key: {key}")

                fname = str(fr["name"]).strip()
                boff = parse_int(fr["bit_offset"], f"{name}.{fname}.bit_offset")
                bwd = parse_int(fr["bit_width"], f"{name}.{fname}.bit_width")
                facc = str(fr["access"]).strip().lower()
                fdesc = str(fr["description"]).strip()
                pulse = bool(fr.get("pulse", False))

                if facc not in VALID_ACCESS:
                    raise ValueError(f"field '{name}.{fname}' has invalid access '{facc}'")
                if bwd <= 0:
                    raise ValueError(f"field '{name}.{fname}' bit_width must be > 0")
                if boff < 0 or boff + bwd > width:
                    raise ValueError(f"field '{name}.{fname}' range exceeds register width")

                for bit in range(boff, boff + bwd):
                    if bit in covered:
                        raise ValueError(f"field '{name}.{fname}' overlaps another field")
                    covered.add(bit)

                fields.append(
                    FieldSpec(
                        name=fname,
                        bit_offset=boff,
                        bit_width=bwd,
                        access=facc,
                        description=fdesc,
                        pulse=pulse,
                    )
                )

        out.append(
            RegisterSpec(
                name=name,
                source=source,
                offset=offset,
                width=width,
                access=access,
                reset=reset,
                description=reg_desc,
                fields=fields,
            )
        )

    irq = data.get("irq")
    if irq is not None and not isinstance(irq, dict):
        raise ValueError("Top-level 'irq' must be a mapping")

    out.sort(key=lambda r: r.offset)
    return module_name, bus_name, description, out, irq


def fmt_hex(value: int, min_nibbles: int = 1) -> str:
    if value < 0:
        return str(value)
    nibbles = max(min_nibbles, (value.bit_length() + 3) // 4)
    return f"0x{value:0{nibbles}X}"


def reg_reset_hex(reg: RegisterSpec) -> str:
    # nibble width based on register width
    nibbles = max(1, (reg.width + 3) // 4)
    return fmt_hex(reg.reset, min_nibbles=nibbles)


def field_bits(field: FieldSpec) -> str:
    msb = field.bit_offset + field.bit_width - 1
    lsb = field.bit_offset
    return f"{msb}:{lsb}" if msb != lsb else f"{lsb}"


def md_escape(text: str) -> str:
    # Minimal escaping for Markdown tables.
    return text.replace("|", "\\|").replace("\n", " ")


def emit_markdown(
    module_name: str,
    bus_name: str,
    description: str,
    regs: list[RegisterSpec],
    irq: dict[str, Any] | None,
    title: str | None,
) -> str:
    lines: list[str] = []
    doc_title = title.strip() if isinstance(title, str) and title.strip() else f"{module_name} Register Map"

    lines.append(f"# {md_escape(doc_title)}")
    lines.append("")
    if description:
        lines.append(md_escape(description))
        lines.append("")

    lines.append(f"- Module: `{module_name}`")
    lines.append(f"- Bus: `{bus_name}`")
    lines.append("")

    lines.append("## Registers")
    lines.append("")
    lines.append("| Name | Offset | Width | Access | Reset | Source | Description |")
    lines.append("|---|---:|---:|---|---|---|---|")
    for r in regs:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{md_escape(r.name)}`",
                    f"`{fmt_hex(r.offset, min_nibbles=2)}`",
                    str(r.width),
                    f"`{r.access}`",
                    f"`{reg_reset_hex(r)}`",
                    f"`{r.source}`",
                    md_escape(r.description),
                ]
            )
            + " |"
        )

    lines.append("")

    for r in regs:
        lines.append(f"## `{md_escape(r.name)}` (@ `{fmt_hex(r.offset, min_nibbles=2)}`)")
        lines.append("")
        if r.description:
            lines.append(md_escape(r.description))
            lines.append("")

        lines.append("| Property | Value |")
        lines.append("|---|---|")
        lines.append(f"| Offset | `{fmt_hex(r.offset, min_nibbles=2)}` |")
        lines.append(f"| Width | `{r.width}` |")
        lines.append(f"| Access | `{r.access}` |")
        lines.append(f"| Reset | `{reg_reset_hex(r)}` |")
        lines.append(f"| Source | `{r.source}` |")
        lines.append("")

        if r.fields:
            lines.append("### Fields")
            lines.append("")
            lines.append("| Bits | Name | Access | Pulse | Description |")
            lines.append("|---:|---|---|---|---|")
            for f in sorted(r.fields, key=lambda x: (x.bit_offset, x.bit_width)):
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            f"`{field_bits(f)}`",
                            f"`{md_escape(f.name)}`",
                            f"`{f.access}`",
                            "`true`" if f.pulse else "`false`",
                            md_escape(f.description),
                        ]
                    )
                    + " |"
                )
            lines.append("")
        else:
            lines.append("### Fields")
            lines.append("")
            lines.append("(No fields)")
            lines.append("")

    if irq:
        irq_name = str(irq.get("name", "irq")).strip() or "irq"
        irq_desc = str(irq.get("description", "Interrupt output")).strip()
        irq_cond = str(irq.get("condition", "")).strip()

        lines.append("## IRQ")
        lines.append("")
        if irq_desc:
            lines.append(md_escape(irq_desc))
            lines.append("")
        lines.append(f"- Name: `{md_escape(irq_name)}`")
        if irq_cond:
            lines.append("- Condition:")
            lines.append("")
            lines.append("```text")
            lines.append(irq_cond)
            lines.append("```")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown register map from YAML"
    )
    parser.add_argument("--yaml", required=True, help="Path to YAML register map")
    parser.add_argument("--out", required=True, help="Path to generated Markdown file")
    parser.add_argument(
        "--title",
        default=None,
        help="Optional document title (defaults to '<module> Register Map')",
    )
    args = parser.parse_args()

    yaml_path = Path(args.yaml)
    out_path = Path(args.out)

    data = load_yaml(yaml_path)
    module_name, bus_name, description, regs, irq = parse_registers(data)

    markdown = emit_markdown(module_name, bus_name, description, regs, irq, args.title)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"Generated {out_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
