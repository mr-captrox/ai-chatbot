import google.generativeai as genai
import os
import dotenv
from pathlib import Path

# Load .env
dotenv.load_dotenv(Path(__file__).parent / "backend" / ".env")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("GOOGLE_API_KEY not found")
else:
    genai.configure(api_key=api_key)
    try:
        print("Listing available models to models.txt...")
        with open("models.txt", "w") as f:
            for m in genai.list_models():
                f.write(f"Model: {m.name}, Methods: {m.supported_generation_methods}\n")
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
