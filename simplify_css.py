#!/usr/bin/env python3
"""
Simplify CSS by converting all non-media-query styles to inline attributes.
Keep only @media queries in the <style> block.
"""

import re
import html
from pathlib import Path

# Read the original file
input_path = Path('/root/.openclaw/workspace/myglobalmobile/index.html')
output_path = Path('/root/.openclaw/workspace/myglobalmobile/index-simplified.html')

content = input_path.read_text(encoding='utf-8')

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

# Split into media queries and regular rules
media_queries = []
regular_rules = []

# Find all @media blocks
media_pattern = r'@media[^{]*\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
media_matches = re.finditer(media_pattern, css_content, re.DOTALL)
for match in media_matches:
    media_queries.append(match.group(0))

# Remove media queries from CSS to get regular rules
css_without_media = re.sub(media_pattern, '', css_content, flags=re.DOTALL)

# Parse regular CSS rules (selector { properties })
rule_pattern = r'([^{]+)\{([^}]*)\}'
rules = re.findall(rule_pattern, css_without_media)

print(f"Found {len(rules)} regular CSS rules")
print(f"Found {len(media_queries)} media queries")

# Build a map of selectors to their styles
selector_styles = {}
for selector, properties in rules:
    selector = selector.strip()
    # Skip @font-face, @keyframes, etc.
    if selector.startswith('@'):
        continue
    # Skip CSS variables in :root
    if ':root' in selector:
        continue
    # Skip comments
    if selector.startswith('/*'):
        continue
    
    props = {}
    for prop_line in properties.split(';'):
        if ':' in prop_line:
            parts = prop_line.split(':', 1)
            prop_name = parts[0].strip()
            prop_value = parts[1].strip()
            # Replace CSS variables
            for var_name, var_value in css_vars.items():
                prop_value = prop_value.replace(var_name, var_value)
            props[prop_name] = prop_value
    
    if props:
        # Handle multiple selectors separated by comma
        for sel in selector.split(','):
            sel = sel.strip()
            if sel not in selector_styles:
                selector_styles[sel] = {}
            selector_styles[sel].update(props)

print(f"Parsed {len(selector_styles)} unique selectors")

# Now we need to apply these styles to HTML elements
# This is complex because we need to match CSS selectors to HTML elements
# For simplicity, we'll focus on class-based selectors which are most common

# Create a mapping of class names to styles
class_styles = {}
for selector, styles in selector_styles.items():
    # Handle .class selectors
    if selector.startswith('.') and ' ' not in selector and ':' not in selector:
        class_name = selector[1:]  # Remove the dot
        class_styles[class_name] = styles

print(f"Found {len(class_styles)} class-based selectors")

# Now process the HTML and add inline styles
# We'll do this by replacing class attributes with class + style attributes

def get_inline_style(class_names):
    """Get combined inline styles for a list of class names."""
    combined_styles = {}
    for cls in class_names:
        if cls in class_styles:
            combined_styles.update(class_styles[cls])
    
    if not combined_styles:
        return None
    
    return '; '.join(f"{k}: {v}" for k, v in combined_styles.items())

# Find all elements with class attributes
# Pattern to match HTML tags with class attributes
tag_pattern = r'<([a-zA-Z][a-zA-Z0-9]*)\s+[^>]*class="([^"]*)"[^>]*>'

def replace_tag(match):
    tag_name = match.group(1)
    class_attr = match.group(2)
    full_match = match.group(0)
    
    # Skip if it's a script or style tag
    if tag_name in ['script', 'style']:
        return full_match
    
    class_names = class_attr.split()
    inline_style = get_inline_style(class_names)
    
    if inline_style:
        # Check if tag already has style attribute
        if 'style="' in full_match:
            # Merge styles
            existing_style_match = re.search(r'style="([^"]*)"', full_match)
            if existing_style_match:
                existing_style = existing_style_match.group(1)
                merged_style = f"{existing_style}; {inline_style}"
                full_match = full_match.replace(f'style="{existing_style}"', f'style="{merged_style}"')
        else:
            # Add style attribute before the closing >
            full_match = full_match.rstrip('>') + f' style="{inline_style}">'
    
    return full_match

# Apply the transformation
new_content = re.sub(tag_pattern, replace_tag, content)

# Now create the new style block with only media queries
new_style_block = '<style>\n'
new_style_block += '        /* CSS Variables - Unified Color Scheme */\n'
new_style_block += '        :root {\n'
new_style_block += '            --bg-primary: #011f46;\n'
new_style_block += '            --bg-card: #4a5568;\n'
new_style_block += '            --gold: #c9b358;\n'
new_style_block += '            --light-grey: #c0c0c0;\n'
new_style_block += '            --white: #ffffff;\n'
new_style_block += '            --glass-border: rgba(201, 179, 88, 0.25);\n'
new_style_block += '        }\n\n'

# Add media queries
for mq in media_queries:
    new_style_block += f'        {mq}\n\n'

new_style_block += '    </style>'

# Replace the old style block with the new one
old_style_block = style_match.group(0)
new_content = new_content.replace(old_style_block, new_style_block)

# Write the output
output_path.write_text(new_content, encoding='utf-8')
print(f"Simplified HTML written to {output_path}")
print(f"Original size: {len(content)} bytes")
print(f"New size: {len(new_content)} bytes")
