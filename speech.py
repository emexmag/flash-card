
import os
from google.cloud import texttospeech
from playsound import playsound

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="data/key.json"

def synthesize_text_file(text):
    """Synthesizes speech from the input file of text."""

    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="fr-FR", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open("data/output.mp3", "wb") as out:
        out.write(response.audio_content)

def play_word():
    playsound("data/output.mp3")
