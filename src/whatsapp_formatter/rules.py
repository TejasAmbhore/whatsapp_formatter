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


class HTMLStripTagsRule(BaseRule):
    name = "html_strip"
    priority = 100

    def apply(self, content: str) -> str:
        return re.sub(r"<[^>]+>", "", content)
