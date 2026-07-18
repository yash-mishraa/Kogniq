import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Ensure we can import from packages
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "learning-content" / "src"))

from learning_content.providers.openrouter import OpenRouterTextGenerationProvider


def run_demo() -> None:
    print("=" * 60)
    print("OpenRouter Text Generation Provider Demo")
    print("=" * 60)

    # Load environment variables
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable not found.")
        print("Please set it in your .env file.")
        sys.exit(1)

    # Note: Llama 3.1 8B is a good, fast default model for testing
    model_name = "meta-llama/llama-3.1-8b-instruct"

    print("\n[1] Initializing provider (lazy load)...")
    provider = OpenRouterTextGenerationProvider(
        api_key=api_key,
        model_name=model_name,
    )

    print(f"Provider: {provider.info.provider_name}")
    print(f"Model: {provider.info.default_model}")
    print(f"Context Window: {provider.info.context_window} tokens")

    prompt = "Explain recursion in two sentences."
    print("\n[2] Generating response...")
    print(f"Prompt: {prompt}")
    print(f"Prompt Length: {len(prompt)} characters")

    start_time = time.time()
    try:
        response = provider.generate(prompt, temperature=0.3, max_tokens=100)
        end_time = time.time()

        latency = end_time - start_time

        print("\n[3] Generation Complete!")
        print(f"Latency: {latency:.2f} seconds")
        print(f"Response Length: {len(response)} characters")
        print("Estimated Cost: $0.000 (Placeholder)")
        print("Finish Reason: stop (Placeholder)\n")

        print("-" * 40)
        print("First 300 characters of response:")
        print("-" * 40)
        print(response[:300] + ("..." if len(response) > 300 else ""))
        print("-" * 40)

    except Exception as e:
        print(f"\nERROR during generation: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_demo()
