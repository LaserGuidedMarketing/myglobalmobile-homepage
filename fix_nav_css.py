#!/usr/bin/env python3
import re

# Read homepage and extract nav CSS
with open('/root/.openclaw/workspace/myglobalmobile/index.html', 'r') as f:
    homepage = f.read()

# Extract from .navbar to start of .hero
nav_match = re.search(r'(\.navbar \{.*?)(\.hero \{)', homepage, re.DOTALL)
if nav_match:
    nav_css = nav_match.group(1)
    print(f"Extracted {len(nav_css)} characters of nav CSS")
else:
    print("Could not find nav CSS")
    exit(1)

# Read AI page
with open('/root/.openclaw/workspace/myglobalmobile/ai-business-automation-agency.html', 'r') as f:
    ai_page = f.read()

# Find and replace nav CSS in AI page (from /* Header/Nav */ to /* Hero */)
pattern = r'/\* Header/Nav \*/.*?/\* Hero \*/'
replacement = '/* Header/Nav */\n' + nav_css + '/* Hero */'

ai_page_new = re.sub(pattern, replacement, ai_page, flags=re.DOTALL)

if ai_page_new == ai_page:
    print("Pattern not found, trying without comments...")
    # Try finding from .navbar to .hero
    pattern2 = r'(\.navbar \{.*?)(\.hero \{)'
    ai_page_new = re.sub(pattern2, replacement, ai_page, flags=re.DOTALL)

# Write back
with open('/root/.openclaw/workspace/myglobalmobile/ai-business-automation-agency.html', 'w') as f:
    f.write(ai_page_new)

print("Nav CSS replaced successfully!")
