import os

def update_static_paths(directory):
    """
    Update all HTML files in directory to use static paths for CSS and JS files
    """
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            filepath = os.path.join(directory, filename)
            
            # Read the file
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace CSS paths
            content = content.replace('href="swift.css"', 'href="/static/css/swift.css"')
            content = content.replace("href='swift.css'", "href='/static/css/swift.css'")
            
            # Replace JS paths
            content = content.replace('src="script.js"', 'src="/static/js/script.js"')
            content = content.replace("src='script.js'", "src='/static/js/script.js'")
            
            # Write the updated content back to the file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            
            print(f"Updated {filepath}")

if __name__ == "__main__":
    update_static_paths("templates") 