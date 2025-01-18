from lxml import etree
import re 

def clean_text(text):
    # Remove wiki markup brackets and their content
    text = re.sub(r'[\[\]{}]', "", text)  # Remove brackets
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
    revision = page.find(f"{namespace}revision")
    text_element = revision.find(f"{namespace}text")
    text = text_element.text if text_element is not None else ""
    
    # Extract category first
    category = None
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
    print({
        "page_content": text.strip(),
        "metadata": {"title": title, "category": category}
    })
    return {
        "page_content": text.strip(),
        "metadata": {"title": title, "category": category}
    }

xml_to_json_with_category("wiki/page_5.xml")