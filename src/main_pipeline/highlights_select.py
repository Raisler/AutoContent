import json 

with open('./demo_files/gemini_prompt_result_pt.json', 'r') as f:
    my_file = json.load(f)

def highlights_select_demo():
    return my_file

import subprocess
def run_command(command):
    try:
        # Run the command and wait for it to finish
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        
        # Print the command's output and errors
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)

        # Check if command was successful
        if result.returncode == 0:
            print("Command executed successfully.")
        else:
            print(f"Command failed with return code {result.returncode}")
    except Exception as e:
        print(f"An error occurred: {e}")

api_key = "from dotenv"

def run_gemini_curl():
    f"""curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: {api_key} \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Just say yes"
          }
        ]
      }
    ]
  }'"""