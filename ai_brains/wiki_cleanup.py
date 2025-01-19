import mwxml
import json
import re
import mwparserfromhell

EXCLUDED_NAMESPACES = {
    "User:",
    "Talk:",
    "Template:",
    "User talk:",
    "Category:",
    "File:",
    "File talk:",
    ".png",
    ".PNG",
    ".css",
    "/doc",
    "SMAPI",
    "Migrate to Stardew Valley",
    "Modding",
    "Infobox",
    "images",
}

def clean_wiki_text(text):
    if not text:
        return ""
    
    # Remove history section
    text = re.sub(r"==History==.*?{{NavboxFurniture}}", "", text, flags=re.DOTALL)
    # Remove translations and tags
    text = re.sub(r"\[\[.*?:.*?\]\]", "", text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Parse wiki text
    wikicode = mwparserfromhell.parse(text)
    
    # Strip wiki markup and get plain text
    text = wikicode.strip_code()

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    if text.endswith('History'):
        return text[:-len('History')].rstrip()

    return text.strip()

def extract_wiki_data(dump_file):
    entries = []
    # Load and parse the XML dump
    dump = mwxml.Dump.from_file(open(dump_file, 'rb'))
    
    # Iterate through pages
    for page in dump:
        # Get the latest revision
        revision = next(page)
        
        # Extract and clean text
        raw_text = revision.text or ""
        if raw_text == "":
            continue
        if "#REDIRECT" in raw_text:
            continue
        if any(namespace in page.title for namespace in EXCLUDED_NAMESPACES):            
            continue
            
        clean_text = clean_wiki_text(raw_text)
        if re.match(r'^[^a-zA-Z0-9\s]+$', clean_text):
            continue
        
        # Parse categories using regex
        cats = re.findall(r'\[\[Category:([^\]]+)\]\]', raw_text)
        categories = [cat.strip() for cat in cats] if cats else []
        
        # Create entry
        entry = {
            'page_content': clean_text,
            'metadata': {
                'title': page.title,
                'categories': categories
            },
        }
        entries.append(entry)
    
    # Write all entries to JSON file
    with open("cleaned_stardew_wiki.json", 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=4)

# Usage example
dump_file = "data/stardewvalleywikicom_mediawiki-20250118-current.xml"
extract_wiki_data(dump_file)
