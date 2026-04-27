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
    rid = ident(reg.name)
    if reg.source == "external":
        if reg.access in {"rw", "wo"}:
            return f"{rid}_rdata_i"
        return f"{rid}_i"
    return f"{rid}_reg"


def convert_irq_condition(expr: str, regs: list[RegisterSpec]) -> str:
    field_map: dict[str, str] = {}
    reg_map = {r.name.upper(): r for r in regs}
    for reg in regs:
        rname = reg.name.upper()
        rread = reg_read_expr(reg)
        field_map[rname] = rread
        for fld in reg.fields:
            key = f"{rname}.{fld.name.upper()}"
            if fld.bit_width == 1:
                field_map[key] = f"{rread}[{fld.bit_offset}]"
            else:
                msb = fld.bit_offset + fld.bit_width - 1
                field_map[key] = f"{rread}[{msb}:{fld.bit_offset}]"

    out = expr
    tokens = sorted(field_map.keys(), key=len, reverse=True)
    for token in tokens:
        out = re.sub(rf"\b{re.escape(token)}\b", field_map[token], out)

    unresolved = re.findall(r"\b[A-Z_][A-Z0-9_]*(?:\.[A-Z_][A-Z0-9_]*)?\b", out)
    unresolved = [u for u in unresolved if u not in {"AND", "OR", "NOT"} and u not in reg_map]
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


