import os
import re

def update_html_links(directory):
    """
    Update all HTML links in HTML files to use URL patterns instead of direct file links
    """
    # Define a pattern to match href to html files
    pattern = r'href=["\']([^"\']+\.html)["\']'
    
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            filepath = os.path.join(directory, filename)
            
            # Read the file
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Find all HTML links
            matches = re.findall(pattern, content)
            
            # Replace links that are direct file references
            for match in matches:
                # Skip if it's already an absolute path
                if match.startswith('/') or match.startswith('http'):
                    continue
                
                # Replace the link with the proper URL pattern
                content = content.replace(
                    f'href="{match}"', 
                    f'href="/{match}"'
                )
                content = content.replace(
                    f"href='{match}'", 
                    f"href='/{match}'"
                )
            
            # Write the updated content back to the file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            
            print(f"Updated links in {filepath}")

if __name__ == "__main__":
    update_html_links("templates") 