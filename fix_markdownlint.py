#!/usr/bin/env python3
"""
Markdownlint Fixer Script
Automatically fixes common markdownlint issues in Markdown files.
"""

import os
import re
import glob

def fix_markdown_file(file_path):
    """Fix markdownlint issues in a single file."""
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix MD022: Add blank lines around headings
    # Pattern: heading followed immediately by non-blank line
    content = re.sub(r'^(#{1,6}\s+.*?)$\n(?!\n)', r'\1\n\n', content, flags=re.MULTILINE)
    
    # Fix MD032: Add blank lines around lists
    # Pattern: list item not preceded by blank line
    content = re.sub(r'^(?!\n)(.*?)\n^(\s*[-*+]\s)', r'\1\n\n\2', content, flags=re.MULTILINE)
    
    # Pattern: list item not followed by blank line (when next line is not a list item)
    content = re.sub(r'^(\s*[-*+]\s.*?)$\n(?!\n)(?!\s*[-*+]\s)', r'\1\n\n', content, flags=re.MULTILINE)
    
    # Fix MD024: Make duplicate headings unique by adding numbers
    headings = {}
    def replace_duplicate_heading(match):
        heading_text = match.group(1)
        if heading_text in headings:
            headings[heading_text] += 1
            return f"### **{heading_text} ({headings[heading_text]})**"
        else:
            headings[heading_text] = 1
            return match.group(0)
    
    # Apply to level 3 headings (###)
    content = re.sub(r'^### \*\*(.*?)\*\*$', replace_duplicate_heading, content, flags=re.MULTILINE)
    
    # Clean up multiple consecutive blank lines (max 2)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Ensure file ends with single newline
    content = content.rstrip() + '\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

def main():
    """Main function to fix all markdown files."""
    # Find all markdown files
    md_files = glob.glob("*.md")
    
    print(f"Found {len(md_files)} markdown files to fix:")
    for file in md_files:
        print(f"  - {file}")
    
    print("\nStarting fixes...")
    
    for md_file in md_files:
        try:
            fix_markdown_file(md_file)
        except Exception as e:
            print(f"Error fixing {md_file}: {e}")
    
    print("\nAll markdown files have been processed!")

if __name__ == "__main__":
    main()

