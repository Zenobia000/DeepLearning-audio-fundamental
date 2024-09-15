import streamlit as st
import glob
import json
from apple_podcast_scraper_api import save_transcript

st.title("Podcast Summaries")

# 使用者輸入 Podcast RSS URL 和 Episode ID
rss_url = st.sidebar.text_input("Podcast RSS URL", value="https://howofbusiness.libsyn.com/rss")
episode_id = st.sidebar.text_input("Episode ID", value="537")

# 按鈕觸發轉錄和下載摘要
button = st.sidebar.button("Download Episode Summary", on_click=save_transcript, args=(episode_id, rss_url))


def get_clean_time(start_ms):
    seconds = int((start_ms / 1000) % 60)
    minutes = int((start_ms / (1000 * 60)) % 60)
    hours = int((start_ms / (1000 * 60 * 60)) % 24)
    if hours > 0:
        start_t = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    else:
        start_t = f'{minutes:02d}:{seconds:02d}'
    return start_t


if button:
    # 顯示下載的集數資訊
    filename = episode_id + '_chapters.json'
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        chapters = data['chapters']
        episode_title = data['episode_title']
        thumbnail = data['thumbnail']
        podcast_title = data['podcast_title']
        audio = data['audio_url']

        st.header(f"{podcast_title} - {episode_title}")
        st.image(thumbnail, width=200)
        st.markdown(f'#### {episode_title}')
        
        # 展示章節摘要
        for chp in chapters:
            with st.expander(chp['gist'] + ' - ' + get_clean_time(chp['start'])):
                st.write(chp['summary'])

    except FileNotFoundError:
        st.error("未找到轉錄結果。請檢查 Episode ID 是否正確，或稍後再試。")
