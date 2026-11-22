#!/usr/bin/env python3
"""
verify_ui_design_system.py - Verification suite for Subphase 00.05 (Core UI Design System).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _verify_tokens(ui_dir: Path) -> None:
    tokens_file = ui_dir / "src" / "tokens" / "tokens.css"
    assert tokens_file.exists(), "tokens.css must exist"
    content = tokens_file.read_text(encoding="utf-8")
    for token in [
        "--nx-surface-bg",
        "--nx-surface-card",
        "--nx-action-primary",
        "--nx-action-text",
        "--nx-status-success-subtle",
        "--nx-status-success-text",
        '[data-theme="dark"]',
        '[data-theme="high-contrast-pos"]',
        ".nx-numeric",
    ]:
        assert token in content, f"Token {token} missing in tokens.css"
    print("  [PASS] Semantic design tokens and theme variants verified")


def _verify_surface_and_typography(ui_dir: Path) -> None:
    ctx_file = ui_dir / "src" / "theme" / "SurfaceContext.tsx"
    text_file = ui_dir / "src" / "typography" / "NexusText.tsx"
    assert ctx_file.exists() and text_file.exists(), "Context and Text must exist"
    assert "useSurface" in ctx_file.read_text(encoding="utf-8")
    text_content = text_file.read_text(encoding="utf-8")
    assert "primary-action" in text_content and "--nx-action-text" in text_content
    print("  [PASS] SurfaceContext and background-aware typography verified")


def _verify_primitives(ui_dir: Path) -> None:
    prims = [
        ui_dir / "src" / "surfaces" / "NexusCard.tsx",
        ui_dir / "src" / "surfaces" / "NexusBadge.tsx",
        ui_dir / "src" / "buttons" / "NexusButton.tsx",
        ui_dir / "src" / "surfaces" / "NexusBox.tsx",
        ui_dir / "src" / "surfaces" / "NexusStack.tsx",
        ui_dir / "src" / "surfaces" / "NexusDivider.tsx",
        ui_dir / "src" / "feedback" / "NexusTooltip.tsx",
        ui_dir / "src" / "icons" / "NexusIcon.tsx",
    ]
    for p in prims:
        assert p.exists(), f"Primitive {p.name} must exist"
    print(f"  [PASS] All {len(prims)} custom surface and button primitives verified")


def _verify_states_and_shells(ui_dir: Path) -> None:
    states = [
        "NexusLoadingSkeleton",
        "NexusEmptyState",
        "NexusFilteredEmptyState",
        "NexusErrorState",
        "NexusPermissionDeniedState",
    ]
    for s in states:
        f = ui_dir / "src" / "feedback" / "states" / f"{s}.tsx"
        assert f.exists(), f"State component {s} must exist"

    shells = [
        "NexusListingPageShell",
        "NexusDetailPageShell",
        "NexusFormPageShell",
        "NexusDashboardPageShell",
        "NexusSplitWorkspaceShell",
        "NexusOperationalCanvasShell",
        "NexusAuthAndGuardShell",
    ]
    for sh in shells:
        f = ui_dir / "src" / "layouts" / f"{sh}.tsx"
        assert f.exists(), f"Shell {sh} must exist"
    print("  [PASS] All 5 canonical states and 7 canonical page shells verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    ui_dir = repo_root / "packages" / "ui"
    print(f"==> Verifying Subphase 00.05 UI Design System in {ui_dir}...")

    _verify_tokens(ui_dir)
    _verify_surface_and_typography(ui_dir)
    _verify_primitives(ui_dir)
    _verify_states_and_shells(ui_dir)

    index_file = ui_dir / "src" / "index.ts"
    assert index_file.exists(), "index.ts must exist"
    assert len(index_file.read_text(encoding="utf-8").splitlines()) <= 30, (
        "Barrel must be <= 30 lines"
    )

    print("\n==> Subphase 00.05 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
