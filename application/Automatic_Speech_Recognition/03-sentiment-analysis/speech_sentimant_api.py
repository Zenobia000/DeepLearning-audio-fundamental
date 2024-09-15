import requests
import json
import time

from dotenv import load_dotenv
import os

# 加載 .env 文件中的環境變數
load_dotenv()

# 從環境變數中讀取 API 金鑰
API_KEY_ASSEMBLYAI = os.getenv('ASSEMBLYAI_API_KEY')

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

headers = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

CHUNK_SIZE = 5_242_880  # 5MB


def upload(filename):
    def read_file(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint, headers=headers_auth_only, data=read_file(filename))
    return upload_response.json()['upload_url']


def transcribe(audio_url, sentiment_analysis):
    transcript_request = {
        'audio_url': audio_url,
        'sentiment_analysis': sentiment_analysis
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    return transcript_response.json()['id']

        
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()


def get_transcription_result_url(url, sentiment_analysis):
    transcribe_id = transcribe(url, sentiment_analysis)
    n = 0
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']
            
        print(f"{n}, waiting for 30 seconds")
        time.sleep(30)
        n += 1
        

def save_transcript(url, title, sentiment_analysis=False):
    data, error = get_transcription_result_url(url, sentiment_analysis)
    
    print(data)
    if data:
        # Save the text transcript
        transcript_filename = f"{title}_transcript.txt"

        with open(transcript_filename, 'w', encoding='utf-8') as f:
            f.write(data['text'])
        print(f'Transcript saved to {transcript_filename}')
        
        if sentiment_analysis:   
            # Save sentiment analysis results
            sentiment_filename = f"{title}_sentiments.json"

            with open(sentiment_filename, 'w', encoding='utf-8') as f:
                sentiments = data['sentiment_analysis_results']
                json.dump(sentiments, f, indent=4, ensure_ascii=False)
            print(f'Sentiment analysis results saved to {sentiment_filename}')
        
        return True
    elif error:
        print("Error!!!", error)
        return False