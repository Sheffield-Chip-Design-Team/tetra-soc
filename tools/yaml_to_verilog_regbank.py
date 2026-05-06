#!/usr/bin/env python3
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: PyYAML. Install with: pip install -r tools/requirements.txt") from exc

VALID_ACCESS = {"rw", "ro", "wo", "rw1c"}


@dataclass
class PortDecl:
    direction: str
    net_type: str
    width: str
    name: str


@dataclass
class FieldSpec:
    name: str
    bit_offset: int
    bit_width: int
    access: str
    description: str
    pulse: bool


@dataclass
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


def ident(name: str) -> str:
    token = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip())
    token = re.sub(r"_+", "_", token)
    if not token:
        raise ValueError("Identifier cannot be empty")
    if token[0].isdigit():
        token = f"n_{token}"
    return token.lower()


def upper_ident(name: str) -> str:
    token = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip())
    token = re.sub(r"_+", "_", token)
    if not token:
        raise ValueError("Identifier cannot be empty")
    if token[0].isdigit():
        token = f"n_{token}"
    return token.upper()


def load_yaml(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    fixed = raw.replace("\t", "  ")
    data = yaml.safe_load(fixed)
    if not isinstance(data, dict):
        raise ValueError("Top-level YAML must be a mapping")
    return data

def parse_registers(data: dict[str, Any]) -> tuple[str, str, list[RegisterSpec], dict[str, Any] | None]:
    module_name = data.get("module")
    if not isinstance(module_name, str) or not module_name.strip():
        raise ValueError("Top-level 'module' is required and must be a string")

    bus_name = data.get("bus", "wishbone")
    if not isinstance(bus_name, str):
        raise ValueError("Top-level 'bus' must be a string")

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
            raise ValueError(f"register '{name}' has invalid source '{source}', expected internal|external")

        offset = parse_int(rr["offset"], f"register {name}.offset")
        width = parse_int(rr["width"], f"register {name}.width")
        access = str(rr["access"]).strip().lower()
        reset = parse_int(rr["reset"], f"register {name}.reset")
        description = str(rr["description"]).strip()

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
                description=description,
                fields=fields,
            )
        )

    irq = data.get("irq")
    if irq is not None and not isinstance(irq, dict):
        raise ValueError("Top-level 'irq' must be a mapping")

    return module_name, bus_name, out, irq


def reg_read_expr(reg: RegisterSpec) -> str:
    rid = upper_ident(reg.name)
    # whole-register naming: registers are prefixed with 'r_' and use ALL CAPS name
    if reg.source == "external":
        if reg.access in {"rw", "wo"}:
            return f"r_{rid}_rdata_i"
        return f"r_{rid}_i"
    # internal storage uses lowercase reg identifier (no r_ prefix)
    return f"{ident(reg.name)}_reg"


def convert_irq_condition(expr: str, regs: list[RegisterSpec]) -> str:
    # Build lookup structures for registers and fields. We'll perform
    # case-insensitive, token-normalized matching so that condition
    # expressions like 'IRQ_STATUS.byte_done' or 'irq_status.BYTE_DONE'
    # both match the YAML-defined register/field names.
    regs_by_norm: dict[str, RegisterSpec] = {}
    for r in regs:
        key = re.sub(r"[^A-Z0-9_]", "_", upper_ident(r.name)).upper()
        regs_by_norm[key] = r

    def normalize_token(tok: str) -> str:
        return re.sub(r"[^A-Z0-9_]", "_", tok).upper()

    # Replacement callback for regex matches of the form: IDENT or IDENT.IDENT
    ident_re = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)(?:\.([A-Za-z_][A-Za-z0-9_]*))?\b")

    def repl(m: re.Match) -> str:
        reg_tok = m.group(1)
        fld_tok = m.group(2)
        reg_norm = normalize_token(reg_tok)
        reg = regs_by_norm.get(reg_norm)
        if reg is None:
            # Not a register reference; leave as-is for later unresolved detection
            return m.group(0)

        reg_tok_ident = upper_ident(reg.name)
        reg_id = ident(reg.name)

        if fld_tok is None:
            # whole-register reference -> use standard read expr
            return reg_read_expr(reg)

        # field-level reference
        fld_norm = normalize_token(fld_tok)
        # Find matching field by normalized name
        match_field = None
        for f in reg.fields:
            if normalize_token(f.name) == fld_norm:
                match_field = f
                break
        if match_field is None:
            # Unknown field; leave as-is
            return m.group(0)

        fld = match_field
        fld_tok_lower = ident(fld.name)
        if reg.source == "external":
            return f"ext_f_{reg_tok_ident}_{fld_tok_lower}_i"
        else:
            return f"{reg_id}_{fld_tok_lower}_reg"

    out = ident_re.sub(lambda mo: repl(mo), expr)

    # Detect unresolved uppercase tokens (likely intended register/field refs)
    unresolved = re.findall(r"\b([A-Z_][A-Z0-9_]*(?:\.[A-Z_][A-Z0-9_]*)?)\b", out)
    # Filter out logical operators and known replacements
    unresolved = [u for u in unresolved if u.upper() not in {"AND", "OR", "NOT"}]
    if unresolved:
        raise ValueError(f"Unresolved symbols in irq.condition: {', '.join(sorted(set(unresolved)))}")

    out = out.replace(" and ", " && ").replace(" or ", " || ").replace(" not ", " !")
    return out


