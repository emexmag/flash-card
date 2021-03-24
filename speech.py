
import os
from google.cloud import texttospeech
from playsound import playsound

my_path = os.path.abspath(os.path.dirname(__file__))
credentials_path = os.path.join(my_path, "data/french-306416-fa272493f67b.json")
output_path = os.path.join(my_path, "data/output.mp3")

#if google credentials are not there load them
a = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if a == None:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

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
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

def play_word():
    playsound(output_path)
