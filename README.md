# WhatsApp Formatter

A Python library to convert Markdown and HTML to WhatsApp-compatible formatting.

## Installation

```bash
pip install py-whatsapp-formatter
```

## Usage

```python
from whatsapp_formatter import convert_markdown_to_whatsapp, convert_html_to_whatsapp

# Convert Markdown to WhatsApp format
text = convert_markdown_to_whatsapp("**Bold** and *italic* and ~~strikethrough~~")
# Output: "*Bold* and _italic_ and ~strikethrough~"

# Convert HTML to WhatsApp format
text = convert_html_to_whatsapp("<strong>Bold</strong> <em>italic</em>")
# Output: "*Bold* _italic_"
```

## WhatsApp Formatting Reference

| Format | WhatsApp Syntax | Markdown | HTML |
|--------|-----------------|----------|------|
| Bold | `*text*` | `**text**` | `<b>`, `<strong>` |
| Italic | `_text_` | `*text*` | `<i>`, `<em>` |
| Strikethrough | `~text~` | `~~text~~` | `<s>`, `<strike>`, `<del>` |
| Monospace | `` `text` `` | `` `text` `` | `<code>` |
| Code block | ` ```text``` ` | ` ```text``` ` | - |

## Advanced Usage

For more control, use the converter classes directly:

```python
from whatsapp_formatter import MarkdownToWhatsAppConverter, HTMLToWhatsAppConverter

# Custom Markdown converter
converter = MarkdownToWhatsAppConverter()
converter.add_post_processor(lambda x: x.strip())
result = converter.convert("  **Hello**  ")

# HTML converter without tag stripping
converter = HTMLToWhatsAppConverter(strip_remaining_tags=False)
result = converter.convert("<b>Bold</b> <span>kept</span>")
```

## Requirements

- Python 3.9+
- No external dependencies

## License

MIT License

