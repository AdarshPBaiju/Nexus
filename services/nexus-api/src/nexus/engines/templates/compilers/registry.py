"""
nexus.engines.templates.compilers.registry - 13-Target Output Compiler Registry.
"""

from __future__ import annotations

from nexus.engines.templates.compilers.base import BaseTargetCompiler
from nexus.engines.templates.compilers.channel_compilers import (
    BotBlockCompiler,
    InAppBlockCompiler,
    MjmlEmailCompiler,
    PushJsonCompiler,
    SmsPlainCompiler,
    VoiceSsmlCompiler,
    WhatsAppHsmCompiler,
)
from nexus.engines.templates.compilers.document_compilers import (
    A4PdfCompiler,
    KitchenKotCompiler,
    MobilePassCompiler,
    ThermalEscPosCompiler,
    VerifiableWebCompiler,
    ZplLabelCompiler,
)


class TemplateCompilerRegistry:
    """
    Central registry providing access to all 13 canonical template target compilers.
    """

    _compilers: dict[str, BaseTargetCompiler] = {}

    @classmethod
    def _initialize_defaults(cls) -> None:
        if cls._compilers:
            return
        all_compilers = [
            # 7 Channels
            MjmlEmailCompiler(),
            WhatsAppHsmCompiler(),
            SmsPlainCompiler(),
            VoiceSsmlCompiler(),
            PushJsonCompiler(),
            BotBlockCompiler(),
            InAppBlockCompiler(),
            # 6 Documents & Peripherals
            A4PdfCompiler(),
            ThermalEscPosCompiler(),
            KitchenKotCompiler(),
            ZplLabelCompiler(),
            MobilePassCompiler(),
            VerifiableWebCompiler(),
        ]
        for comp in all_compilers:
            cls._compilers[comp.target_name] = comp

    @classmethod
    def get(cls, target: str) -> BaseTargetCompiler | None:
        cls._initialize_defaults()
        return cls._compilers.get(target.upper())

    @classmethod
    def all_targets(cls) -> list[str]:
        cls._initialize_defaults()
        return sorted(cls._compilers.keys())
