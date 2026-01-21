"""WhatsApp format converters."""

from __future__ import annotations

from typing import Callable

from .rules import (
    BaseRule,
    HTMLBoldRule,
    HTMLCodeRule,
    HTMLItalicRule,
    HTMLStrikethroughRule,
    HTMLStripTagsRule,
    MarkdownBoldRule,
    MarkdownFinalizeBoldRule,
    MarkdownItalicRule,
    MarkdownStrikethroughRule,
    PreserveCodeBlocksRule,
    PreserveInlineCodeRule,
)


class BaseConverter:
    """Base converter with rule-based processing pipeline."""

    def __init__(self) -> None:
        self._rules: list[BaseRule] = []
        self._pre_processors: list[Callable[[str], str]] = []
        self._post_processors: list[Callable[[str], str]] = []

    def add_rule(self, rule: BaseRule) -> BaseConverter:
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority)
        return self

    def remove_rule(self, rule_name: str) -> BaseConverter:
        self._rules = [r for r in self._rules if r.name != rule_name]
        return self

    def add_pre_processor(self, processor: Callable[[str], str]) -> BaseConverter:
        self._pre_processors.append(processor)
        return self

    def add_post_processor(self, processor: Callable[[str], str]) -> BaseConverter:
        self._post_processors.append(processor)
        return self

    def convert(self, content: str) -> str:
        if not content:
            return content

        for processor in self._pre_processors:
            content = processor(content)

        for rule in self._rules:
            content = rule.apply(content)

        for processor in self._post_processors:
            content = processor(content)

        return content


class MarkdownToWhatsAppConverter(BaseConverter):
    """Converts Markdown formatting to WhatsApp format."""

    def __init__(self) -> None:
        super().__init__()
        self._code_block_rule = PreserveCodeBlocksRule()
        self._inline_code_rule = PreserveInlineCodeRule()

        self.add_rule(self._code_block_rule)
        self.add_rule(self._inline_code_rule)
        self.add_rule(MarkdownBoldRule())
        self.add_rule(MarkdownItalicRule())
        self.add_rule(MarkdownFinalizeBoldRule())
        self.add_rule(MarkdownStrikethroughRule())

    def convert(self, content: str) -> str:
        if not content:
            return content

        for processor in self._pre_processors:
            content = processor(content)

        for rule in self._rules:
            content = rule.apply(content)

        content = self._inline_code_rule.restore(content)
        content = self._code_block_rule.restore(content)

        for processor in self._post_processors:
            content = processor(content)

        return content


class HTMLToWhatsAppConverter(BaseConverter):
    """Converts HTML formatting to WhatsApp format."""

    def __init__(self, strip_remaining_tags: bool = True) -> None:
        super().__init__()

        self.add_rule(HTMLCodeRule())
        self.add_rule(HTMLBoldRule())
        self.add_rule(HTMLItalicRule())
        self.add_rule(HTMLStrikethroughRule())

        if strip_remaining_tags:
            self.add_rule(HTMLStripTagsRule())
