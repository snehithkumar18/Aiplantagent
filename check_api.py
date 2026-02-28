#!/usr/bin/env python3
"""
Quick script to check API key configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("API Key Configuration Check")
print("=" * 50)

groq_key = os.getenv("GROQ_API_KEY")
hf_key = os.getenv("HUGGINGFACE_API_KEY")
weather_key = os.getenv("OPENWEATHER_API_KEY")

print(f"\nGROQ_API_KEY: {'[OK] SET' if groq_key and groq_key != 'your_groq_key_here' else '[X] NOT SET or placeholder'}")
if groq_key:
    print(f"  Value: {groq_key[:20]}..." if len(groq_key) > 20 else f"  Value: {groq_key}")

print(f"\nHUGGINGFACE_API_KEY: {'[OK] SET' if hf_key and hf_key != 'your_hf_token_here' else '[X] NOT SET or placeholder'}")
if hf_key:
    print(f"  Value: {hf_key[:20]}..." if len(hf_key) > 20 else f"  Value: {hf_key}")

print(f"\nOPENWEATHER_API_KEY: {'[OK] SET' if weather_key and weather_key != 'your_openweather_key_here' else '[X] NOT SET or placeholder'}")
if weather_key:
    print(f"  Value: {weather_key[:20]}..." if len(weather_key) > 20 else f"  Value: {weather_key}")

print("\n" + "=" * 50)
print("IMPORTANT: For translation to work, GROQ_API_KEY must be set!")
print("Create a .env file in the project root with:")
print("GROQ_API_KEY=your_actual_api_key_here")
print("=" * 50)

