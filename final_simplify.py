#!/usr/bin/env python3
"""
Final CSS to Inline Styles Converter - Pure Python
"""

import re
from pathlib import Path

input_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')
output_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')

content = input_path.read_text(encoding='utf-8')

# Extract style block
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if not style_match:
    print("No style block found")
    exit(1)

css_text = style_match.group(1)

# Extract CSS variables
vars_match = re.findall(r'--([\w-]+):\s*([^;]+);', css_text)
css_vars = {f'var(--{name})': value.strip() for name, value in vars_match}

def replace_vars(text):
    for var_name, var_value in css_vars.items():
        text = text.replace(var_name, var_value)
    return text

# Extract @media blocks
media_blocks = []
remaining = css_text

while '@media' in remaining:
    idx = remaining.find('@media')
    brace_idx = remaining.find('{', idx)
    if brace_idx == -1:
        break
    
    # Find matching closing brace
    count = 1
    pos = brace_idx + 1
    while count > 0 and pos < len(remaining):
        if remaining[pos] == '{':
            count += 1
        elif remaining[pos] == '}':
            count -= 1
        pos += 1
    
    media_blocks.append(remaining[idx:pos])
    remaining = remaining[:idx] + remaining[pos:]

print(f"Found {len(media_blocks)} media blocks")

# Parse remaining CSS rules
class_styles = {}

# Match .classname { properties }
rule_pattern = r'\.([a-zA-Z_][\w-]*)\s*\{([^}]*)\}'
for match in re.finditer(rule_pattern, remaining):
    class_name = match.group(1)
    properties = replace_vars(match.group(2).strip())
    
    # Parse properties
    styles = {}
    for prop in properties.split(';'):
        if ':' in prop:
            parts = prop.split(':', 1)
            name = parts[0].strip()
            value = parts[1].strip()
            styles[name] = value
    
    if class_name not in class_styles:
        class_styles[class_name] = {}
    class_styles[class_name].update(styles)

print(f"Found {len(class_styles)} class definitions")

# Apply inline styles
html = content

# Find all class="..." and add style attributes
class_pattern = r'class="([^"]*)"'

def add_styles(match):
    classes = match.group(1).split()
    all_styles = {}
    
    for cls in classes:
        if cls in class_styles:
            all_styles.update(class_styles[cls])
    
    if all_styles:
        style_str = '; '.join(f"{k}: {v}" for k, v in all_styles.items())
        return f'class="{match.group(1)}" style="{style_str}"'
    return match.group(0)

html = re.sub(class_pattern, add_styles, html)

# Build minimal style block
minimal_style = '''<style>
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
    minimal_style += '\n' + mb + '\n'

minimal_style += '    </style>'

# Replace old style block
old_style = style_match.group(0)
html = html.replace(old_style, minimal_style)

# Write output
output_path.write_text(html, encoding='utf-8')
print(f"Done! Saved to {output_path}")
print(f"Media queries preserved: {len(media_blocks)}")
print(f"Classes with inline styles: {len([c for c in class_styles if c in html])}")
