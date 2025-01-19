import os
from mistralai import Mistral
from dotenv import load_dotenv
import base64
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
model = "pixtral-large-latest"
client = Mistral(api_key=api_key)

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

img_path = "images/A-screenshot-from-Stardew-Valley-showing-the-players-farm-inventory-and-avatar.png"
base64_image = encode_image(img_path)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": """
                    Additional information: 
                    The current season is indicated by the symbol in the top right of the image.
                    - Pink flower: Spring
                    - Boat: Summer
                    - Leaf: Fall
                    - Winterberry: Winter
                    Only answer the question.
                    What can I buy right now to make the most money?
                    """
            },
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_image}" 
            }
        ]
    }
]

chat_response = client.chat.complete(
    model=model,
    messages=messages
)

print(chat_response.choices[0].message.content)
