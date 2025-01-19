import requests
import json
import markdown2
import tempfile
import webbrowser


def main():
    url = "http://127.0.0.1:5000/generate-langchain-response-endpoint/"
    payload = {"user_message": "What is your name and what can you tell me about the Big Chest?"}

    # We'll collect all markdown pieces here so we can show a final rendered version later
    markdown_parts = []

    # 1) Stream the response in real time, print the events to console
    with requests.post(url, json=payload, stream=True) as response:
        response.raise_for_status()
        print("Streaming Markdown in real time...\n")

        for line in response.iter_lines(decode_unicode=True):
            print(f"Received line: {line}")

            if not line:
                # Skip empty lines
                continue

            # SSE lines come in the format: data: {"type":"...", "content":"..."}---END OF EVENT---
            if line.startswith("data: "):
                # Remove the "data: " prefix
                data_str = line[len("data: ") :]

                # Strip off the trailing marker ---END OF EVENT---
                data_str = data_str.replace("---END OF EVENT---", "").strip()

                try:
                    event = json.loads(data_str)
                    event_type = event.get("type")
                    content = event.get("content")

                    # Depending on event type, handle the content
                    if event_type == "onText":
                        print("MD Text:", content)
                        markdown_parts.append(content)

                    elif event_type == "onImageUrl":
                        md_image = f"![Image]({content})"
                        print("MD Image:", md_image)
                        markdown_parts.append(md_image)

                    else:
                        # onStart, onEnd, or other event types
                        print(f"{event_type}:", content)
                        # Optionally store them as well, if desired

                except json.JSONDecodeError:
                    print("Could not parse JSON from line:", data_str)

    # 2) After streaming finishes, combine everything into one Markdown string
    combined_markdown = "".join(markdown_parts)

    # 3) Convert that Markdown to HTML
    html_output = markdown2.markdown(combined_markdown)

    # 4) Write HTML to a temporary file and open it in the browser
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as temp_html:
        temp_html.write(html_output)
        temp_html_path = temp_html.name

    webbrowser.open(f"file://{temp_html_path}")
    print("\nDone! A rendered Markdown preview should now open in your browser.")


if __name__ == "__main__":
    main()
