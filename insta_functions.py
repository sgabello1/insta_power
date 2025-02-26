import nltk
from urllib.parse import urljoin
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import openai
from pytube import YouTube
import subprocess
import numpy as np
import requests
import re
import textwrap
import random
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip,CompositeAudioClip,  AudioFileClip, concatenate_audioclips
from gtts import gTTS
import yt_dlp
import sys
from moviepy.video.fx.all import fadein, resize
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

image_width = 300
image_height = 300


from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from PIL import Image
from io import BytesIO

def extract_images(soup, url, W, H):
    """
    Extracts images from the provided BeautifulSoup object, prioritizing those with captions or meaningful alt text.
    Automatically converts WebP images to PNG format.

    :param soup: BeautifulSoup object of the parsed HTML content
    :param url: Base URL of the article for resolving relative image URLs
    :param W: Minimum width of the image
    :param H: Minimum height of the image
    :return: List of PIL Image objects (converted to PNG if in WebP format)
    """
    images = []

    def download_and_convert_image(img_url):
        """Downloads an image and converts it to PNG if necessary."""
        try:
            img_response = requests.get(img_url, stream=True)
            img_response.raise_for_status()
            img = Image.open(BytesIO(img_response.content))

            # Convert WebP to PNG if needed
            if img.format == 'WEBP':
                img = img.convert("RGBA")  # Ensure compatibility
                print(f"Converted WebP to PNG: {img_url}")

            # Check dimensions
            if img.width > W and img.height > H:
                return img
        except Exception as e:
            print(f"Error downloading or converting image: {e}")
        return None

    # 1. Look for images with captions
    captions = soup.find_all(["figcaption", "div", "span"], class_=lambda c: c and "caption" in c.lower())
    for caption in captions:
        parent = caption.find_parent()
        img_tag = parent.find("img") if parent else None
        if not img_tag:
            img_tag = caption.find_previous_sibling("img") or caption.find_next_sibling("img")
        
        if img_tag and img_tag.get("src"):
            img_url = urljoin(url, img_tag["src"])
            img = download_and_convert_image(img_url)
            if img:
                images.append(img)
                print(f"Image with caption downloaded: {img_url}")
                #return images  # Prioritize the first image with a caption

    # 2. Look for images with meaningful "alt" attributes
    for img_tag in soup.find_all("img"):
        img_alt = img_tag.get("alt", "").strip()
        if img_alt and len(img_alt) > 5:
            img_url = urljoin(url, img_tag.get("src"))
            img = download_and_convert_image(img_url)
            if img:
                images.append(img)
                print(f"Image with alt text downloaded: {img_url} (Alt: {img_alt})")
                #return images  # Prioritize the first image with meaningful alt text

    # 3. Fallback: Try to find the first large image in the article content
    try:
        article_body = soup.find(["article", "div"], class_=lambda c: c and "content" in c.lower() or "article" in c.lower())
        if article_body:
            for img_tag in article_body.find_all("img"):
                img_url = img_tag.get("src")
                if not img_url:
                    continue
                img_url = urljoin(url, img_url)
                img = download_and_convert_image(img_url)
                if img:
                    images.append(img)
                    print(f"Fallback article image downloaded: {img_url}")
                    #return images
    except Exception as e:
        print(f"Error processing: {e}")

    # 4. Final fallback: General image extraction
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if not img_url:
            continue
        img_url = urljoin(url, img_url)
        img = download_and_convert_image(img_url)
        if img:
            images.append(img)
            print(f"Generic fallback image downloaded: {img_url}")
    if images != None:
        return images
    else:
        return None



