import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from insta_functions import pimp_with_ai, download_youtube_short, add_captions_with_voice
from insta_functions import story_from_article
import subprocess

def apply_filter(input_file):
    output_file = input_file.replace(".mp4", "_filtered.mp4")
    command = [
        "ffmpeg", "-i", input_file, "-vf",
        "eq=contrast=1.2:brightness=0.1:saturation=1.1, colorbalance=rm=0.09:gm=0.08:bm=-0.1, curves=m='0/0 0.35/0.25 0.7/0.85 1/1', colortemperature=6000, unsharp=3:3:0.5",
        "-c:a", "copy", output_file
    ]
    subprocess.run(command, check=True)
    return output_file

def process_video():
    url = url_entry.get()
    num_of_words = int(words_entry.get())
    adapt = adapt_var.get()
    captions = captions_var.get()
    apply_filter_var_state = apply_filter_var.get()
    voice_over_text = article_vc_text.get()
    text_font = int(article_vc_text_font.get())
    
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, "Downloading video...\n")
    output_text.see(tk.END)
    output_text.update()
    
    try:
        video_path, video_description, description = download_youtube_short(url)
        
        if captions:
            output_text.insert(tk.END, "Adding captions to video with voiceover...\n")
            output_video = add_captions_with_voice(video_path, voice_over_text, adapt, text_font)
        else:
            output_video = video_path
            pimped_text = pimp_with_ai(video_description, num_of_words)
            output_text.insert(tk.END, f"Description (pimped):\n{pimped_text}\n")
        
        if apply_filter_var_state:
            output_text.insert(tk.END, "Applying filter to video...\n")
            output_video = apply_filter(output_video)
            
        output_text.insert(tk.END, f"\nVideo saved to: {output_video}\n")
    except Exception as e:
        output_text.insert(tk.END, f"Error: {e}\n")
    
    output_text.config(state=tk.DISABLED)

def process_article():
    article_url = article_url_entry.get()
    word_limit = int(article_words_entry.get())
    
    
    if not article_url:
        messagebox.showerror("Error", "Please enter an article URL")
        return
    
    output_article_text.config(state=tk.NORMAL)
    output_article_text.insert(tk.END, "Fetching article...\n")
    output_article_text.see(tk.END)
    output_article_text.update()
    
    try:
        title, summary, full_text = story_from_article(article_url, word_limit)
        output_article_text.insert(tk.END, f"Title: {title}\n\nSummary:\n{summary}\n")
    except Exception as e:
        output_article_text.insert(tk.END, f"Error: {e}\n")
    
    output_article_text.config(state=tk.DISABLED)

def clear_youtube_output():
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.config(state=tk.DISABLED)

def clear_article_output():
    output_article_text.config(state=tk.NORMAL)
    output_article_text.delete("1.0", tk.END)
    output_article_text.config(state=tk.DISABLED)
    
# Create UI window
root = tk.Tk()
root.title("Content Processor")
root.geometry("1000x800")

notebook = ttk.Notebook(root)

youtube_frame = ttk.Frame(notebook)
article_frame = ttk.Frame(notebook)
notebook.add(youtube_frame, text="YouTube Shorts")
notebook.add(article_frame, text="Story from Article")
notebook.pack(expand=True, fill="both")

# YouTube Tab
tk.Label(youtube_frame, text="YouTube URL:").pack()
url_entry = tk.Entry(youtube_frame, width=50)
url_entry.pack()

tk.Label(youtube_frame, text="Number of words for AI text:").pack()
words_entry = tk.Entry(youtube_frame, width=10)
words_entry.insert(0, "100")
words_entry.pack()

#voice_over_text
tk.Label(youtube_frame, text="Voice over text:").pack()
article_vc_text = tk.Entry(youtube_frame, width=80) 
article_vc_text.insert(0, "...")
article_vc_text.pack()

tk.Label(youtube_frame, text="Text font:").pack()
article_vc_text_font = tk.Entry(youtube_frame, width=80) 
article_vc_text_font.insert(0, "60")
article_vc_text_font.pack()

adapt_var = tk.BooleanVar()
adapt_checkbox = tk.Checkbutton(youtube_frame, text="Adapt Captions", variable=adapt_var)
adapt_checkbox.pack()

captions_var = tk.BooleanVar()
captions_checkbox = tk.Checkbutton(youtube_frame, text="Generate Captions", variable=captions_var)
captions_checkbox.pack()

apply_filter_var = tk.BooleanVar()
apply_filter_checkbox = tk.Checkbutton(youtube_frame, text="Apply Filter", variable=apply_filter_var)
apply_filter_checkbox.pack()

run_button = tk.Button(youtube_frame, text="Run", command=process_video)
run_button.pack()

clear_button = tk.Button(youtube_frame, text="Clear", command=clear_youtube_output)
clear_button.pack()

output_text = tk.Text(youtube_frame, height=10, width=70, state=tk.DISABLED)
output_text.pack()

# Article Tab
tk.Label(article_frame, text="Article URL:").pack()
article_url_entry = tk.Entry(article_frame, width=50)
article_url_entry.pack()

tk.Label(article_frame, text="Word Limit for Summary:").pack()
article_words_entry = tk.Entry(article_frame, width=10)
article_words_entry.insert(0, "100")
article_words_entry.pack()

article_run_button = tk.Button(article_frame, text="Fetch Story", command=process_article)
article_run_button.pack()

article_clear_button = tk.Button(article_frame, text="Clear", command=clear_article_output)
article_clear_button.pack()

output_article_text = tk.Text(article_frame, height=10, width=70, state=tk.DISABLED)
output_article_text.pack()

root.mainloop()
