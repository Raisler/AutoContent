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

def extract_audio(input_path, output_path):
    ffmpeg_command = f'ffmpeg -i "{input_path}" -map a -c:a libmp3lame -b:a 192k "{output_path}"'
    run_command(ffmpeg_command)

