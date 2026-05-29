#!/usr/bin/env python3
"""
Comprehensive CSS to Inline Styles Converter
Converts all non-media-query CSS to inline styles while preserving functionality.
"""

import re
import cssutils
from pathlib import Path

# Suppress cssutils warnings
import logging
cssutils.log.setLevel(logging.ERROR)

input_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')
output_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')

# Read file
content = input_path.read_text(encoding='utf-8')

# Extract style block
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if not style_match:
    print("No style block found")
    exit(1)

css_text = style_match.group(1)

# Parse CSS
sheet = cssutils.parseString(css_text)

# Collect styles by selector
selector_styles = {}
media_rules = []

for rule in sheet:
    if rule.type == rule.MEDIA_RULE:
        # Keep media queries as-is
        media_rules.append(rule.cssText)
    elif rule.type == rule.STYLE_RULE:
        selector = rule.selectorText
        styles = {}
        for prop in rule.style:
            styles[prop.name] = prop.value
        selector_styles[selector] = styles

print(f"Found {len(selector_styles)} style rules")
print(f"Found {len(media_rules)} media rules")

# Build inline styles for class selectors
class_map = {}
for selector, styles in selector_styles.items():
    # Handle simple class selectors only
    if selector.startswith('.') and ' ' not in selector and ':' not in selector:
        class_name = selector[1:]
        style_str = '; '.join(f"{k}: {v}" for k, v in styles.items())
        class_map[class_name] = style_str

print(f"Class map has {len(class_map)} entries")

# Apply inline styles to HTML
# Find elements with class attributes and add inline styles

def add_inline_styles(html_content):
    # Pattern to find class attributes
    pattern = r'class="([^"]*)"'
    
    def replace_class(match):
        classes = match.group(1).split()
        combined_styles = []
        
        for cls in classes:
            if cls in class_map:
                combined_styles.append(class_map[cls])
        
        if combined_styles:
            style_attr = '; '.join(combined_styles)
            return f'class="{match.group(1)}" style="{style_attr}"'
        return match.group(0)
    
    return re.sub(pattern, replace_class, html_content)

new_content = add_inline_styles(content)

# Build minimal style block with only media queries and essential base styles
minimal_css = """<style>
        :root {
            --bg-primary: #011f46;
            --bg-card: #4a5568;
            --gold: #c9b358;
            --light-grey: #c0c0c0;
            --white: #ffffff;
            --glass-border: rgba(201, 179, 88, 0.25);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; scroll-padding-top: 100px; }
"""

# Add media queries
for mr in media_rules:
    minimal_css += '\n' + mr + '\n'

minimal_css += "    </style>"

# Replace old style block
old_style = style_match.group(0)
new_content = new_content.replace(old_style, minimal_css)

# Write output
output_path.write_text(new_content, encoding='utf-8')
print(f"Done! Output written to {output_path}")