def format_ports(port_decls: list[PortDecl]) -> list[str]:
    if not port_decls:
        return []

    dir_w = max(len(p.direction) for p in port_decls)
    net_w = max(len(p.net_type) for p in port_decls)
    width_w = max(len(p.width) for p in port_decls)

    out: list[str] = []
    for p in port_decls:
        out.append(f"  {p.direction:<{dir_w}} {p.net_type:<{net_w}} {p.width:<{width_w}} {p.name}")
    return out


def section_block(title: str) -> list[str]:
    return [
        "  //------------------------------------------------------------",
        f"  // {title} ",
        "  //------------------------------------------------------------",
        "",
    ]


def fmt_decl_lines(
    decls: list[tuple[str, str, str]],
    *,
    kind_w: int | None = None,
    width_w: int | None = None,
) -> list[str]:
    """Format module-scope declarations.

    decls entries are (kind, width, name), e.g. ("reg", "[7:0]", "foo_reg").
    """
    if not decls:
        return []
    if kind_w is None:
        kind_w = max(len(k) for k, _, _ in decls)
    if width_w is None:
        width_w = max(len(w) for _, w, _ in decls)
    lines: list[str] = []
    for kind, width, name in decls:
        lines.append(f"  {kind:<{kind_w}} {width:<{width_w}} {name};".rstrip())
    return lines


def fmt_assign_lines(assigns: list[tuple[str, str]], align: bool = True) -> list[str]:
    if not assigns:
        return []
    lhs_w = max(len(lhs) for lhs, _ in assigns) if align else 0
    lines: list[str] = []
    for lhs, rhs in assigns:
        if align:
            lines.append(f"  assign {lhs:<{lhs_w}} = {rhs};")
        else:
            lines.append(f"  assign {lhs} = {rhs};")
    return lines


