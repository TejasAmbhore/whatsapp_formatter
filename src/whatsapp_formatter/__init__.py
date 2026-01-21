"""
WhatsApp Format Converter

A Python library to convert Markdown and HTML to WhatsApp-compatible formatting.

WhatsApp Formatting Reference:
- Bold: *text*
- Italic: _text_
- Strikethrough: ~text~
- Monospace: `text`
- Code block: ```text```

See: https://faq.whatsapp.com/539178204879377/
"""

from __future__ import annotations

from .converter import (
    BaseConverter,
    HTMLToWhatsAppConverter,
    MarkdownToWhatsAppConverter,
)
from .rules import BaseRule, FormattingRule

__version__ = "1.0.0"
__all__ = [
    "convert_markdown_to_whatsapp",
    "convert_html_to_whatsapp",
    "MarkdownToWhatsAppConverter",
    "HTMLToWhatsAppConverter",
    "BaseConverter",
    "BaseRule",
    "FormattingRule",
]

_markdown_converter: MarkdownToWhatsAppConverter | None = None
_html_converter: HTMLToWhatsAppConverter | None = None


def _get_markdown_converter() -> MarkdownToWhatsAppConverter:
    global _markdown_converter
    if _markdown_converter is None:
        _markdown_converter = MarkdownToWhatsAppConverter()
    return _markdown_converter


def _get_html_converter() -> HTMLToWhatsAppConverter:
    global _html_converter
    if _html_converter is None:
        _html_converter = HTMLToWhatsAppConverter()
    return _html_converter


def convert_markdown_to_whatsapp(content: str) -> str:
    """
    Convert Markdown formatting to WhatsApp format.

    Conversions:
        - **bold** or __bold__ -> *bold*
        - *italic* -> _italic_
        - ~~strikethrough~~ -> ~strikethrough~
        - `code` and ```code blocks``` are preserved

    Args:
        content: The Markdown text to convert.

    Returns:
        WhatsApp-formatted text.

    Example:
        >>> convert_markdown_to_whatsapp("**Hello** *World*")
        '*Hello* _World_'
    """
    return _get_markdown_converter().convert(content)


def convert_html_to_whatsapp(content: str) -> str:
    """
    Convert HTML formatting to WhatsApp format.

    Conversions:
        - <b>, <strong> -> *bold*
        - <i>, <em> -> _italic_
        - <s>, <strike>, <del> -> ~strikethrough~
        - <code> -> `monospace`
        - Other HTML tags are stripped

    Args:
        content: The HTML text to convert.

    Returns:
        WhatsApp-formatted text.

    Example:
        >>> convert_html_to_whatsapp("<strong>Hello</strong> <em>World</em>")
        '*Hello* _World_'
    """
    return _get_html_converter().convert(content)
