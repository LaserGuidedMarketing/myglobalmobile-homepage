#!/usr/bin/env python3
"""
Simplify CSS by converting all non-media-query styles to inline attributes.
Keep only @media queries in the <style> block.
"""

import re
from pathlib import Path

# Read the original file
input_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')
output_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')
backup_path = Path('/root/.openclaw/workspace/myglobalmobile/index-backup-pre-simplify.html')

content = input_path.read_text(encoding='utf-8')

# Save backup
backup_path.write_text(content, encoding='utf-8')

# Extract CSS from <style> block
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if not style_match:
    print("No <style> block found!")
    exit(1)

css_content = style_match.group(1)

# Parse CSS variables
vars_match = re.findall(r'--([\w-]+):\s*([^;]+);', css_content)
css_vars = {f'var(--{name})': value.strip() for name, value in vars_match}
print(f"Found {len(css_vars)} CSS variables")

# Function to replace CSS vars in a string
def replace_vars(s):
    for var_name, var_value in css_vars.items():
        s = s.replace(var_name, var_value)
    return s

# Extract all @media blocks properly
media_blocks = []
remaining_css = css_content

# Pattern for @media blocks - handles nested braces
media_start = 0
while True:
    media_idx = remaining_css.find('@media', media_start)
    if media_idx == -1:
        break
    
    # Find opening brace
    brace_idx = remaining_css.find('{', media_idx)
    if brace_idx == -1:
        break
    
    # Count braces to find the matching closing brace
    brace_count = 1
    pos = brace_idx + 1
    while brace_count > 0 and pos < len(remaining_css):
        if remaining_css[pos] == '{':
            brace_count += 1
        elif remaining_css[pos] == '}':
            brace_count -= 1
        pos += 1
    
    media_block = remaining_css[media_idx:pos]
    media_blocks.append(media_block)
    media_start = pos

print(f"Found {len(media_blocks)} media queries")

# Get CSS without media blocks for parsing regular rules
css_no_media = css_content
for mb in media_blocks:
    css_no_media = css_no_media.replace(mb, '')

# Parse regular CSS rules
# Match selector { properties }
rule_pattern = r'([^{}@]+)\{([^{}]*)\}'
rules = re.findall(rule_pattern, css_no_media)

print(f"Found {len(rules)} regular CSS rules")

# Build a map of class selectors to their styles
class_styles = {}
element_styles = {}  # For tag selectors like body, html, etc.

for selector, properties in rules:
    selector = selector.strip()
    props_str = replace_vars(properties.strip())
    
    # Skip certain selectors
    if not selector or selector.startswith('/*') or ':' in selector or ' ' in selector:
        continue
    
    if selector.startswith('.'):
        # Class selector
        class_name = selector[1:]
        if class_name not in class_styles:
            class_styles[class_name] = {}
        # Parse properties
        for prop_line in props_str.split(';'):
            if ':' in prop_line:
                parts = prop_line.split(':', 1)
                prop_name = parts[0].strip()
                prop_value = parts[1].strip()
                class_styles[class_name][prop_name] = prop_value
    elif selector in ['body', 'html', 'section', 'nav', 'footer', '*']:
        # Element selector - we'll apply to all matching elements
        if selector not in element_styles:
            element_styles[selector] = {}
        for prop_line in props_str.split(';'):
            if ':' in prop_line:
                parts = prop_line.split(':', 1)
                prop_name = parts[0].strip()
                prop_value = parts[1].strip()
                element_styles[selector][prop_name] = prop_value

print(f"Parsed {len(class_styles)} class selectors")
print(f"Parsed {len(element_styles)} element selectors")

# Build inline style string from a style dict
def build_style(style_dict):
    if not style_dict:
        return None
    return '; '.join(f"{k}: {v}" for k, v in style_dict.items())

# Process HTML - add inline styles based on classes
# Process class attributes
class_pattern = r'class="([^"]*)"'

def process_classes(match):
    class_attr = match.group(1)
    classes = class_attr.split()
    
    # Collect all styles from all classes
    combined_styles = {}
    for cls in classes:
        if cls in class_styles:
            combined_styles.update(class_styles[cls])
    
    if combined_styles:
        style_str = build_style(combined_styles)
        return f'class="{class_attr}" style="{style_str}"'
    return match.group(0)

new_content = re.sub(class_pattern, process_classes, content)

# Also add styles to elements without classes but with element selectors
# This is trickier - we need to match tags
tags_to_style = list(element_styles.keys())
for tag in tags_to_style:
    if tag == '*':
        continue  # Skip universal selector
    style_str = build_style(element_styles[tag])
    if style_str:
        # Add style to opening tags of this element type
        # Match <tag ...> but not <tag ... style=...>
        tag_pattern = rf'<{tag}\b([^>]*)>'
        def add_style_to_tag(m):
            attrs = m.group(1)
            if 'style=' in attrs:
                # Merge with existing style
                existing = re.search(r'style="([^"]*)"', attrs)
                if existing:
                    old_style = existing.group(1)
                    new_style = f"{old_style}; {style_str}"
                    old_attr = f'style="{old_style}"'
                    new_attr = f'style="{new_style}"'
                    return f'<{tag}{attrs.replace(old_attr, new_attr)}>'
            return f'<{tag}{attrs} style="{style_str}">'
        new_content = re.sub(tag_pattern, add_style_to_tag, new_content)

# Create new style block with only CSS vars and media queries
new_style = '''<style>
        /* CSS Variables - Unified Color Scheme */
        :root {
            --bg-primary: #011f46;
            --bg-card: #4a5568;
            --gold: #c9b358;
            --light-grey: #c0c0c0;
            --white: #ffffff;
            --glass-border: rgba(201, 179, 88, 0.25);
        }

        /* Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
            scroll-padding-top: 100px;
        }

        /* Base body styles */
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-primary);
            color: var(--white);
            line-height: 1.6;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
'''

# Add media queries
for mb in media_blocks:
    new_style += '\n' + mb + '\n'

new_style += '    </style>'

# Replace old style block
old_style = style_match.group(0)
new_content = new_content.replace(old_style, new_style)

# Write output
output_path.write_text(new_content, encoding='utf-8')
print(f"Simplified HTML written to {output_path}")
print(f"Backup saved to {backup_path}")