def emit_verilog(module_name: str, regs: list[RegisterSpec], irq: dict[str, Any] | None, addr_width: int, data_width: int) -> str:
    out_mod = f"{ident(module_name)}_regs"

    wb_ports: list[PortDecl] = [
        PortDecl("input", "wire", "", "clk"),
        PortDecl("input", "wire", "", "rst_n"),
        PortDecl("input", "wire", f"[{addr_width - 1}:0]", "wb_addr_i"),
        PortDecl("input", "wire", f"[{data_width - 1}:0]", "wb_wdata_i"),
        PortDecl("input", "wire", "", "wb_we_i"),
        PortDecl("input", "wire", "", "wb_stb_i"),
        PortDecl("output", "reg", f"[{data_width - 1}:0]", "wb_rdata_o"),
        PortDecl("output", "wire", "", "wb_ack_o"),
    ]

    irq_port: PortDecl | None = None

    rw1c_set_ports: list[PortDecl] = []
    rw1c_clear_ports: list[PortDecl] = []
    field_pulse_ports: list[PortDecl] = []
    reg_iface_ports: list[PortDecl] = []

    for reg in regs:
        reg_tok = upper_ident(reg.name)
        reg_id = ident(reg.name)

        # If register has fields, emit field-level signals instead of whole-register signals
        if reg.fields:
            for fld in reg.fields:
                fld_tok_upper = upper_ident(fld.name)
                fld_tok_lower = ident(fld.name)
                fid_upper = f"f_{reg_tok}_{fld_tok_upper}"
                # Internal register with fields: emit field-level ports
                if reg.source == "internal":
                    if fld.access in {"rw", "ro"}:
                        width = f"[{fld.bit_width - 1}:0]" if fld.bit_width > 1 else ""
                        # port name uses lowercase field token
                        port_name = f"f_{reg_tok}_{fld_tok_lower}_o"
                        reg_iface_ports.append(PortDecl("output", "wire", width, port_name))
                    if fld.access == "wo" and fld.pulse:
                        pulse_name = f"f_{reg_tok}_{fld_tok_lower}_pulse_o"
                        field_pulse_ports.append(PortDecl("output", "reg", "", pulse_name))
                    if fld.access == "rw1c":
                        set_name = f"f_{reg_tok}_{fld_tok_lower}_set_i"
                        rw1c_set_ports.append(PortDecl("input", "wire", "", set_name))
                else:
                    # External register with fields: emit field-level ports
                    if fld.access in {"rw", "ro"}:
                        width = f"[{fld.bit_width - 1}:0]" if fld.bit_width > 1 else ""
                        reg_iface_ports.append(PortDecl("input", "wire", width, f"ext_f_{reg_tok}_{fld_tok_lower}_i"))
                    if fld.access == "rw1c":
                        width = f"[{fld.bit_width - 1}:0]" if fld.bit_width > 1 else ""
                        reg_iface_ports.append(PortDecl("input", "wire", width, f"ext_f_{reg_tok}_{fld_tok_lower}_i"))
                        # external clear output port uses lowercase field token
                        rw1c_clear_ports.append(PortDecl("output", "reg", "", f"ext_f_{reg_tok}_{fld_tok_lower}_clr_o"))
                    if fld.access == "wo" and fld.pulse:
                        field_pulse_ports.append(PortDecl("output", "reg", "", f"ext_f_{reg_tok}_{fld_tok_lower}_pulse_o"))
        else:
            # Register without fields: use whole-register signals
            if reg.source == "external":
                if reg.access == "rw":
                    reg_iface_ports += [
                        PortDecl("input", "wire", f"[{reg.width - 1}:0]", f"r_{reg_tok}_rdata_i"),
                        PortDecl("output", "reg", f"[{reg.width - 1}:0]", f"r_{reg_tok}_wdata_o"),
                        PortDecl("output", "reg", "", f"r_{reg_tok}_we_o"),
                    ]
                else:
                    reg_iface_ports.append(PortDecl("input", "wire", f"[{reg.width - 1}:0]", f"r_{reg_tok}_i"))
            else:
                reg_iface_ports.append(PortDecl("output", "wire", f"[{reg.width - 1}:0]", f"r_{reg_tok}_o"))
    if irq:
        irq_name = ident(str(irq.get("name", "irq")))
        irq_port = PortDecl("output", "wire", "", f"{irq_name}_o")

    # -----------------------------
    # Module header + ports (grouped like the example output)
    # -----------------------------
    port_elems: list[tuple[str, PortDecl | str]] = []
    port_elems.append(("port", wb_ports[0]))
    port_elems.append(("port", wb_ports[1]))
    port_elems.append(("raw", ""))
    port_elems.append(("raw", "  // Wishbone interface"))
    for p in wb_ports[2:]:
        port_elems.append(("port", p))
    if irq_port:
        port_elems.append(("port", irq_port))
    port_elems.append(("raw", ""))
    port_elems.append(("raw", "  // Register bank interface"))
    for p in reg_iface_ports:
        port_elems.append(("port", p))
    for p in field_pulse_ports:
        port_elems.append(("port", p))
    for p in rw1c_set_ports:
        port_elems.append(("port", p))
    for p in rw1c_clear_ports:
        port_elems.append(("port", p))

    only_ports = [x for k, x in port_elems if k == "port"]
    assert all(isinstance(p, PortDecl) for p in only_ports)
    only_ports = [p for p in only_ports if isinstance(p, PortDecl)]
    dir_w = max(len(p.direction) for p in only_ports)
    net_w = max(len(p.net_type) for p in only_ports)
    width_w = max(len(p.width) for p in only_ports)

    def render_port(p: PortDecl) -> str:
        return f"  {p.direction:<{dir_w}} {p.net_type:<{net_w}} {p.width:<{width_w}} {p.name}".rstrip()

    # Render ports but keep the Wishbone/clk/rst section as-is.
    # Find the index of the '  // register bank interface' raw marker so we can
    # emit the preceding ports in their original order, then emit the register
    # bank ports with inputs first and outputs last.
    rendered_ports: list[str] = []
    total_ports = len(only_ports)

    # locate split point
    split_idx = None
    for i, (kind, payload) in enumerate(port_elems):
        if kind == "raw" and str(payload).strip().lower() == "// register bank interface":
            split_idx = i
            break

    # fallback: if not found, render all ports in original order
    if split_idx is None:
        port_count = total_ports
        port_idx = 0
        for kind, payload in port_elems:
            if kind == "raw":
                rendered_ports.append(str(payload))
                continue
            assert isinstance(payload, PortDecl)
            port_idx += 1
            comma = "," if port_idx < port_count else ""
            rendered_ports.append(f"{render_port(payload)}{comma}")
    else:
        # Render everything up to and including the split raw header
        rendered_ports_count = 0
        port_idx = 0
        for kind, payload in port_elems[: split_idx + 1]:
            if kind == "raw":
                rendered_ports.append(str(payload))
                continue
            assert isinstance(payload, PortDecl)
            port_idx += 1
            rendered_ports_count += 1
            comma = "," if rendered_ports_count < total_ports else ""
            rendered_ports.append(f"{render_port(payload)}{comma}")

        # Collect the remaining port declarations (the register-bank interface)
        reg_ports: list[PortDecl] = [p for k, p in port_elems[split_idx + 1 :] if k == "port" and isinstance(p, PortDecl)]

        # Split into inputs then outputs, preserve relative order
        reg_inputs = [p for p in reg_ports if p.direction.startswith("input")]
        reg_outputs = [p for p in reg_ports if p.direction.startswith("output")]

        # Render inputs first
        for p in reg_inputs:
            rendered_ports_count += 1
            comma = "," if rendered_ports_count < total_ports else ""
            rendered_ports.append(f"{render_port(p)}{comma}")

        # Render outputs next
        if reg_outputs:
            rendered_ports.append("")
            for p in reg_outputs:
                rendered_ports_count += 1
                comma = "," if rendered_ports_count < total_ports else ""
                rendered_ports.append(f"{render_port(p)}{comma}")

    lines: list[str] = []
    lines.append("// Auto-generated by tools/yaml_to_verilog_regbank.py")
    lines.append(f"module {out_mod} (")
    lines.extend(rendered_ports)
    lines.append(");")
    lines.append("")

    # -----------------------------
    # Address Map Paramaters
    # -----------------------------
    lines.extend(section_block("Address Map Paramaters"))
    name_w = max(len(f"ADDR_{upper_ident(r.name)}") for r in regs)
    for reg in regs:
        reg_tok = upper_ident(reg.name)
        pname = f"ADDR_{reg_tok}"
        lines.append(
            f"  localparam [{addr_width - 1}:0] {pname:<{name_w}} = {addr_width}'h{reg.offset:X};"
        )
    lines.append("")

    # -----------------------------
    # Internal Signals
    # -----------------------------
    lines.extend(section_block("Internal Signals"))
    decl_kind_w = max(3, 4)  # "reg" vs "wire"
    decl_width_w = 0
    for reg in regs:
        if reg.source == "internal":
            if reg.fields:
                for fld in reg.fields:
                    if fld.bit_width > 1:
                        decl_width_w = max(decl_width_w, len(f"[{fld.bit_width - 1}:0]"))
            else:
                decl_width_w = max(decl_width_w, len(f"[{reg.width - 1}:0]"))
    for reg in regs:
        reg_tok = upper_ident(reg.name)
        reg_id = ident(reg.name)
        lines.append(f"  // Register: {reg.name}")
        lines.append(f"  // Access: {reg.access.upper()}")
        lines.append(f"  // {reg.description}")
        decls: list[tuple[str, str, str]] = []
        if reg.source == "internal":
            if reg.fields:
                # Emit field-level storage registers (lowercase names, no f_/r_ prefixes)
                for fld in reg.fields:
                    fld_tok_upper = upper_ident(fld.name)
                    fld_tok_lower = ident(fld.name)
                    fid_storage = f"{reg_id}_{fld_tok_lower}"
                    width_str = f"[{fld.bit_width - 1}:0]" if fld.bit_width > 1 else ""
                    decls.append(("reg", width_str, f"{fid_storage}_reg"))
            else:
                # Emit whole-register storage
                decls.append(("reg", f"[{reg.width - 1}:0]", f"{reg_id}_reg"))
        decls.append(("wire", "", f"sel_{reg_id}"))
        lines.extend(fmt_decl_lines(decls, kind_w=decl_kind_w, width_w=decl_width_w))
        lines.append("")

    # -----------------------------
    # Address Decode Logic
    # -----------------------------
    lines.extend(section_block("Address Decode Logic"))
    assigns: list[tuple[str, str]] = []
    for reg in regs:
        reg_tok = upper_ident(reg.name)
        reg_id = ident(reg.name)
        assigns.append((f"sel_{reg_id}", f"(wb_addr_i == ADDR_{reg_tok})"))
        if reg.source == "internal":
            if reg.fields:
                # For internal registers with fields, assign each readable field output
                for fld in reg.fields:
                    fld_tok_upper = upper_ident(fld.name)
                    fld_tok_lower = ident(fld.name)
                    fid_storage = f"{reg_id}_{fld_tok_lower}"
                    port_name = f"f_{reg_tok}_{fld_tok_lower}_o"
                    # Only assign outputs for readable fields
                    if fld.access in {"rw", "ro", "rw1c"}:
                        assigns.append((port_name, f"{fid_storage}_reg"))
            else:
                # For internal registers without fields, assign whole register
                assigns.append((f"r_{reg_tok}_o", f"{reg_id}_reg"))
    lines.extend(fmt_assign_lines(assigns, align=True))
    lines.append("  assign wb_ack_o = wb_stb_i;")
    lines.append("")

    # -----------------------------
    # Read Logic
    # -----------------------------
    lines.extend(section_block("Read Logic"))
    lines.append("  always @* begin")
    lines.append(f"    wb_rdata_o = {data_width}'d0;")
    lines.append("    case (wb_addr_i)")
    case_label_w = max(len(f"ADDR_{upper_ident(r.name)}") for r in regs)
    for reg in regs:
        reg_tok = upper_ident(reg.name)
        reg_id = ident(reg.name)
        label = f"ADDR_{reg_tok}"

        if reg.fields:
            # Build read value of width reg.width from individual fields and external inputs,
            # filling unspecified bits with zeros.
            parts: list[str] = []
            # sort fields by bit_offset ascending so we can walk from MSB->LSB
            fields_sorted = sorted(reg.fields, key=lambda f: f.bit_offset)
            cursor = reg.width - 1
            # iterate from highest field to lowest
            for fld in reversed(fields_sorted):
                lo = fld.bit_offset
                hi = fld.bit_offset + fld.bit_width - 1
                # gap above this field
                if cursor > hi:
                    gap = cursor - hi
                    parts.append(f"{gap}'d0")
                # field expression
                fld_tok_upper = upper_ident(fld.name)
                fld_tok_lower = ident(fld.name)
                if reg.source == "external":
                    # external port uses lowercase field token
                    expr = f"ext_f_{reg_tok}_{fld_tok_lower}_i"
                else:
                    # internal storage uses lowercase reg_id and field token
                    expr = f"{reg_id}_{fld_tok_lower}_reg"
                # if field is multi-bit, use slice expression directly
                if fld.bit_width > 1:
                    parts.append(expr)
                else:
                    parts.append(expr)
                cursor = lo - 1
            # any remaining gap down to bit 0
            if cursor >= 0:
                parts.append(f"{cursor + 1}'d0")
            # parts built from MSB->LSB; join into concat
            if parts:
                rexpr = "{" + ", ".join(parts) + "}"
            else:
                rexpr = f"{reg.width}'d0"
        else:
            # Whole register read (existing behavior)
            rexpr = reg_read_expr(reg)
        
        if reg.width < data_width:
            pad = f"{{{{{data_width - reg.width}{{1'b0}}}}, {rexpr}}}"
            lines.append(f"      {label:<{case_label_w}}: wb_rdata_o = {pad};")
        elif reg.width == data_width:
            lines.append(f"      {label:<{case_label_w}}: wb_rdata_o = {rexpr};")
        else:
            lines.append(f"      {label:<{case_label_w}}: wb_rdata_o = {rexpr}[{data_width - 1}:0];")
    lines.append("      default: wb_rdata_o = '0;")
    lines.append("    endcase")
    lines.append("  end")
    lines.append("")

    # -----------------------------
    # Write Logic
    # -----------------------------
    lines.extend(section_block("Write Logic"))
    lines.append("  always @(posedge clk) begin")
    lines.append("    if (!rst_n) begin")

    # Reset logic
    for reg in regs:
        reg_tok = upper_ident(reg.name)
        reg_id = ident(reg.name)
        if reg.source == "internal":
            if reg.fields:
                # Initialize individual field registers based on their reset values
                for fld in reg.fields:
                    fld_tok_upper = upper_ident(fld.name)
                    fld_tok_lower = ident(fld.name)
                    fld_reset = (reg.reset >> fld.bit_offset) & ((1 << fld.bit_width) - 1)
                    lines.append(f"      {reg_id}_{fld_tok_lower}_reg <= {fld.bit_width}'h{fld_reset:X};")
            else:
                # Initialize whole register
                lines.append(f"      {reg_id}_reg <= {reg.width}'h{reg.reset:X};")

        # Reset pulse/clear outputs
        for fld in reg.fields:
            fld_tok_upper = upper_ident(fld.name)
            fld_tok_lower = ident(fld.name)
            fid_port_lower = f"f_{reg_tok}_{fld_tok_lower}"
            if reg.source == "internal":
                if fld.access == "wo" and fld.pulse:
                    # internal pulse output uses lowercase field token in port name
                    lines.append(f"      f_{reg_tok}_{fld_tok_lower}_pulse_o <= 1'b0;")
            else:
                # external outputs: pulses and rw1c clear outputs (use lowercase field token in port)
                if fld.access == "wo" and fld.pulse:
                    lines.append(f"      ext_{fid_port_lower}_pulse_o <= 1'b0;")
                if fld.access == "rw1c":
                    lines.append(f"      ext_f_{reg_tok}_{fld_tok_lower}_clr_o <= 1'b0;")

    lines.append("    end else begin")

    # Clear pulse outputs in non-reset state (only for internal registers with pulse fields)
    for reg in regs:
        reg_tok = upper_ident(reg.name)
        reg_id = ident(reg.name)
        for fld in reg.fields:
            fld_tok_upper = upper_ident(fld.name)
            fld_tok_lower = ident(fld.name)
            fid_port_lower = f"f_{reg_tok}_{fld_tok_lower}"
            if reg.source == "internal":
                if fld.access == "wo" and fld.pulse:
                    lines.append(f"      f_{reg_tok}_{fld_tok_lower}_pulse_o <= 1'b0;")
            else:
                if fld.access == "wo" and fld.pulse:
                    lines.append(f"      ext_{fid_port_lower}_pulse_o <= 1'b0;")
                if fld.access == "rw1c":
                    lines.append(f"      ext_f_{reg_tok}_{fld_tok_lower}_clr_o <= 1'b0;")

    lines.append("      if (wb_stb_i && wb_we_i) begin")

    # Write logic for each register (only for writable registers)
    for reg in regs:
        reg_tok = upper_ident(reg.name)
        reg_id = ident(reg.name)
        # Check if register is writable (internal or external)
        is_writable = False
        if reg.source == "internal":
            if reg.access == "rw":
                is_writable = True
            elif reg.fields:
                # Check if any field is writable
                for fld in reg.fields:
                    if fld.access in {"rw", "rw1c"} or (fld.access == "wo" and fld.pulse):
                        is_writable = True
                        break
        else:
            # external registers: writable if whole-register rw or any writable fields
            if reg.access == "rw":
                is_writable = True
            elif reg.fields:
                for fld in reg.fields:
                    if fld.access in {"rw", "rw1c"} or (fld.access == "wo" and fld.pulse):
                        is_writable = True
                        break
        
        # Only emit if statement for writable registers
        if is_writable:
            # use lowercase sel_<reg_id> for internal decoding
            lines.append(f"        if (sel_{reg_id}) begin")
            if reg.fields:
                # Write individual fields
                for fld in reg.fields:
                    fld_tok = upper_ident(fld.name)
                    fld_tok_lower = ident(fld.name)
                    fid_port_lower = f"f_{reg_tok}_{fld_tok_lower}"
                    lo = fld.bit_offset
                    hi = fld.bit_offset + fld.bit_width - 1
                    sl = f"[{hi}:{lo}]" if hi != lo else f"[{lo}]"
                    wd = f"wb_wdata_i{sl}"
                    if reg.source == "external":
                        # External fields: drives clear/pulse outputs back to external logic
                        if fld.access == "rw1c":
                            lines.append(f"          ext_f_{reg_tok}_{fld_tok_lower}_clr_o <= {wd};")
                        elif fld.access == "wo" and fld.pulse:
                            if fld.bit_width == 1:
                                lines.append(f"          ext_f_{reg_tok}_{fld_tok_lower}_pulse_o <= {wd};")
                            else:
                                lines.append(f"          ext_f_{reg_tok}_{fld_tok_lower}_pulse_o <= |{wd};")
                    else:
                        # Internal fields: update internal storage
                        if fld.access == "rw":
                            lines.append(f"          {reg_id}_{fld_tok_lower}_reg <= {wd};")
                        elif fld.access == "rw1c":
                            lines.append(f"          {reg_id}_{fld_tok_lower}_reg <= {reg_id}_{fld_tok_lower}_reg & ~{wd};")
                        elif fld.access == "wo" and fld.pulse:
                            if fld.bit_width == 1:
                                lines.append(f"          f_{reg_tok}_{fld_tok_lower}_pulse_o <= {wd};")
                            else:
                                lines.append(f"          f_{reg_tok}_{fld_tok_lower}_pulse_o <= |{wd};")
            else:
                # Write whole register
                if reg.access == "rw":
                    lines.append(f"          {reg_id}_reg <= wb_wdata_i[{reg.width - 1}:0];")
                elif reg.access == "rw1c":
                    lines.append(f"          {reg_id}_reg <= {reg_id}_reg & ~wb_wdata_i[{reg.width - 1}:0];")
            lines.append("        end")

    lines.append("      end")

    # Handle rw1c set signals (internal rw1c fields)
    for reg in regs:
            reg_tok = upper_ident(reg.name)
            reg_id = ident(reg.name)
            if reg.source != "internal":
                continue
            for fld in reg.fields:
                if fld.access == "rw1c":
                    fld_tok_upper = upper_ident(fld.name)
                    fld_tok_lower = ident(fld.name)
                    fid_port_lower = f"f_{reg_tok}_{fld_tok_lower}"
                    lines.append(f"      if ({fid_port_lower}_set_i) {reg_id}_{fld_tok_lower}_reg <= 1'b1;")

    lines.append("    end")
    lines.append("  end")

    # -----------------------------
    # IRQ Logic
    # -----------------------------
    if irq:
        irq_name = ident(str(irq.get("name", "irq")))
        cond = str(irq.get("condition", "1'b0"))
        cond_v = convert_irq_condition(cond, regs)
        lines.append("")
        lines.extend(section_block("IRQ Logic"))
        lines.append(f"  // {str(irq.get('description', 'Interrupt output'))}")
        lines.append(f"  assign {irq_name}_o = ({cond_v});")

    lines.append("")
    lines.append("endmodule")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Verilog register-bank module from YAML")
    parser.add_argument("--yaml", required=True, help="Path to YAML register map")
    parser.add_argument("--out", required=True, help="Path to generated Verilog file")
    parser.add_argument("--addr-width", type=int, default=8, help="Wishbone address width")
    parser.add_argument("--data-width", type=int, default=32, help="Wishbone data width")
    args = parser.parse_args()

    yaml_path = Path(args.yaml)
    out_path = Path(args.out)

    data = load_yaml(yaml_path)
    module_name, bus_name, regs, irq = parse_registers(data)
    if bus_name.lower() != "wishbone":
        raise ValueError(f"Unsupported bus '{bus_name}'. This script currently supports 'wishbone'.")

    verilog = emit_verilog(module_name, regs, irq, args.addr_width, args.data_width)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(verilog, encoding="utf-8")
    print(f"Generated {out_path}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
