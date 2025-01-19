#!/usr/bin/env python3
import requests
import base64


def main():
    # The URL of an image you want to test with
    img_url = "https://stardewvalleywiki.com/mediawiki/images/6/68/Main_Logo.png"

    # Fetch the image
    response = requests.get(img_url)
    response.raise_for_status()  # Raise an error if the fetch fails

    # Encode the image content to Base64
    base64_image = base64.b64encode(response.content).decode("utf-8")

    # Prepare the JSON payload matching your PromptInput schema
    payload = {"image": base64_image, "user_message": "What is shown in this image? Provide a short description."}

    # The URL of your local FastAPI endpoint
    endpoint_url = "http://127.0.0.1:5000/vision-screenshot-endpoint/"

    # Send the POST request (stream=True to handle streaming response)
    with requests.post(endpoint_url, json=payload, stream=True) as resp:
        resp.raise_for_status()

        print("Server response (streaming):")
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                # Decode bytes to string and print in real-time
                print(chunk.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