def extract_videos(soup, url):
    """
    Extracts video URLs from the provided BeautifulSoup object.
    
    :param soup: BeautifulSoup object of the parsed HTML content
    :param url: Base URL of the article for resolving relative video URLs
    :return: List of video file URLs
    """
    video_urls = []

    # Search for <video> tags with source elements
    for video_tag in soup.find_all("video"):
        sources = video_tag.find_all("source")
        for source in sources:
            video_url = source.get("src")
            if video_url:
                video_urls.append(urljoin(url, video_url))

    # Search for direct <video> tags with a src attribute
    for video_tag in soup.find_all("video", src=True):
        video_url = video_tag.get("src")
        if video_url:
            video_urls.append(urljoin(url, video_url))

    # Search for embedded video links (e.g., <iframe>)
    for iframe_tag in soup.find_all("iframe"):
        video_url = iframe_tag.get("src")
        if video_url and ("youtube.com" in video_url or "vimeo.com" in video_url):
            video_urls.append(urljoin(url, video_url))

    return video_urls


def download_article_content(url,yes_img,yes_video):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
 
    try:
        # Fetch the article
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the title of the article
        title = soup.title.string if soup.title else "Untitled"
        
        # Extract the article text
        paragraphs = soup.find_all('p')
        article_text = " ".join(p.get_text() for p in paragraphs)

        # Summarize the text using OpenAI
        prompt = f"You are working for a famous Marketing agency and your role is to post incredible contents on Instagram. Your job is to take articles online and with your creativity extrapolate the best information and summarize them into minimum of 1000 to a maximum of 2000 characters, according to the lenght of the article. Summarize the following article in 5 sentences and make it catchy. After the text, add 2 return rows (to make the text well readable) then add 20 trendy hashtag that are relevant to the post. Then just created put two return lines to separate the text and improve readability. Finish with always the same sentence: Follow me for incredible china.robotics !!:\n\n{article_text}"
    
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
                temperature=0.7
            )
            summary_text = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            raise Exception(f"OpenAI API request failed: {e}")

        # Get a better title
        prompt2 = f"Find a great catchy title for this article, very short, max 5 words and impactful. Write with passion and excitment. NEVER put quotation marks. \n\n{article_text}"
    
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt2}
            ],
                temperature=0.7
            )
            title = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            raise Exception(f"OpenAI API request n2 failed: {e}")

        # Extract images and videos
        if yes_img == "True":
            images = extract_images(soup, url,image_width,image_height)
        else:
            images = None
        if yes_video == "True":
            videos = extract_videos(soup, url)
        else:
            videos = None

        return title, summary_text, images, videos

    except Exception as e:
        print(f"Error fetching article: {e}")
        return None, None, None, None


import os
from pytube import YouTube

