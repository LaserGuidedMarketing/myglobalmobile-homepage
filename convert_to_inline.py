#!/usr/bin/env python3
"""
Convert CSS to inline styles - comprehensive version
"""

import re
from pathlib import Path
from collections import defaultdict

input_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')
output_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')

content = input_path.read_text(encoding='utf-8')

# Extract CSS variables first
vars_pattern = r'--([\w-]+):\s*([^;]+);'
vars = dict(re.findall(vars_pattern, content))
print(f"CSS variables: {list(vars.keys())}")

def expand_vars(text):
    for name, value in vars.items():
        text = text.replace(f'var(--{name})', value)
    return text

# Extract the style block
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if not style_match:
    print("No style block found")
    exit(1)

css = style_match.group(1)

# Extract @media blocks first (preserve these)
media_blocks = []
css_without_media = css

# Find all @media blocks
media_start = 0
while True:
    at_idx = css_without_media.find('@media', media_start)
    if at_idx == -1:
        break
    
    # Find opening brace
    open_brace = css_without_media.find('{', at_idx)
    if open_brace == -1:
        break
    
    # Count braces to find matching close
    depth = 1
    pos = open_brace + 1
    while depth > 0 and pos < len(css_without_media):
        if css_without_media[pos] == '{':
            depth += 1
        elif css_without_media[pos] == '}':
            depth -= 1
        pos += 1
    
    media_block = css_without_media[at_idx:pos]
    media_blocks.append(expand_vars(media_block))
    # Remove from css_without_media
    css_without_media = css_without_media[:at_idx] + css_without_media[pos:]
    media_start = at_idx

print(f"Found {len(media_blocks)} media blocks")

# Now parse regular CSS rules from remaining CSS
# Handle nested braces by flattening
class_styles = defaultdict(dict)

# Pattern for .class { props }
# Need to handle multi-line and nested
rule_pattern = r'\.([a-zA-Z_-][\w-]*)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'

for match in re.finditer(rule_pattern, css_without_media):
    class_name = match.group(1)
    props_text = expand_vars(match.group(2))
    
    # Parse properties
    for prop_match in re.finditer(r'([\w-]+)\s*:\s*([^;]+)', props_text):
        prop_name = prop_match.group(1).strip()
        prop_value = prop_match.group(2).strip()
        class_styles[class_name][prop_name] = prop_value

# Also handle element selectors we want to inline
element_styles = {}
element_selectors = ['body', 'section', 'nav', 'footer', '.navbar', '.hero', '.btn']

for selector in element_selectors:
    pattern = rf'{re.escape(selector)}\s*\{{([^{{}}]*)\}}'
    match = re.search(pattern, css_without_media)
    if match:
        props = {}
        props_text = expand_vars(match.group(1))
        for prop_match in re.finditer(r'([\w-]+)\s*:\s*([^;]+)', props_text):
            props[prop_match.group(1).strip()] = prop_match.group(2).strip()
        if selector.startswith('.'):
            class_styles[selector[1:]].update(props)
        else:
            element_styles[selector] = props

print(f"Found {len(class_styles)} classes with styles")
print(f"Found {len(element_styles)} element selectors")

# Apply styles to HTML
html = content

# Add inline styles to elements with classes
class_attr_pattern = r'class="([^"]*)"'

def process_class_attr(match):
    class_list = match.group(1).split()
    combined = {}
    
    for cls in class_list:
        if cls in class_styles:
            combined.update(class_styles[cls])
    
    if combined:
        style = '; '.join(f"{k}: {v}" for k, v in combined.items())
        return f'class="{match.group(1)}" style="{style}"'
    return match.group(0)

html = re.sub(class_attr_pattern, process_class_attr, html)

# Build new minimal style block
new_style = '''<style>
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
'''

for mb in media_blocks:
    new_style += '\n' + mb + '\n'

new_style += '    </style>'

# Replace
old_style = style_match.group(0)
html = html.replace(old_style, new_style)

output_path.write_text(html, encoding='utf-8')
print(f"\nOutput saved to {output_path}")

# Count inline styles added
inline_count = html.count('style="')
print(f"Total elements with inline styles: {inline_count}")
