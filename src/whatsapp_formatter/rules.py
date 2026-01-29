"""Formatting rules using the Strategy Pattern."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Protocol

BOLD_PLACEHOLDER = "\x00WA_BOLD\x00"
CODE_BLOCK_PLACEHOLDER = "\x00CODE_BLOCK_{}\x00"
INLINE_CODE_PLACEHOLDER = "\x00INLINE_CODE_{}\x00"

# Placeholders for WhatsApp to Markdown/HTML conversion
WA_BOLD_PLACEHOLDER = "\x00WA_BOLD_CONTENT\x00"
WA_ITALIC_PLACEHOLDER = "\x00WA_ITALIC_CONTENT\x00"
WA_STRIKE_PLACEHOLDER = "\x00WA_STRIKE_CONTENT\x00"


class FormattingRule(Protocol):
    """Protocol for formatting rules."""

    name: str
    priority: int

    def apply(self, content: str) -> str: ...


class BaseRule(ABC):
    """Abstract base class for formatting rules."""

    name: str = ""
    priority: int = 0

    @abstractmethod
    def apply(self, content: str) -> str:
        pass


class PreservableRule(BaseRule):
    """Base class for rules that preserve and restore content."""

    placeholder_template: str = ""

    def __init__(self) -> None:
        self._preserved: list[str] = []

    def restore(self, content: str) -> str:
        for i, item in enumerate(self._preserved):
            content = content.replace(self.placeholder_template.format(i), item)
        return content


class PreserveCodeBlocksRule(PreservableRule):
    name = "code_block"
    priority = 0
    placeholder_template = CODE_BLOCK_PLACEHOLDER

    def apply(self, content: str) -> str:
        self._preserved.clear()

        def save(match: re.Match[str]) -> str:
            self._preserved.append(match.group(0))
            return self.placeholder_template.format(len(self._preserved) - 1)

        return re.sub(r"```[\s\S]*?```", save, content)


class PreserveInlineCodeRule(PreservableRule):
    name = "inline_code"
    priority = 1
    placeholder_template = INLINE_CODE_PLACEHOLDER

    def apply(self, content: str) -> str:
        self._preserved.clear()

        def save(match: re.Match[str]) -> str:
            self._preserved.append(match.group(0))
            return self.placeholder_template.format(len(self._preserved) - 1)

        return re.sub(r"`[^`]+`", save, content)


class MarkdownBoldRule(BaseRule):
    name = "md_bold"
    priority = 10

    def apply(self, content: str) -> str:
        content = re.sub(r"\*\*(.+?)\*\*", rf"{BOLD_PLACEHOLDER}\1{BOLD_PLACEHOLDER}", content)
        content = re.sub(r"__(.+?)__", rf"{BOLD_PLACEHOLDER}\1{BOLD_PLACEHOLDER}", content)
        return content


class MarkdownItalicRule(BaseRule):
    name = "md_italic"
    priority = 20

    def apply(self, content: str) -> str:
        return re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"_\1_", content)


class MarkdownFinalizeBoldRule(BaseRule):
    name = "md_finalize_bold"
    priority = 25

    def apply(self, content: str) -> str:
        return content.replace(BOLD_PLACEHOLDER, "*")


class MarkdownStrikethroughRule(BaseRule):
    name = "md_strikethrough"
    priority = 30

    def apply(self, content: str) -> str:
        return re.sub(r"~~(.+?)~~", r"~\1~", content)


class HTMLBoldRule(BaseRule):
    name = "html_bold"
    priority = 10

    def apply(self, content: str) -> str:
        def replace_with_trimmed(match: re.Match[str]) -> str:
            inner = match.group(1)
            leading_ws = inner[: len(inner) - len(inner.lstrip())]
            trailing_ws = inner[len(inner.rstrip()) :]
            trimmed = inner.strip()

            if not trimmed:  # Only whitespace inside
                return inner  # Return just the whitespace, skip empty formatting

            return f"{leading_ws}*{trimmed}*{trailing_ws}"

        return re.sub(
            r"<(?:b|strong)>(.*?)</(?:b|strong)>",
            replace_with_trimmed,
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )


class HTMLItalicRule(BaseRule):
    name = "html_italic"
    priority = 20

    def apply(self, content: str) -> str:
        def replace_with_trimmed(match: re.Match[str]) -> str:
            inner = match.group(1)
            leading_ws = inner[: len(inner) - len(inner.lstrip())]
            trailing_ws = inner[len(inner.rstrip()) :]
            trimmed = inner.strip()

            if not trimmed:  # Only whitespace inside
                return inner  # Return just the whitespace, skip empty formatting

            return f"{leading_ws}_{trimmed}_{trailing_ws}"

        return re.sub(
            r"<(?:i|em)>(.*?)</(?:i|em)>",
            replace_with_trimmed,
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )


class HTMLStrikethroughRule(BaseRule):
    name = "html_strikethrough"
    priority = 30

    def apply(self, content: str) -> str:
        def replace_with_trimmed(match: re.Match[str]) -> str:
            inner = match.group(1)
            leading_ws = inner[: len(inner) - len(inner.lstrip())]
            trailing_ws = inner[len(inner.rstrip()) :]
            trimmed = inner.strip()

            if not trimmed:  # Only whitespace inside
                return inner  # Return just the whitespace, skip empty formatting

            return f"{leading_ws}~{trimmed}~{trailing_ws}"

        return re.sub(
            r"<(?:s|strike|del)>(.*?)</(?:s|strike|del)>",
            replace_with_trimmed,
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )


class HTMLCodeRule(BaseRule):
    name = "html_code"
    priority = 5

    def apply(self, content: str) -> str:
        return re.sub(
            r"<code>(.*?)</code>",
            r"`\1`",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )


class HTMLLineBreakRule(BaseRule):
    name = "html_br"
    priority = 40

    def apply(self, content: str) -> str:
        return re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)


class HTMLParagraphRule(BaseRule):
    name = "html_paragraph"
    priority = 45

    def apply(self, content: str) -> str:
        content = re.sub(r"<p>(.*?)</p>", r"\1\n\n", content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r"</p>", "\n\n", content, flags=re.IGNORECASE)
        content = re.sub(r"<p>", "", content, flags=re.IGNORECASE)
        return content


class HTMLUnorderedListRule(BaseRule):
    name = "html_ul"
    priority = 50

    def apply(self, content: str) -> str:
        def convert_ul(match: re.Match[str]) -> str:
            list_content = match.group(1)
            items = re.findall(r"<li>(.*?)</li>", list_content, flags=re.IGNORECASE | re.DOTALL)
            return "\n".join(f"- {item.strip()}" for item in items) + "\n"

        return re.sub(r"<ul>(.*?)</ul>", convert_ul, content, flags=re.IGNORECASE | re.DOTALL)


class HTMLOrderedListRule(BaseRule):
    name = "html_ol"
    priority = 51

    def apply(self, content: str) -> str:
        def convert_ol(match: re.Match[str]) -> str:
            list_content = match.group(1)
            items = re.findall(r"<li>(.*?)</li>", list_content, flags=re.IGNORECASE | re.DOTALL)
            return "\n".join(f"{i}. {item.strip()}" for i, item in enumerate(items, 1)) + "\n"

        return re.sub(r"<ol>(.*?)</ol>", convert_ol, content, flags=re.IGNORECASE | re.DOTALL)


class HTMLBlockquoteRule(BaseRule):
    name = "html_blockquote"
    priority = 52

    def apply(self, content: str) -> str:
        def convert_quote(match: re.Match[str]) -> str:
            quote_content = match.group(1).strip()
            lines = quote_content.split("\n")
            return "\n".join(f"> {line}" for line in lines)

        return re.sub(
            r"<blockquote>(.*?)</blockquote>",
            convert_quote,
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )


class HTMLPreRule(BaseRule):
    name = "html_pre"
    priority = 4

    def apply(self, content: str) -> str:
        return re.sub(
            r"<pre>(.*?)</pre>",
            r"```\1```",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )


class HTMLStripTagsRule(BaseRule):
    name = "html_strip"
    priority = 100

    def apply(self, content: str) -> str:
        return re.sub(r"<[^>]+>", "", content)


# ============================================================================
# WhatsApp to Markdown Rules
# ============================================================================


class WhatsAppPreserveCodeBlocksRule(PreservableRule):
    """Preserve WhatsApp code blocks during conversion."""

    name = "wa_code_block"
    priority = 0
    placeholder_template = CODE_BLOCK_PLACEHOLDER

    def apply(self, content: str) -> str:
        self._preserved.clear()

        def save(match: re.Match[str]) -> str:
            self._preserved.append(match.group(1))
            return self.placeholder_template.format(len(self._preserved) - 1)

        return re.sub(r"```([\s\S]*?)```", save, content)


class WhatsAppPreserveInlineCodeRule(PreservableRule):
    """Preserve WhatsApp inline code during conversion."""

    name = "wa_inline_code"
    priority = 1
    placeholder_template = INLINE_CODE_PLACEHOLDER

    def apply(self, content: str) -> str:
        self._preserved.clear()

        def save(match: re.Match[str]) -> str:
            self._preserved.append(match.group(1))
            return self.placeholder_template.format(len(self._preserved) - 1)

        return re.sub(r"`([^`]+)`", save, content)


class WhatsAppBoldToMarkdownRule(BaseRule):
    """Convert WhatsApp bold (*text*) to Markdown bold (**text**)."""

    name = "wa_bold_to_md"
    priority = 10

    def apply(self, content: str) -> str:
        # Match *text* but not **text** (which would be empty bold)
        # Use negative lookbehind/lookahead to avoid matching within words
        return re.sub(
            r"(?<![*\w])\*([^*]+)\*(?![*\w])",
            r"**\1**",
            content,
        )


class WhatsAppItalicToMarkdownRule(BaseRule):
    """Convert WhatsApp italic (_text_) to Markdown italic (*text*)."""

    name = "wa_italic_to_md"
    priority = 20

    def apply(self, content: str) -> str:
        # Match _text_ avoiding underscores within words
        return re.sub(
            r"(?<![_\w])_([^_]+)_(?![_\w])",
            r"*\1*",
            content,
        )


class WhatsAppStrikethroughToMarkdownRule(BaseRule):
    """Convert WhatsApp strikethrough (~text~) to Markdown (~~text~~)."""

    name = "wa_strike_to_md"
    priority = 30

    def apply(self, content: str) -> str:
        return re.sub(
            r"(?<![~\w])~([^~]+)~(?![~\w])",
            r"~~\1~~",
            content,
        )


class WhatsAppCodeBlockToMarkdownRule(BaseRule):
    """Restore code blocks for Markdown output."""

    name = "wa_code_block_to_md"
    priority = 90

    def __init__(self, preserve_rule: WhatsAppPreserveCodeBlocksRule) -> None:
        self._preserve_rule = preserve_rule

    def apply(self, content: str) -> str:
        for i, code in enumerate(self._preserve_rule._preserved):
            content = content.replace(
                CODE_BLOCK_PLACEHOLDER.format(i),
                f"```{code}```",
            )
        return content


class WhatsAppInlineCodeToMarkdownRule(BaseRule):
    """Restore inline code for Markdown output."""

    name = "wa_inline_code_to_md"
    priority = 91

    def __init__(self, preserve_rule: WhatsAppPreserveInlineCodeRule) -> None:
        self._preserve_rule = preserve_rule

    def apply(self, content: str) -> str:
        for i, code in enumerate(self._preserve_rule._preserved):
            content = content.replace(
                INLINE_CODE_PLACEHOLDER.format(i),
                f"`{code}`",
            )
        return content


# ============================================================================
# WhatsApp to HTML Rules
# ============================================================================


class WhatsAppBoldToHTMLRule(BaseRule):
    """Convert WhatsApp bold (*text*) to HTML (<strong>text</strong>)."""

    name = "wa_bold_to_html"
    priority = 10

    def apply(self, content: str) -> str:
        return re.sub(
            r"(?<![*\w])\*([^*]+)\*(?![*\w])",
            r"<strong>\1</strong>",
            content,
        )


class WhatsAppItalicToHTMLRule(BaseRule):
    """Convert WhatsApp italic (_text_) to HTML (<em>text</em>)."""

    name = "wa_italic_to_html"
    priority = 20

    def apply(self, content: str) -> str:
        return re.sub(
            r"(?<![_\w])_([^_]+)_(?![_\w])",
            r"<em>\1</em>",
            content,
        )


class WhatsAppStrikethroughToHTMLRule(BaseRule):
    """Convert WhatsApp strikethrough (~text~) to HTML (<del>text</del>)."""

    name = "wa_strike_to_html"
    priority = 30

    def apply(self, content: str) -> str:
        return re.sub(
            r"(?<![~\w])~([^~]+)~(?![~\w])",
            r"<del>\1</del>",
            content,
        )


class WhatsAppCodeBlockToHTMLRule(BaseRule):
    """Restore code blocks for HTML output."""

    name = "wa_code_block_to_html"
    priority = 90

    def __init__(self, preserve_rule: WhatsAppPreserveCodeBlocksRule) -> None:
        self._preserve_rule = preserve_rule

    def apply(self, content: str) -> str:
        for i, code in enumerate(self._preserve_rule._preserved):
            # Escape HTML entities in code
            escaped_code = (
                code.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            content = content.replace(
                CODE_BLOCK_PLACEHOLDER.format(i),
                f"<pre><code>{escaped_code}</code></pre>",
            )
        return content


class WhatsAppInlineCodeToHTMLRule(BaseRule):
    """Restore inline code for HTML output."""

    name = "wa_inline_code_to_html"
    priority = 91

    def __init__(self, preserve_rule: WhatsAppPreserveInlineCodeRule) -> None:
        self._preserve_rule = preserve_rule

    def apply(self, content: str) -> str:
        for i, code in enumerate(self._preserve_rule._preserved):
            # Escape HTML entities in code
            escaped_code = (
                code.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            content = content.replace(
                INLINE_CODE_PLACEHOLDER.format(i),
                f"<code>{escaped_code}</code>",
            )
        return content


class WhatsAppLineBreakToHTMLRule(BaseRule):
    """Convert newlines to HTML line breaks.
    
    Priority 85 ensures this runs BEFORE code blocks are restored,
    so newlines inside code blocks remain intact.
    """

    name = "wa_br_to_html"
    priority = 85

    def apply(self, content: str) -> str:
        return content.replace("\n", "<br>\n")
