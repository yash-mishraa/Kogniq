import os

def check_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("GEMINI_API_KEY is NOT set.")
        return
        
    print(f"Key is set. Length: {len(key)}")
    print(f"Starts with: {key[:4]}")
    print(f"Ends with: {key[-4:]}")
    
    if " " in key:
        print("WARNING: Key contains spaces!")
        
    if key.startswith('"') or key.startswith("'"):
        print("WARNING: Key starts with a quote character!")
        
    if key.endswith('"') or key.endswith("'"):
        print("WARNING: Key ends with a quote character!")
        
    if key == "your-actual-key-here" or key == "your-actual-api-key":
        print("WARNING: Key is literally the placeholder text!")

if __name__ == "__main__":
    check_key()
