import moviepy.editor as mp
import whisper
from better_profanity import profanity
import os
import sys
import json

def convert_seconds_to_minutes_and_seconds(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return minutes, seconds

def extract_audio_from_video(video_path, output_audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)

def transcribe_audio(audio_path, model_type="small"):
    model = whisper.load_model(model_type)
    result = model.transcribe(audio_path)
    return result

def scan_for_swear_words(transcription_result):
    segments = transcription_result['segments']
    swear_word_timestamps = []
    for segment in segments:
        text = segment['text']
        start_time = segment['start']
        if profanity.contains_profanity(text):
            swear_word_timestamps.append({
                'start': start_time,
                'text': text
            })
    return swear_word_timestamps

def dump_timestamps(swear_word_timestamps):
    filename = 'swear_words.json'
    swear_words = []
    for item in swear_word_timestamps:
        minutes, seconds = convert_seconds_to_minutes_and_seconds(item['start'])
        converted_time = f"{minutes:02d}:{seconds:02d}"
        swear_words.append({converted_time: item['text']}) 

    with open(filename, 'w') as f:
        json.dump(swear_words, f, indent=4)
    
    return filename

def main(video_path, selected_model):
    audio_path = "extracted_audio.wav"
    extract_audio_from_video(video_path, audio_path)
    transcription_result = transcribe_audio(audio_path, model_type=selected_model)
    swear_word_timestamps = scan_for_swear_words(transcription_result)
    json_file = dump_timestamps(swear_word_timestamps)

    os.remove(audio_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 detect.py <file_path> <model_type>")
        sys.exit(1)
    video_path = sys.argv[1]
    selected_model = sys.argv[2]
    main(video_path, selected_model)