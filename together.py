from together import Together
import os
from dotenv import load_dotenv

def initialize_together_client():
    load_dotenv()
    together_api_key = os.getenv("TOGETHER_API_KEY")
    return Together(api_key=together_api_key)
