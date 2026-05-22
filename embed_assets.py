import base64, re, json
from pathlib import Path

src  = Path("Harpagia Guide May20.html")
out  = Path("Harpagia Guide May20 embed.html")
html = src.read_text(encoding="utf-8")

# Collect unique filenames referenced in the HTML
names = sorted(set(re.findall(r'src="Assets/([^"]+)"', html)))

# Build data-URI map
uri_map = {}
for name in names:
    path = Path("Assets") / name
    if path.exists():
        data = base64.b64encode(path.read_bytes()).decode()
        uri_map[name] = f"data:image/png;base64,{data}"

# Replace every src="Assets/foo.png" with src="" data-embed="foo.png"
def replacer(m):
    name = m.group(1)
    if name in uri_map:
        return f'src="" data-embed="{name}"'
    return m.group(0)

html = re.sub(r'src="Assets/([^"]+)"', replacer, html)

# Build the loader script + data block
uri_json = json.dumps(uri_map)
loader = f"""<script>
(function(){{
  var D={uri_json};
  document.querySelectorAll('[data-embed]').forEach(function(el){{
    var k=el.getAttribute('data-embed');
    if(D[k])el.src=D[k];
  }});
}})();
</script>"""

# Inject just before </body>
html = html.replace("</body>", loader + "\n</body>")

out.write_text(html, encoding="utf-8")
print(f"Done. {len(uri_map)} unique images, output {out.stat().st_size/1024/1024:.2f} MB")
