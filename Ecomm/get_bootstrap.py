import os
import requests

# Paths
base_dir = os.path.join(os.getcwd(), "static")
css_dir = os.path.join(base_dir, "css")
js_dir = os.path.join(base_dir, "js")

os.makedirs(css_dir, exist_ok=True)
os.makedirs(js_dir, exist_ok=True)

# Bootstrap version
version = "5.3.2"

# Files to download
files = {
    f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/css/bootstrap.min.css": os.path.join(css_dir, "bootstrap.min.css"),
    f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/js/bootstrap.bundle.min.js": os.path.join(js_dir, "bootstrap.bundle.min.js"),
}

# Download each file
for url, path in files.items():
    print(f"Downloading {url}...")
    r = requests.get(url)
    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"Saved to {path}")
    else:
        print(f"Failed to download {url}")
