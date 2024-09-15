import json
from yt_extractor import get_video_info, get_audio_url
from speech_sentimant_api import save_transcript
import re

def save_video_sentiments(url):
    video_info = get_video_info(url)
    url = get_audio_url(video_info)
    print(url)
    if url:
        title = video_info['title']
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'\s+', '_', title.strip())

        title = "data/" + title
        print(title)
        save_transcript(url, title, sentiment_analysis=True)
        return f"{title}_sentiments.json"
    return None

if __name__ == "__main__":
    file_path = save_video_sentiments("https://www.youtube.com/watch?v=WhzxsC-4wXM&t=52s")

    # if file_path:
    #     with open(file_path, "r") as f:
    #         data = json.load(f)

    # # with open("data/iPhone_13_Review:_Pros_and_Cons_sentiments.json", "r") as f:
    # #     data = json.load(f)
    
    # positives = []
    # negatives = []
    # neutrals = []
    # for result in data:
    #     text = result["text"]
    #     if result["sentiment"] == "POSITIVE":
    #         positives.append(text)
    #     elif result["sentiment"] == "NEGATIVE":
    #         negatives.append(text)
    #     else:
    #         neutrals.append(text)
        
    # n_pos = len(positives)
    # n_neg  = len(negatives)
    # n_neut = len(neutrals)

    # print("Num positives:", n_pos)
    # print("Num negatives:", n_neg)
    # print("Num neutrals:", n_neut)

    # # ignore neutrals here
    # r = n_pos / (n_pos + n_neg)
    # print(f"Positive ratio: {r:.3f}")

