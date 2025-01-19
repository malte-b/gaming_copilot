from pathlib import Path
from lxml import etree
import re 
import json

def clean_text(text):
    # Remove wiki markup brackets and their content
    text = re.sub(r'[\[\]{}|]', "", text)  # Remove brackets
    # Remove multiple single quotes (used for bold/italic in wiki markup)
    text = re.sub(r"''''*", "", text)
    # Remove leading }} if present
    text = re.sub(r"^}}\n*", "", text)
    return text.strip()


def xml_to_json_with_category(xml_file):
    tree = etree.parse(xml_file)
    root = tree.getroot()
    namespace = "{" + root.tag.split('}')[0].strip('{') + "}"
    
    page = root.find(f"{namespace}page")
    title = page.find(f"{namespace}title").text
    if "User:" in title or "Talk:" in title or "Template:" in title or "User talk:" in title or "Category:" in title or "File:" in title or "File talk:" in title:
        return
    revision = page.find(f"{namespace}revision")
    text_element = revision.find(f"{namespace}text")
    text = text_element.text if text_element is not None else ""
    
    # Extract category first
    category = None
    if not text:
        return
    if "#REDIRECT" in text:
        return
    if "[[Category:" in text:
        start = text.find("[[Category:") + len("[[Category:")
        end = text.find("]]", start)
        category = text[start:end]

    # Post-process text
    if "==History==" in text:
        text = text.split("==History==")[0]
    
    if "{{" in text and "}}" in text:
        text = text.split("}}", 1)[1]

    text = clean_text(text)
    return {
        "page_content": text.strip(),
        "metadata": {"title": title, "category": category}
    }

wiki_path = Path("wiki")
all_data = []

# Process all files and collect data into a single list
for file_path in wiki_path.glob("*"):
    result = xml_to_json_with_category(file_path)
    if result:
        all_data.append(result)

# Save all data into a single JSON file
output_file = Path("wiki_json.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)