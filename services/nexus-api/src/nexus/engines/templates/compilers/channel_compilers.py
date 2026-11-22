"""
nexus.engines.templates.compilers.channel_compilers - 7 Digital & Messaging Output Compilers.
"""
from __future__ import annotations

from typing import Any

from nexus.engines.templates.ast.nodes import ASTNode
from nexus.engines.templates.compilers.base import BaseTargetCompiler


class MjmlEmailCompiler(BaseTargetCompiler):
    """Target 1: Responsive Email Compiler emitting MJML intermediate representation."""

    @property
    def target_name(self) -> str:
        return "EMAIL_MJML"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> str:
        text = self.collect_text(root)
        return f"<mjml><mj-body><mj-section><mj-column><mj-text>{text}</mj-text></mj-column></mj-section></mj-body></mjml>"


class WhatsAppHsmCompiler(BaseTargetCompiler):
    """Target 2: Meta Cloud WhatsApp HSM Compiler."""

    @property
    def target_name(self) -> str:
        return "WHATSAPP_HSM"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.collect_text(root)
        meta = metadata or {}
        return {
            "type": "template",
            "template": {
                "name": meta.get("template_name", "order_update"),
                "language": {"code": meta.get("language", "en")},
                "components": [{"type": "body", "parameters": [{"type": "text", "text": text}]}],
            },
        }


class SmsPlainCompiler(BaseTargetCompiler):
    """Target 3: Plain text SMS Compiler stripped of tags."""

    @property
    def target_name(self) -> str:
        return "SMS_PLAIN"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> str:
        return self.collect_text(root).strip()


class VoiceSsmlCompiler(BaseTargetCompiler):
    """Target 4: SSML Voice / Telephony Compiler."""

    @property
    def target_name(self) -> str:
        return "VOICE_SSML"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> str:
        text = self.collect_text(root)
        return f'<speak><prosody rate="medium">{text}</prosody></speak>'


class PushJsonCompiler(BaseTargetCompiler):
    """Target 5: FCM / APNs Push JSON Payload Compiler."""

    @property
    def target_name(self) -> str:
        return "PUSH_JSON"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.collect_text(root)
        meta = metadata or {}
        return {
            "title": meta.get("title", "Notification"),
            "body": text,
            "data": meta.get("data", {}),
        }


class BotBlockCompiler(BaseTargetCompiler):
    """Target 6: Telegram / Discord / Slack Block Kit Compiler."""

    @property
    def target_name(self) -> str:
        return "BOT_BLOCKS"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.collect_text(root)
        return {
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            ]
        }


class InAppBlockCompiler(BaseTargetCompiler):
    """Target 7: In-App Notification Center Card Compiler."""

    @property
    def target_name(self) -> str:
        return "IN_APP_BLOCKS"

    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.collect_text(root)
        meta = metadata or {}
        return {
            "title": meta.get("title", "Notice"),
            "body": text,
            "category": meta.get("category", "SYSTEM"),
            "action_url": meta.get("action_url", ""),
        }
