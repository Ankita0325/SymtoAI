# test_groq.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
print(f"API Key: {api_key[:15] if api_key else 'None'}...")

if api_key and api_key.startswith('gsk_'):
    print("✅ Valid Groq API key format!")
    
    try:
        client = Groq(api_key=api_key)
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'API is working!'"}
            ],
            temperature=0.7,
            max_tokens=100,
        )
        
        print(f"✅ SUCCESS! Response: {completion.choices[0].message.content}")
        print("🎉 Your Groq API is working perfectly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Invalid API key format. Must start with 'gsk_'")