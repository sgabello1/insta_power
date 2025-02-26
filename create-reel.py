import os
import sys
from insta_functions import pimp_with_ai, download_youtube_short, add_captions_with_voice

PARAMS_FILE = "create_reel_params.txt"  # Define the parameters file

def load_parameters(filename):
    """Load parameters from a file."""
    try:
        with open(filename, "r") as file:
            data = file.read().strip().split("\n")
            params = {line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip() for line in data if "=" in line}
        return params
    except Exception as e:
        print(f"Error reading parameters file: {e}")
        sys.exit(1)

def main():

    # Load parameters
    params = load_parameters(PARAMS_FILE)
    url = params.get("URL", "")
    num_of_words = int(params.get("NUM_WORDS", 100))
    text = params.get("URL", "")
    adapt = bool(params.get("ADAPT", ""))
    captions = bool(params.get("CAPTIONS", ""))

    print("Downloading video...")
    video_path, title, description = download_youtube_short(url)
    
    if captions:
        print("Adding captions to video with voiceover...")
        output_video = add_captions_with_voice(video_path, text, adapt)
    else:
        output_video = video_path
        pimped_text = pimp_with_ai(description,num_of_words)
        print("Description(pimped) \n", pimped_text)
    print(f"\n\nVideo saved to: {output_video}")

if __name__ == "__main__":
    main()
