"""Formatting rules using the Strategy Pattern."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Protocol

BOLD_PLACEHOLDER = "\x00WA_BOLD\x00"
CODE_BLOCK_PLACEHOLDER = "\x00CODE_BLOCK_{}\x00"
INLINE_CODE_PLACEHOLDER = "\x00INLINE_CODE_{}\x00"


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
        return re.sub(
            r"<(?:b|strong)>(.*?)</(?:b|strong)>",
            r"*\1*",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )


class HTMLItalicRule(BaseRule):
    name = "html_italic"
    priority = 20

    def apply(self, content: str) -> str:
        return re.sub(
            r"<(?:i|em)>(.*?)</(?:i|em)>",
            r"_\1_",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )


class HTMLStrikethroughRule(BaseRule):
    name = "html_strikethrough"
    priority = 30

    def apply(self, content: str) -> str:
        return re.sub(
            r"<(?:s|strike|del)>(.*?)</(?:s|strike|del)>",
            r"~\1~",
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
