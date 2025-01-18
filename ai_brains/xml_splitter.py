from lxml import etree
import os


def split_xml_into_single_page_files(file_path, output_dir):
    """
    Splits an XML file into multiple files, each containing a single <page> element.

    :param file_path: Path to the large XML file.
    :param output_dir: Directory where the split files will be saved.
    """
    # Namespace used in the XML file
    ns = {"": "http://www.mediawiki.org/xml/export-0.11/"}
    context = etree.iterparse(file_path, events=("start", "end"), tag=f"{{{ns['']}}}page")
    file_prefix = "page"
    file_index = 1

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for event, element in context:
        if event == "end" and element.tag.endswith("page"):
            # Generate file name
            file_name = f"{file_prefix}_{file_index}.xml"
            file_path = os.path.join(output_dir, file_name)

            # Write the current <page> to a file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" '
                        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                        'xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.11/ '
                        'http://www.mediawiki.org/xml/export-0.11.xsd" '
                        'version="0.11" xml:lang="en">\n')
                f.write(etree.tostring(element, pretty_print=True, encoding="utf-8").decode("utf-8"))
                f.write("\n</mediawiki>")

            print(f"Written file: {file_path}")
            file_index += 1

            # Clear element to free memory
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]

    print(f"Splitting complete. Total files created: {file_index - 1}")

# Example usage
file_path = "data/stardewvalleywikicom_mediawiki-20250118-current.xml"
output_dir = "wiki"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

split_xml_into_single_page_files(file_path, output_dir)
