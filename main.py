import json
from openai import OpenAI

with open("config.json", "r") as file:
    config = json.load(file)

client = OpenAI(
    api_key=config["OPENAI_API_KEY"]
)

response = client.responses.create(
    model="gpt-5.6-luna",
    input="Say hello in one sentence."
)

print(response.output_text)