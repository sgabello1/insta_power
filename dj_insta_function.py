from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import subprocess
from insta_functions import pimp_with_ai, download_youtube_short, add_captions_with_voice, story_from_article
import os

UPLOAD_FOLDER = 'processed_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def apply_filter(input_file):
    output_file = input_file.replace(".mp4", "_filtered.mp4")
    command = [
        "ffmpeg", "-i", input_file, "-vf",
        "eq=contrast=1.2:brightness=0.1:saturation=1.1, colorbalance=rm=0.09:gm=0.08:bm=-0.1, curves=m='0/0 0.35/0.25 0.7/0.85 1/1', colortemperature=6000, unsharp=3:3:0.5",
        "-c:a", "copy", output_file
    ]
    subprocess.run(command, check=True)
    return output_file

@csrf_exempt
def process_video(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url')
        num_of_words = data.get('num_of_words', 100)
        adapt = data.get('adapt', False)
        captions = data.get('captions', False)
        apply_filter_option = data.get('apply_filter', False)
        voice_over_text = data.get('voice_over_text', "")
        text_font = int(data.get('text_font', 60))

        if not url:
            return JsonResponse({"error": "YouTube URL is required"}, status=400)

        try:
            video_path, video_description, description = download_youtube_short(url)

            if captions:
                output_video = add_captions_with_voice(video_path, voice_over_text, adapt, text_font)
            else:
                output_video = video_path
                pimped_text = pimp_with_ai(video_description, num_of_words)
            
            if apply_filter_option:
                output_video = apply_filter(output_video)

            return JsonResponse({
                "video_url": f"/{UPLOAD_FOLDER}/{os.path.basename(output_video)}",
                "description": description
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def process_article(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        article_url = data.get('article_url')
        word_limit = int(data.get('word_limit', 100))

        if not article_url:
            return JsonResponse({"error": "Article URL is required"}, status=400)

        try:
            title, summary, full_text = story_from_article(article_url, word_limit)
            return JsonResponse({"title": title, "summary": summary})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def index(request):
    return render(request, 'index.html')
