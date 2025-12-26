import openai
import config

class AIContentGenerator:
    def __init__(self):
        openai.api_key = config.OPENAI_KEY

    def generate_assets(self, data):
        prompt = f"Create a viral TikTok script for {data['title']} priced at ${data['suggested_price']}"
        res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return res.choices[0].message.content
