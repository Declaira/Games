import sys
from pathlib import Path

def build_single_html(html_file, css_file, js_file, json_file, output_file):
    # Lire chaque fichier
    html_content = Path(html_file).read_text(encoding="utf-8")
    css_content = Path(css_file).read_text(encoding="utf-8")
    js_content = Path(js_file).read_text(encoding="utf-8")
    json_content = Path(json_file).read_text(encoding="utf-8")

    # Injecter CSS
    html_content = html_content.replace(
        "</head>",
        f"<style>\n{css_content}\n</style>\n</head>"
    )

    # Injecter JSON comme variable JS
    html_content = html_content.replace(
        "</body>",
        f"<script>\nconst data = {json_content};\n</script>\n</body>"
    )

    # Injecter JS (remplace fetch par variable locale)
    js_content = js_content.replace(
        "fetch(", 
        "// fetch remplacé\nPromise.resolve(data).then(data => {"
    ).replace(
        ".then(response => response.json())", 
        ""
    ).replace(
        ".then(data =>", 
        ""
    )

    html_content = html_content.replace(
        "</body>",
        f"<script>\n{js_content}\n</script>\n</body>"
    )

    # Sauvegarder
    Path(output_file).write_text(html_content, encoding="utf-8")
    print(f"✅ Fichier fusionné généré : {output_file}")

"""
if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python merge.py index.html style.css script.js data.json output.html")
    else:
        build_single_html(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
"""
inp = ["0", "index.html", "style.css", "script.js", "characters.json", "output.html"]
build_single_html(inp[1], inp[2], inp[3], inp[4], inp[5])