def emit_verilog(module_name: str, regs: list[RegisterSpec], irq: dict[str, Any] | None, addr_width: int, data_width: int) -> str:
    out_mod = f"{ident(module_name)}_regs"

    ports: list[PortDecl] = [
        PortDecl("input", "wire", "", "clk"),
        PortDecl("input", "wire", "", "rst_n"),
        PortDecl("input", "wire", f"[{addr_width - 1}:0]", "wb_addr_i"),
        PortDecl("input", "wire", f"[{data_width - 1}:0]", "wb_wdata_i"),
        PortDecl("input", "wire", "", "wb_we_i"),
        PortDecl("input", "wire", "", "wb_stb_i"),
        PortDecl("output", "reg", f"[{data_width - 1}:0]", "wb_rdata_o"),
        PortDecl("output", "wire", "", "wb_ack_o"),
    ]

    rw1c_set_ports: list[PortDecl] = []
    field_pulse_ports: list[PortDecl] = []
    reg_iface_ports: list[PortDecl] = []

    for reg in regs:
        rid = ident(reg.name)
        if reg.source == "external":
            if reg.access == "rw":
                reg_iface_ports += [
                    PortDecl("input", "wire", f"[{reg.width - 1}:0]", f"{rid}_rdata_i"),
                    PortDecl("output", "reg", f"[{reg.width - 1}:0]", f"{rid}_wdata_o"),
                    PortDecl("output", "reg", "", f"{rid}_we_o"),
                ]
            else:
                reg_iface_ports.append(PortDecl("input", "wire", f"[{reg.width - 1}:0]", f"{rid}_i"))
            continue

        reg_iface_ports.append(PortDecl("output", "wire", f"[{reg.width - 1}:0]", f"{rid}_o"))

        for fld in reg.fields:
            fid = f"{rid}_{ident(fld.name)}"
            if fld.access == "wo" and fld.pulse:
                field_pulse_ports.append(PortDecl("output", "reg", "", f"{fid}_pulse_o"))
            if fld.access == "rw1c":
                rw1c_set_ports.append(PortDecl("input", "wire", "", f"{fid}_set_i"))

    if irq:
        irq_name = ident(str(irq.get("name", "irq")))
        ports.append(PortDecl("output", "wire", "", f"{irq_name}_o"))

    ports.extend(reg_iface_ports)
    ports.extend(field_pulse_ports)
    ports.extend(rw1c_set_ports)

    lines: list[str] = []
    lines.append("// Auto-generated by tools/yaml_to_verilog_regbank.py")
    lines.append(f"module {out_mod} (")
    formatted_ports = format_ports(ports)
    for i, p in enumerate(formatted_ports):
        comma = "," if i < len(ports) - 1 else ""
        lines.append(f"{p}{comma}")
    lines.append(");")
    lines.append("")

    for reg in regs:
        rid = ident(reg.name)
        lines.append(f"  // {reg.description}")
        lines.append(f"  localparam [{addr_width - 1}:0] ADDR_{rid.upper()} = {addr_width}'h{reg.offset:0X};")
        lines.append(f"  wire sel_{rid} = (wb_addr_i == ADDR_{rid.upper()});")
        if reg.source == "internal":
            lines.append(f"  reg [{reg.width - 1}:0] {rid}_reg;")
            lines.append(f"  assign {rid}_o = {rid}_reg;")
        lines.append("")

    lines.append("  assign wb_ack_o = wb_stb_i;")
    lines.append("")

    lines.append("  always @* begin")
    lines.append(f"    wb_rdata_o = {data_width}'d0;")
    lines.append("    case (wb_addr_i)")
    for reg in regs:
        rid = ident(reg.name)
        rexpr = reg_read_expr(reg)
        if reg.width < data_width:
            lines.append(f"      ADDR_{rid.upper()}: wb_rdata_o = {{{{{data_width - reg.width}{{1'b0}}}}, {rexpr}}};")
        elif reg.width == data_width:
            lines.append(f"      ADDR_{rid.upper()}: wb_rdata_o = {rexpr};")
        else:
            lines.append(f"      ADDR_{rid.upper()}: wb_rdata_o = {rexpr}[{data_width - 1}:0];")
    lines.append("      default: wb_rdata_o = '0;")
    lines.append("    endcase")
    lines.append("  end")
    lines.append("")

    lines.append("  always @(posedge clk) begin")
    lines.append("    if (!rst_n) begin")

    for reg in regs:
        rid = ident(reg.name)
        if reg.source == "internal":
            lines.append(f"      {rid}_reg <= {reg.width}'h{reg.reset:X};")
        if reg.source == "external" and reg.access == "rw":
            lines.append(f"      {rid}_wdata_o <= {reg.width}'d0;")
            lines.append(f"      {rid}_we_o <= 1'b0;")
        for fld in reg.fields:
            fid = f"{rid}_{ident(fld.name)}"
            if fld.access == "wo" and fld.pulse:
                lines.append(f"      {fid}_pulse_o <= 1'b0;")

    lines.append("    end else begin")

    for reg in regs:
        rid = ident(reg.name)
        if reg.source == "external" and reg.access == "rw":
            lines.append(f"      {rid}_we_o <= 1'b0;")
        for fld in reg.fields:
            fid = f"{rid}_{ident(fld.name)}"
            if fld.access == "wo" and fld.pulse:
                lines.append(f"      {fid}_pulse_o <= 1'b0;")

    lines.append("      if (wb_stb_i && wb_we_i) begin")

    for reg in regs:
        rid = ident(reg.name)
        lines.append(f"        if (sel_{rid}) begin")
        if reg.source == "external":
            if reg.access == "rw":
                lines.append(f"          {rid}_wdata_o <= wb_wdata_i[{reg.width - 1}:0];")
                lines.append(f"          {rid}_we_o <= 1'b1;")
        else:
            if not reg.fields:
                if reg.access == "rw":
                    lines.append(f"          {rid}_reg <= wb_wdata_i[{reg.width - 1}:0];")
                elif reg.access == "rw1c":
                    lines.append(f"          {rid}_reg <= {rid}_reg & ~wb_wdata_i[{reg.width - 1}:0];")
            else:
                for fld in reg.fields:
                    fid = f"{rid}_{ident(fld.name)}"
                    lo = fld.bit_offset
                    hi = fld.bit_offset + fld.bit_width - 1
                    sl = f"[{hi}:{lo}]" if hi != lo else f"[{lo}]"
                    wd = f"wb_wdata_i{sl}"
                    if fld.access == "rw":
                        lines.append(f"          {rid}_reg{sl} <= {wd};")
                    elif fld.access == "rw1c":
                        lines.append(f"          {rid}_reg{sl} <= {rid}_reg{sl} & ~{wd};")
                    elif fld.access == "wo" and fld.pulse:
                        if fld.bit_width == 1:
                            lines.append(f"          {fid}_pulse_o <= {wd};")
                        else:
                            lines.append(f"          {fid}_pulse_o <= |{wd};")
        lines.append("        end")

    lines.append("      end")

    for reg in regs:
        rid = ident(reg.name)
        if reg.source != "internal":
            continue
        for fld in reg.fields:
            if fld.access == "rw1c":
                fid = f"{rid}_{ident(fld.name)}"
                lo = fld.bit_offset
                hi = fld.bit_offset + fld.bit_width - 1
                sl = f"[{hi}:{lo}]" if hi != lo else f"[{lo}]"
                lines.append(f"      if ({fid}_set_i) {rid}_reg{sl} <= {{{fld.bit_width}{{1'b1}}}};")

    lines.append("    end")
    lines.append("  end")

    if irq:
        irq_name = ident(str(irq.get("name", "irq")))
        cond = str(irq.get("condition", "1'b0"))
        cond_v = convert_irq_condition(cond, regs)
        lines.append("")
        lines.append(f"  // {str(irq.get('description', 'Interrupt output'))}")
        lines.append(f"  assign {irq_name}_o = ({cond_v});")

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
