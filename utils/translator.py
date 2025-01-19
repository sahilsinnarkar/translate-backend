import os
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import tempfile
import uuid
# }

# Supported languages
INDIAN_LANGUAGES = {
    'Hindi': 'hi',
    'Marathi': 'mr',
    'Gujarati': 'gu',
    'Tamil': 'ta',
    'Kannada': 'kn',
    'Telugu': 'te',
    'Bengali': 'bn',
    'Malayalam': 'ml',
    'Punjabi': 'pa',
    'Odia': 'or'
}

# Process video file
def process_video(video_file, source_language):
    session_id = str(uuid.uuid4())
    audio_path = convert_video_to_audio(video_file)
    if not audio_path:
        raise Exception("Failed to convert video to audio")
    
    try:
        # Transcribe audio to English
        english_text = transcribe_audio_to_english(audio_path, source_language)
        if not english_text:
            raise Exception("Failed to transcribe audio")
        
        # Generate translations and audio files
        translations = {}
        for lang_name, lang_code in INDIAN_LANGUAGES.items():
            translated_text = translate_text(english_text, lang_code)
            if translated_text:
                audio_filename = f"{session_id}_{lang_code}.mp3"
                audio_path = create_audio_file(translated_text, lang_code, audio_filename)
                translations[lang_name] = {
                    'text': translated_text,
                    'audio_url': f'/api/audio/{audio_filename}'
                }
        
        return {
            'english_text': english_text,
            'translations': translations
        }
    finally:
        # Cleanup
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

# Convert video to audio
def convert_video_to_audio(video_file):
    try:
        temp_video = tempfile.mktemp(suffix='.mp4')
        video_file.save(temp_video)
        
        video = VideoFileClip(temp_video)
        audio_path = tempfile.mktemp(suffix='.wav')
        video.audio.write_audiofile(audio_path)
        
        video.close()
        os.remove(temp_video)
        
        return audio_path
    except Exception as e:
        print(f"Error converting video to audio: {str(e)}")
        return 

# Transcribe audio
def transcribe_audio_to_english(audio_path, source_language):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=source_language)
        
        if source_language != 'en-US':
            translator = Translator()
            translation = translator.translate(text, dest='en')
            return translation.text
        return text
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        return 

# Translate text
def translate_text(text, target_language):
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        return 

# Create audio file from text
def create_audio_file(text, language_code, filename):
    try:
        output_path = os.path.join('temp', filename)
        tts = gTTS(text=text, lang=language_code, slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error creating audio file: {str(e)}")
        return 