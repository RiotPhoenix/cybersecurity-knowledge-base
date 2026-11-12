"""Colour tokens and WCAG contrast for the RiotPhoenix stylesheet."""
import re

import pytest


def tokens(root) -> dict[str, str]:
    css = (root / "docs/assets/css/riotphoenix.css").read_text()
    block = re.search(r":root\s*\{(.*?)\}", css, re.S).group(1)
    return {k: v.lower() for k, v in re.findall(r"--(rp-[\w-]+):\s*(#[0-9a-fA-F]{6})", block)}


def luminance(hex_colour: str) -> float:
    rgb = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_palette_tokens_defined(root):
    t = tokens(root)
    expected = {"rp-bg": "#101114", "rp-surface": "#191b1f", "rp-surface-2": "#25282d",
                "rp-accent": "#b86b3b", "rp-link": "#d69a61", "rp-text": "#f1f1ef",
                "rp-muted": "#a0a4aa"}
    for k, v in expected.items():
        assert t.get(k) == v, f"--{k} should be {v}"


# Text colours used on each background in the stylesheet (WCAG AA body text >= 4.5:1).
TEXT_PAIRS = [(fg, bg) for fg in ("rp-text", "rp-muted", "rp-link", "rp-info", "rp-warn",
                                  "rp-danger")
              for bg in ("rp-bg", "rp-surface", "rp-surface-2")]


@pytest.mark.parametrize("fg,bg", TEXT_PAIRS)
def test_text_contrast_aa(root, fg, bg):
    t = tokens(root)
    assert contrast(t[fg], t[bg]) >= 4.5, f"--{fg} on --{bg}: {contrast(t[fg], t[bg]):.2f}:1"


def test_accent_non_text_contrast(root):
    t = tokens(root)  # WCAG 1.4.11 non-text contrast >= 3:1 for borders/indicators
    for bg in ("rp-bg", "rp-surface", "rp-surface-2"):
        assert contrast(t["rp-accent"], t[bg]) >= 3.0


def test_no_imagery_or_animation(root):
    css = (root / "docs/assets/css/riotphoenix.css").read_text()
    assert "url(" not in css, "stylesheet should not load external images or fonts"
    assert "@keyframes" not in css
    assert "prefers-reduced-motion" in css
