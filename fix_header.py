#!/usr/bin/env python3

import re

# Read the AI page
with open('/root/.openclaw/workspace/myglobalmobile/ai-business-automation-agency.html', 'r') as f:
    content = f.read()

# The exact header/nav CSS from homepage (from /* Header/Nav */ to start of /* Hero */)
new_header_css = '''        /* Header/Nav */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background-color: var(--bg-primary);
            border-bottom: 1px solid var(--glass-border);
        }

        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 80px;
            position: relative;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-decoration: none;
        }

        .logo img {
            height: 45px;
            width: auto;
        }

        .logo-text {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--white);
        }

        .logo-text span {
            color: var(--gold);
        }

        /* Mobile menu toggle */
        .mobile-menu-toggle {
            display: none;
            background: none;
            border: none;
            cursor: pointer;
            flex-direction: column;
            gap: 4px;
        }

        .mobile-menu-toggle span {
            display: block;
            width: 25px;
            height: 3px;
            background-color: var(--gold);
            transition: all 0.3s ease;
        }

        /* Base nav menu */
        .nav-menu {
            list-style: none;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        /* Hide FAQ on mobile */
        .faq-desktop-only {
            display: none;
        }

        .nav-item {
            position: relative;
        }

        .nav-link {
            color: var(--light-grey);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            padding: 0.6rem 0.9rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            display: inline-block;
        }

        .nav-link:hover {
            color: var(--gold);
            background-color: rgba(201, 179, 88, 0.1);
        }

        .nav-cta {
            color: var(--bg-primary);
            background-color: var(--gold);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 700;
            padding: 0.6rem 1.2rem;
            border-radius: 50px;
            white-space: nowrap;
            transition: all 0.3s ease;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .nav-cta:hover {
            background-color: #f4dd72;
        }

        .book-consult-item {
            margin-left: 10px;
        }

        /* Dropdown menu - hidden by default */
        .dropdown-menu {
            list-style: none;
            position: absolute;
            top: 100%;
            left: 0;
            background-color: var(--bg-primary);
            border: 2px solid var(--gold);
            border-radius: 12px;
            box-shadow: 0 10px 15px rgba(0,0,0,0.3);
            padding: 0;
            padding-top: 10px;
            margin: 0;
            margin-top: 0;
            min-width: 300px;
            display: none;
            z-index: 10000;
        }

        /* Invisible bridge to keep hover active */
        .dropdown-menu::before {
            content: '';
            position: absolute;
            top: -10px;
            left: 0;
            right: 0;
            height: 10px;
        }

        .dropdown-menu li {
            margin: 0;
            padding: 0;
        }

        .dropdown-item {
            display: block;
            padding: 0.75rem 1.5rem;
            color: var(--light-grey);
            text-decoration: none;
            white-space: nowrap;
            border-bottom: 1px solid var(--gold);
            transition: all 0.3s ease;
        }

        .dropdown-menu li:last-child .dropdown-item {
            border-bottom: none;
        }

        .dropdown-item:hover {
            background-color: rgba(201, 179, 88, 0.2);
            color: var(--gold);
        }

        /* Desktop: show dropdown on hover */
        @media (min-width: 1024px) {
            .dropdown-parent:hover .dropdown-menu {
                display: block;
            }

            .mobile-menu-toggle {
                display: none;
            }
        }

        /* Mobile styles */
        @media (max-width: 1023px) {
            .mobile-menu-toggle {
                display: flex;
            }

            .nav-menu {
                display: none;
                position: fixed;
                top: 80px;
                left: 0;
                right: 0;
                background-color: var(--bg-card);
                flex-direction: column;
                padding: 1.5rem;
                border-top: 1px solid var(--glass-border);
                gap: 0.5rem;
                max-height: calc(100vh - 80px);
                overflow-y: auto;
            }

            .nav-menu.active {
                display: flex;
            }

            .nav-item {
                width: 100%;
            }

            .nav-link {
                display: block;
                padding: 1rem;
                font-size: 1.1rem;
            }

            .dropdown-menu {
                position: static;
                border: none;
                box-shadow: none;
                margin: 0.5rem 0 0 1rem;
                padding-left: 1rem;
                border-left: 2px solid var(--gold);
                display: block;
                background-color: transparent;
            }

            .dropdown-item {
                padding: 0.75rem 1rem;
                border-bottom: none;
                font-size: 1rem;
            }

            .book-consult-item {
                margin: 1rem 0 0 0;
            }

            .nav-cta {
                display: block;
                text-align: center;
                padding: 1rem;
            }
        }
'''

# Find and replace the header/nav section
# Pattern: from "/* Header/Nav */" to "/* Hero */"
pattern = r'/\* Header/Nav \*/.*?/\* Hero \*/'
replacement = new_header_css + '        /* Hero */'

content_new = re.sub(pattern, replacement, content, flags=re.DOTALL)

if content_new == content:
    print("Pattern not found, trying alternative...")
    # Try without space
    pattern = r'/\*Header/Nav\*/.*?/\* Hero \*/'
    content_new = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('/root/.openclaw/workspace/myglobalmobile/ai-business-automation-agency.html', 'w') as f:
    f.write(content_new)

print("Header CSS replaced successfully!")
