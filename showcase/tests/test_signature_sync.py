"""Verify that every component's JinjaX header and Jinja2 macro declare the
same parameters with the same defaults.

The dual-mode pattern requires this invariant: when JinjaX renders the
component (driven by the ``{#def ... #}`` header) and when vanilla Jinja2
imports the macro (driven by the ``{% macro ... %}`` signature), both must
produce identical HTML for the same inputs. If the signatures drift, the
two render paths diverge silently — the test must fail loudly first.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

#: Header looks like:  {#def label, variant="primary", attrs={} #}
HEADER_RE = re.compile(r"\{#def\s+(.*?)#\}", re.DOTALL)

#: Macro signature looks like:  {% macro button(label, variant="primary") -%}
MACRO_RE = re.compile(r"\{%-?\s*macro\s+(\w+)\s*\((.*?)\)\s*-?%\}", re.DOTALL)


def _parse_param_list(raw: str) -> list[tuple[str, object]]:
    """Parse a Python-ish parameter list into ``[(name, default_repr), ...]``.

    Defaults are returned as their literal source string (e.g. ``'"primary"'``,
    ``'False'``, ``'{}'``). Required params have ``default = _MISSING``.
    """
    # Wrap as a fake function call so ``ast`` can parse the parameters.
    src = f"def _f({raw.strip().rstrip(',')}): pass"
    tree = ast.parse(src)
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)

    args = func.args.args
    defaults = func.args.defaults
    # Defaults align with the tail of args.
    n_required = len(args) - len(defaults)
    params: list[tuple[str, object]] = []
    for i, arg in enumerate(args):
        if i < n_required:
            params.append((arg.arg, _MISSING))
        else:
            default_node = defaults[i - n_required]
            params.append((arg.arg, ast.unparse(default_node)))
    return params


_MISSING = object()


def _parse_component(path: Path) -> tuple[str, list[tuple[str, object]], list[tuple[str, object]]]:
    """Return (macro_name, header_params, macro_params) for a component file."""
    src = path.read_text()
    header_match = HEADER_RE.search(src)
    macro_match = MACRO_RE.search(src)
    assert header_match, f"{path.name}: missing {{#def ... #}} header"
    assert macro_match, f"{path.name}: missing {{% macro ... %}} signature"

    header_params = _parse_param_list(header_match.group(1))
    macro_name = macro_match.group(1)
    macro_params = _parse_param_list(macro_match.group(2))
    return macro_name, header_params, macro_params


def test_every_component_has_header_and_macro(component_files):
    for path in component_files:
        _parse_component(path)


def test_header_and_macro_params_match(component_files):
    for path in component_files:
        _, header, macro = _parse_component(path)

        # Param names must match exactly, in order.
        header_names = [name for name, _ in header]
        macro_names = [name for name, _ in macro]
        assert header_names == macro_names, (
            f"{path.name}: param name mismatch\n"
            f"  header: {header_names}\n"
            f"  macro:  {macro_names}"
        )

        # Defaults must match (treating ``None`` and ``none`` as equivalent).
        for (name, h_default), (_, m_default) in zip(header, macro):
            h = "None" if h_default == "none" else h_default
            m = "None" if m_default == "none" else m_default
            assert h == m, (
                f"{path.name}: default mismatch on `{name}`\n"
                f"  header: {h}\n"
                f"  macro:  {m}"
            )


def test_shim_uses_first_required_arg(component_files):
    """The trailing shim must check the first required arg, not a kwarg.

    Pattern: ``{% if first_required is defined %}{{ name(...) }}{% endif %}``.
    """
    for path in component_files:
        macro_name, header, _ = _parse_component(path)
        # First required (no default) param.
        required = [name for name, default in header if default is _MISSING]
        first = required[0] if required else header[0][0]

        src = path.read_text()
        # Allow either {% if X is defined %} or its endpoint variant.
        pattern = re.compile(
            rf"\{{%-?\s*if\s+{first}\s+is\s+defined\s*-?%\}}"
        )
        assert pattern.search(src), (
            f"{path.name}: shim must guard with `{{% if {first} is defined %}}`"
        )
