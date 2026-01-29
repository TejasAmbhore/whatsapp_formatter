# WhatsApp Formatter

A Python library for bidirectional conversion between WhatsApp, Markdown, and HTML formatting.

## Installation

```bash
pip install py-whatsapp-formatter
```

## Usage

### Convert to WhatsApp Format

```python
from whatsapp_formatter import convert_markdown_to_whatsapp, convert_html_to_whatsapp

# Convert Markdown to WhatsApp format
text = convert_markdown_to_whatsapp("**Bold** and *italic* and ~~strikethrough~~")
# Output: "*Bold* and _italic_ and ~strikethrough~"

# Convert HTML to WhatsApp format
text = convert_html_to_whatsapp("<strong>Bold</strong> <em>italic</em>")
# Output: "*Bold* _italic_"
```

### Convert from WhatsApp Format

```python
from whatsapp_formatter import convert_whatsapp_to_markdown, convert_whatsapp_to_html

# Convert WhatsApp to Markdown format
text = convert_whatsapp_to_markdown("*Bold* and _italic_ and ~strikethrough~")
# Output: "**Bold** and *italic* and ~~strikethrough~~"

# Convert WhatsApp to HTML format
text = convert_whatsapp_to_html("*Bold* and _italic_ and ~strikethrough~")
# Output: "<strong>Bold</strong> and <em>italic</em> and <del>strikethrough</del>"
```

## WhatsApp Formatting Reference

| Format | WhatsApp | Markdown | HTML |
|--------|----------|----------|------|
| Bold | `*text*` | `**text**` | `<b>`, `<strong>` |
| Italic | `_text_` | `*text*` | `<i>`, `<em>` |
| Strikethrough | `~text~` | `~~text~~` | `<s>`, `<strike>`, `<del>` |
| Monospace | `` `text` `` | `` `text` `` | `<code>` |
| Code block | ` ```text``` ` | ` ```text``` ` | `<pre><code>` |

All conversions are bidirectional. Nested formatting is supported (e.g., `*_bold and italic_*`).

## Advanced Usage

For more control, use the converter classes directly:

```python
from whatsapp_formatter import (
    MarkdownToWhatsAppConverter,
    HTMLToWhatsAppConverter,
    WhatsAppToMarkdownConverter,
    WhatsAppToHTMLConverter,
)

# Custom Markdown converter with post-processing
converter = MarkdownToWhatsAppConverter()
converter.add_post_processor(lambda x: x.strip())
result = converter.convert("  **Hello**  ")

# HTML converter without tag stripping
converter = HTMLToWhatsAppConverter(strip_remaining_tags=False)
result = converter.convert("<b>Bold</b> <span>kept</span>")

# WhatsApp to Markdown
converter = WhatsAppToMarkdownConverter()
result = converter.convert("*bold* _italic_ ~strike~")
# Output: "**bold** *italic* ~~strike~~"

# WhatsApp to HTML (with optional line break conversion)
converter = WhatsAppToHTMLConverter(include_line_breaks=True)
result = converter.convert("*bold*\n_italic_")
# Output: "<strong>bold</strong><br>\n<em>italic</em>"
```

## Requirements

- Python 3.9+
- No external dependencies

## License

MIT License

