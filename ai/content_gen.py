import openai
import config

class AIContentGenerator:
    def __init__(self):
        openai.api_key = config.OPENAI_KEY

    def generate_assets(self, data):
        prompt = f"Create a viral TikTok script for {data['title']} priced at ${data['suggested_price']}"
        res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return res.choices[0].message.content
class AIContentGenerator:
    # ... (הקוד הקיים) ...
    
    def generate_image_prompt(self, product_title):
        """שדרוג 2: יצירת פקודה לתמונת פרסום מקצועית"""
        return f"High-end commercial photography of {product_title}, cinematic lighting, studio background, 8k resolution, professional product shot."
