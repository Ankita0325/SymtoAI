# test_env.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Check if .env exists
env_path = Path('.env')
print(f".env exists: {env_path.exists()}")

if env_path.exists():
    # Read and display content
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f".env content:\n{content}")
    
    # Load .env
    load_dotenv(env_path)
    
    # Check if key is loaded
    api_key = os.getenv('GROQ_API_KEY')
    print(f"GROQ_API_KEY from os.getenv: {api_key}")
    
    if api_key:
        print(f"✅ API Key found: {api_key[:15]}...")
    else:
        print("❌ API Key not found in environment")
        
        # Try loading with explicit encoding
        print("\nTrying with explicit encoding...")
        load_dotenv(env_path, encoding='utf-8-sig')
        api_key = os.getenv('GROQ_API_KEY')
        print(f"GROQ_API_KEY: {api_key}")
        
        if not api_key:
            # Try reading directly from file
            print("\nReading directly from file...")
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('GROQ_API_KEY='):
                        key = line.split('=')[1].strip()
                        print(f"Found in file: {key}")
                        # Set it manually
                        os.environ['GROQ_API_KEY'] = key
                        api_key = key
                        break
    
    if api_key:
        print(f"✅ API Key loaded: {api_key[:15]}...")
        
        # Test Groq
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            print("✅ Groq client created!")
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say 'Hello!'"}],
                temperature=0.7,
                max_tokens=20,
            )
            print(f"✅ API Response: {completion.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Still no API key found")
else:
    print("❌ .env file not found!")