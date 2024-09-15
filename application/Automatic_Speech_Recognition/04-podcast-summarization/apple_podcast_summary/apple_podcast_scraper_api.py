import requests
import json
import time
import feedparser
from dotenv import load_dotenv
import os
import pprint

# 加載環境變數
load_dotenv()

# 從環境變數中讀取 API 金鑰
API_KEY_ASSEMBLYAI = os.getenv('ASSEMBLYAI_API_KEY')
API_KEY_LISTENNOTES = os.getenv('LISTENNOTES_API_KEY')

# AssemblyAI API 設定
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'
headers_assemblyai = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

# Get episode info from RSS feed (替代 listennotes API)
def get_episode_audio_url(rss_url, episode_number=None, episode_title=None):
    # 解析 RSS feed
    podcast_feed = feedparser.parse(rss_url)

    # 檢查 RSS 解析是否成功
    if podcast_feed.bozo:
        print("無法解析 RSS feed，請確認 URL 是否正確。")
        return None, None, None, None
    
    # 取得 Podcast 的標題和縮略圖
    podcast_title = podcast_feed.feed.title if 'title' in podcast_feed.feed else '未知的 Podcast 標題'
    thumbnail = podcast_feed.feed.get('image', {}).get('url', '無法取得縮略圖')

    # 遍歷所有集數，並根據使用者輸入的集數號碼或標題進行篩選
    for item in podcast_feed.entries:
        if episode_number is not None and str(episode_number) in item.title:
            # 取得集數資訊
            episode_title = item.title
            audio_url = next((link['href'] for link in item.links if link['type'] == 'audio/mpeg'), '無法取得音訊 URL')
            return audio_url, thumbnail, podcast_title, episode_title
        
        if episode_title is not None and episode_title.lower() in item.title.lower():
            # 取得集數資訊
            episode_title = item.title
            audio_url = next((link['href'] for link in item.links if link['type'] == 'audio/mpeg'), '無法取得音訊 URL')
            return audio_url, thumbnail, podcast_title, episode_title
    
    print("未找到符合條件的集數。")
    return None, None, None, None


# 使用 AssemblyAI 轉錄音訊
def transcribe(audio_url, auto_chapters):
    transcript_request = {
        'audio_url': audio_url,
        'auto_chapters': auto_chapters
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers_assemblyai)
    pprint.pprint(transcript_response.json())
    return transcript_response.json()['id']


# 輪詢 AssemblyAI 以獲取轉錄結果
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers_assemblyai)
    return polling_response.json()
    

# 從 AssemblyAI 獲取轉錄結果
def get_transcription_result_url(url, auto_chapters):
    transcribe_id = transcribe(url, auto_chapters)
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']

        print("等待 60 秒...")
        time.sleep(60)
            

# 儲存轉錄結果
def save_transcript(episode_id, rss_url):
    audio_url, thumbnail, podcast_title, episode_title = get_episode_audio_url(rss_url, episode_number=episode_id)
    
    if not audio_url:
        print(f"無法找到集數: {episode_id}")
        return False
    
    data, error = get_transcription_result_url(audio_url, auto_chapters=True)
    
    if data:
        # 儲存轉錄文字檔案
        filename = episode_id + '.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])

        # 儲存章節資訊
        filename = episode_id + '_chapters.json'
        with open(filename, 'w') as f:
            chapters = data.get('chapters', [])
            data = {
                'chapters': chapters,
                'audio_url': audio_url,
                'thumbnail': thumbnail,
                'podcast_title': podcast_title,
                'episode_title': episode_title
            }
            json.dump(data, f, indent=4)
            print('轉錄結果已儲存')
            return True
    elif error:
        print("發生錯誤!!!", error)
        return False

if __name__ == "__main__":
    # 使用者輸入測試
    rss_url = "https://howofbusiness.libsyn.com/rss"
    episode_id = "537"
    save_transcript(episode_id, rss_url)
