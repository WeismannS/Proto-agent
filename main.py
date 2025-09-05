from pyexpat.errors import messages
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

def main(api_key : str, verbose : bool = False) :
    prompt = sys.argv[1]
    messages = [types.Content(role="user",parts=[types.Part(text=prompt)])]
    gemini_client = genai.Client(api_key=api_key)

    response = gemini_client.models.generate_content(model="gemini-2.0-flash-001",contents=messages)

    print(response.text)
    if (verbose and response.usage_metadata) :
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__" :
    verbose = False
    if (length := len(sys.argv)) == 1 :
        print("Please provide a valid prompt!")
        exit(1)
    elif length == 3 and sys.argv[2] == '--verbose' :
        verbose = True
    elif length == 2 :
        pass
    else :
        print("Please provide a single prompt and an optional --verbose")
        exit(1)
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None :
        raise Exception("Please provide an api key in your .env")
    main(api_key, verbose)
    