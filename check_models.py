import google.generativeai as genai
import os

# Use the hardcoded key
api_key = "AIzaSyDvSdRKARV2s0-1p25jBsuQCmQcewNZI84"

genai.configure(api_key=api_key)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