def download_and_convert_video(video_url):
    try:
        # Ensure the output directory exists
        output_dir = "temp_video"
        os.makedirs(output_dir, exist_ok=True)

        # Set the output template for yt-dlp
        output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

        # Download the video using yt-dlp
        print("Downloading video with yt-dlp...")
        subprocess.run(["yt-dlp", "-o", output_template, video_url], check=True)

        # Find the downloaded video file
        downloaded_files = [f for f in os.listdir(output_dir) if not f.endswith(".mp4")]
        if not downloaded_files:
            print("No video files found after download.")
            return None

        # Assume the first downloaded file is the target
        video_path = os.path.join(output_dir, downloaded_files[0])
        mp4_path = os.path.splitext(video_path)[0] + ".mp4"

        # Convert to MP4 using ffmpeg
        print(f"Converting {video_path} to MP4...")
        subprocess.run(["ffmpeg", "-i", video_path, "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", "-b:a", "128k", mp4_path], check=True)

        # Remove the original file if conversion is successful
        if os.path.exists(mp4_path):
            os.remove(video_path)
            print(f"Video successfully converted to MP4: {mp4_path}")
            return mp4_path
        else:
            print("MP4 conversion failed.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error during video processing: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    
# Function to crop the image to 1080x1080 centered
def crop_to_square(image, size=1080):
    width, height = image.size
    if width > height:
        left = (width - height) // 2
        top = 0
        right = left + height
        bottom = height
    else:
        left = 0
        top = (height - width) // 2
        right = width
        bottom = top + width

    return image.crop((left, top, right, bottom)).resize((size, size), Image.LANCZOS)


def find_least_crowded_area(image):
    """
    Finds the least crowded area in an image, limiting to three possible vertical bands: top, center, or bottom.
    """
    # Convert image to grayscale and apply a blur to smooth details
    gray_image = image.convert("L").filter(ImageFilter.GaussianBlur(5))
    img_array = np.array(gray_image)

    # Calculate edge density using gradients
    grad_y, grad_x = np.gradient(img_array)
    edge_density = np.abs(grad_x) + np.abs(grad_y)

    # Get image dimensions
    h, w = img_array.shape

    # Define the vertical bands
    bands = {
        "top": (0, h // 3),
        "center": (h // 3, 2 * h // 3),
        "bottom": (2 * h // 3, h),
    }

    # Calculate the average edge density for each band
    band_densities = {}
    for band_name, (start_y, end_y) in bands.items():
        band = edge_density[start_y:end_y, :]
        band_densities[band_name] = np.mean(band)

    # Find the band with the lowest density
    least_crowded_band = min(band_densities, key=band_densities.get)

    # Calculate the center of the selected band
    start_y, end_y = bands[least_crowded_band]
    y = (start_y + end_y) // 2
    x = w // 2  # Center horizontally

    print(f"Selected area: {least_crowded_band} (x: {x}, y: {y})")
    return x, y



from random import choice

def load_random_font(font_folder):
    # Get a list of font files from the specified folder
    font_files = [f for f in os.listdir(font_folder) if f.endswith('.ttf')]
    if not font_files:
        raise Exception("No font files found in the folder.")
    # Select a random font file
    return choice(font_files)

def closest_color(color, palette):
    return min(palette.values(), key=lambda c: sum((sc - pc) ** 2 for sc, pc in zip(color, c)))

def calculate_luminance(color):
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]

def title_image_one(image, title, position):
    try:
        img = crop_to_square(image).convert("RGBA")
        draw = ImageDraw.Draw(img)
        font_path = os.path.join("/home/gabriele.ermacora/Documents/robbba_mea/cr-insta/fonts", load_random_font("./fonts"))
        base_font_size = 70
        font = ImageFont.truetype(font_path, base_font_size)
        
        # Fixed text box size
        box_width, box_height = 1040, 180
        max_width = box_width - 10  # Padding for better centering
        
        # Adjust font size and wrap text to fit the fixed text box
        while True:
            wrapped_text = textwrap.fill(title, width=50)  # Wrapping text to fit the box
            bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            
            if text_width <= max_width and text_height <= box_height:
                break  # Stop adjusting if it fits
            
            base_font_size -= 2
            if base_font_size <= 10:  # Prevent font from being too small
                break
            font = ImageFont.truetype(font_path, base_font_size)
        
        # Ensure the text box is centered either at the top or bottom
        img_width, img_height = img.size
        if position == "top":
            x, y = img_width // 2, box_height // 2 + 20
        else:  # "bottom"
            x, y = img_width // 2, img_height - box_height // 2 - 20
        
        # Determine background color dynamically
        text_bg_coords = [
            (x - box_width // 2, y - box_height // 2),
            (x + box_width // 2, y + box_height // 2),
        ]
        cropped_region = img.crop(
            (
                max(0, text_bg_coords[0][0]),
                max(0, text_bg_coords[0][1]),
                min(img.size[0], text_bg_coords[1][0]),
                min(img.size[1], text_bg_coords[1][1]),
            )
        )
        avg_color = np.array(cropped_region.resize((1, 1)).getpixel((0, 0)))
        avg_luminance = calculate_luminance(avg_color)

        # Define limited color choices
        defined_colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            #"red": (255, 0, 0),
            #"yellow": (255, 255, 0),
            #"blue": (0, 0, 255),
        }
        
        # Get the best matching color
        chosen_color = closest_color(avg_color[:3], defined_colors)

        # Apply transparency
        bg_color = (*chosen_color, 150)
        
        # Transparent background rectangle
        transparent_bg = Image.new("RGBA", img.size, (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(transparent_bg)
        
        # Draw transparent rectangle
        bg_draw.rectangle([
            (x - box_width // 2, y - box_height // 2),
            (x + box_width // 2, y + box_height // 2)
        ], fill=bg_color)
        
        # Composite the transparent background onto the original image
        img = Image.alpha_composite(img, transparent_bg)
        draw = ImageDraw.Draw(img)
        
        # Set text color to contrast with background
        text_color = (255, 255, 255, 255) if avg_luminance < 128 else (0, 0, 0, 255)
        
        # Draw text centered in the box
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        draw.multiline_text((text_x, text_y), wrapped_text, fill=text_color, font=font, align="center")
        
        return img
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    

def story_from_article(url,number):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    }

    try:
        # Fetch the article
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the title of the article
        title = soup.title.string if soup.title else "Untitled"
        
        # Extract the article text
        paragraphs = soup.find_all('p')
        article_text = " ".join(p.get_text() for p in paragraphs)

        # Constructing an advanced prompt with structure
        prompt = (
            f"Article content:\n{article_text}"
            f"**Find me:why is this article interesting?Identify key elements that evoke emotions and make the reader engaged.Why should the reader care?**\n"
            f"**Add some shocking fact based on the data from the same article or drama to make the story more interesting and gripping. Underline how the proposed solution make it as an improvement to the problem you just stated**\n"
            f"Deliver a concise but powerful summary, written with very easy words, stating the problem first and then the solution, in max {number} words of the article written with the sytle of the famous copywriter Tim Denning.\n\n"
            f"Provide a well-researched list of at least 29 hashtags to maximize reach. Write them one after the other dont add numbers or lists.\n\n"
            f"Now keep only the last two answers combined and add at end the sentence FOLLOW ME FOR INCREDIBLE CHINA.ROBOTICS!!!"            
        )
    
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # Use the latest model
                messages=[
                    {"role": "system", "content": "You are an expert content strategist and social media marketer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0
            )
            summary_text = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            raise Exception(f"OpenAI API request failed: {e}")

        return title, summary_text, article_text

    except Exception as e:
        print(f"Error fetching article: {e}")
        return None, None, None

def pimp_with_ai(text, words_number):
    # Constructing an advanced prompt with structure
    prompt = (f"Article content:\n{text}"
        f"**Find me:why is this video description is interesting?Identify key elements that evoke emotions and make the reader engaged.Why should the reader care?**\n"
        f"**Add some shocking fact based on the data from Internet or your knowledge related to China, innovation, robotics and AI or drama to make the story more interesting and gripping. Underline how the proposed solution make it as an improvement to the problem you just stated**\n"
        f"Deliver a concise but powerful summary, written with very easy words, stating the problem first and then the solution, in max {words_number} words of the article written with the sytle of the famous copywriter Tim Denning.\n\n"
        f"Provide a well-researched list of at least 29 hashtags to maximize reach. Write them one after the other dont add numbers or lists.\n\n"
        f"Now keep only the last two answers combined and add at end the sentence '\n\n FOLLOW ME FOR INCREDIBLE CHINA.ROBOTICS!!!'" )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Use the latest model
            messages=[
                {"role": "system", "content": "You are an expert content strategist and social media marketer."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0
        )
        text_pimped = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        raise Exception(f"OpenAI API request failed: {e}")


    return text_pimped

def ensure_output_folder(folder="captioned video for gabriele"):
    if not os.path.exists(folder):
        os.makedirs(folder)

def split_text_into_sentences(text):
    sentences = re.split(r'(?<=[.!?,]) +', text)  # Split by punctuation
    sentences = [s.strip() for s in sentences if s.strip()]  # Remove empty strings
    word_counts = [len(s.split()) for s in sentences]  # Count words in each sentence
    
    return sentences

def generate_voice(text, filename="voiceover.mp3", speed=1.0, output_dir="captioned video for gabriele"):
    """Convert text to speech, adjust speed, and save in the correct folder."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filepath = os.path.join(output_dir, filename)
    
    tts = gTTS(text, lang="en", tld="com.au")
    tts.save(filepath)

    # Adjust speed if needed
    if speed != 1.0:
        fast_filepath = os.path.join(output_dir, f"fast_{filename}")
        command = f'ffmpeg -i "{filepath}" -filter:a "atempo={speed}" -vn "{fast_filepath}" -y'
        subprocess.run(command, shell=True, check=True)
        return fast_filepath  # Return adjusted-speed audio file

    return filepath  # Return original file if speed = 1.0

def download_youtube_short(url, output_dir="downloads"):
    """Downloads a YouTube Short and returns the file path."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",  # Spoof browser
        "extractor_args": {"youtube": {"player_client": ["web", "tv"]}},  # Bypass age restriction
        "cookies": "cookies.txt"  # 🔥 Use this if authentication is needed
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        return file_path, info.get("title", ""), info.get("description", "")

def add_captions_with_voice(video_path, text, adapt, text_font):
    """Add captions that perfectly sync with the generated voiceover."""
    ensure_output_folder()
    
    video = VideoFileClip(video_path)
    original_audio = video.audio  # Get original video audio
    sentences = split_text_into_sentences(text)
    if adapt:
        estimated_time_to_text = len(text)*0.09 # estimated every text word is 0.4 sec
        voice_speed =  estimated_time_to_text/ (video.duration - 0.05) if video.duration > 0 else 1.0
        print(f"OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU \n\n\” voice speed = {voice_speed},video duration = {video.duration},len sentences = {len(sentences)} OUUUUUUUUUUUUUUUUUUUUUUUUUUUU\n\n\n")
    else:
        voice_speed = 1.5
    
    clips = []
    audio_clips = []
    current_time = 0
    
    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue

        audio_file = generate_voice(sentence, f"voiceover_{i}.mp3", speed=voice_speed)
        audio_clip = AudioFileClip(audio_file)
        audio_clips.append(audio_clip)

        words = sentence.split()
        word_count = len(words)
        word_duration = audio_clip.duration / word_count  # Time per word

        word_clips = []
        for j in range(word_count):
            partial_text = " ".join(words[: j + 1])  # Add words progressively
            txt_clip = TextClip(
                partial_text,
                fontsize=text_font,
                font="Poppins-Bold",  # Instagram-style bold font
                color="white",
                stroke_color="white",
                stroke_width=2,
                method="caption",
                size=(video.w * 0.8, None),
                bg_color="rgba(0, 0, 0, 0.3)",  # Semi-transparent black background
            ).set_position(("center", "center")).set_start(current_time + j * word_duration).set_duration(word_duration)

            txt_clip = resize(txt_clip, 0.5).fx(fadein, 0.001).resize(1.0)

            word_clips.append(txt_clip)

        clips.extend(word_clips)
        current_time += audio_clip.duration

    final_video = CompositeVideoClip([video] + clips)
    
    if audio_clips:
        final_audio = concatenate_audioclips(audio_clips)
        final_audio = CompositeAudioClip([original_audio.volumex(0.3), final_audio.volumex(1.2)])  # Mix with lower background music
        final_video = final_video.set_audio(final_audio)
    
    output_path = os.path.join("captioned video for gabriele", "output_with_voice.mp4")
    final_video.write_videofile(output_path, fps=video.fps, codec="libx264", audio_codec="aac", threads=4)
    
    return output_path