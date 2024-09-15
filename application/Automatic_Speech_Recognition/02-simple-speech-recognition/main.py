import os
import requests
from transcribe_api import upload, save_transcript

# Use relative path

current_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(current_dir, "transcribe", "elon_learning_methos_audio.mp3")

print(filename)

try:
    print(f"Uploading file: {filename}")
    audio_url = upload(filename)

    print(f"File uploaded successfully, URL: {audio_url}")

    print("Starting transcription...")
    output_filename = os.path.join(current_dir, "elon_learning_methods")
    save_transcript(audio_url, output_filename)
    print("Transcription process completed")

except FileNotFoundError:
    print(f"Error: File not found {filename}")
except requests.exceptions.RequestException as e:
    print(f"Network request error: {str(e)}")
    print(f"Error details: {e.response.text if e.response else 'No response'}")
except Exception as e:
    print(f"An unknown error occurred: {str(e)}")

print("Program execution completed")

