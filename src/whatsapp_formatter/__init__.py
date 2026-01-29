"""
WhatsApp Format Converter

A Python library to convert between WhatsApp, Markdown, and HTML formatting.

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
    WhatsAppToHTMLConverter,
    WhatsAppToMarkdownConverter,
)
from .rules import BaseRule, FormattingRule

__version__ = "1.1.0"
__all__ = [
    # Markdown <-> WhatsApp
    "convert_markdown_to_whatsapp",
    "convert_whatsapp_to_markdown",
    # HTML <-> WhatsApp
    "convert_html_to_whatsapp",
    "convert_whatsapp_to_html",
    # Converter classes
    "MarkdownToWhatsAppConverter",
    "HTMLToWhatsAppConverter",
    "WhatsAppToMarkdownConverter",
    "WhatsAppToHTMLConverter",
    # Base classes
    "BaseConverter",
    "BaseRule",
    "FormattingRule",
]

_markdown_converter: MarkdownToWhatsAppConverter | None = None
_html_converter: HTMLToWhatsAppConverter | None = None
_wa_to_markdown_converter: WhatsAppToMarkdownConverter | None = None
_wa_to_html_converter: WhatsAppToHTMLConverter | None = None


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


def _get_wa_to_markdown_converter() -> WhatsAppToMarkdownConverter:
    global _wa_to_markdown_converter
    if _wa_to_markdown_converter is None:
        _wa_to_markdown_converter = WhatsAppToMarkdownConverter()
    return _wa_to_markdown_converter


def _get_wa_to_html_converter() -> WhatsAppToHTMLConverter:
    global _wa_to_html_converter
    if _wa_to_html_converter is None:
        _wa_to_html_converter = WhatsAppToHTMLConverter()
    return _wa_to_html_converter


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


def convert_whatsapp_to_markdown(content: str) -> str:
    """
    Convert WhatsApp formatting to Markdown format.

    Conversions:
        - *bold* -> **bold**
        - _italic_ -> *italic*
        - ~strikethrough~ -> ~~strikethrough~~
        - `code` and ```code blocks``` are preserved

    Supports nested formatting:
        - *_bold and italic_* -> ***bold and italic***

    Args:
        content: The WhatsApp-formatted text to convert.

    Returns:
        Markdown-formatted text.

    Example:
        >>> convert_whatsapp_to_markdown("*Hello* _World_")
        '**Hello** *World*'
    """
    return _get_wa_to_markdown_converter().convert(content)


def convert_whatsapp_to_html(content: str) -> str:
    """
    Convert WhatsApp formatting to HTML format.

    Conversions:
        - *bold* -> <strong>bold</strong>
        - _italic_ -> <em>italic</em>
        - ~strikethrough~ -> <del>strikethrough</del>
        - `code` -> <code>code</code>
        - ```code block``` -> <pre><code>code block</code></pre>
        - newlines -> <br>

    Supports nested formatting:
        - *_bold and italic_* -> <strong><em>bold and italic</em></strong>

    Args:
        content: The WhatsApp-formatted text to convert.

    Returns:
        HTML-formatted text.

    Example:
        >>> convert_whatsapp_to_html("*Hello* _World_")
        '<strong>Hello</strong> <em>World</em>'
    """
    return _get_wa_to_html_converter().convert(content)
