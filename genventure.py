from os import environ

import openai

openai.api_key = environ["API_KEY"]

response = openai.Image.create(
    prompt="Pixel art of a horse",
    n=1,
    size="1024x1024"
)
image_url = response['data'][0]['url']

print(image_url)