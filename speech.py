
import os
from google.cloud import texttospeech

my_path = os.path.abspath(os.path.dirname(__file__))
credentials_path = os.path.join(my_path, "data/french-306416-fa272493f67b.json")

prod_path = os.environ.get('AUDIO_PATH')
if prod_path == None:
    output_path = os.path.join(my_path, "static/")
else:
    output_path = prod_path

#if google credentials are not there load them
a = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if a == None:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

def synthesize_text_file(text,id):
    """Synthesizes speech from the input file of text."""

    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="fr-FR", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        #audio_encoding=texttospeech.AudioEncoding.MP3
        audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    audio_path = os.path.join(output_path, f"{id}_output.ogg")
    # The response's audio_content is binary.
    with open(audio_path, "wb") as out:
        out.write(response.audio_content)

def generate(id):
    audio_path = os.path.join(output_path, f"{id}_output.ogg")
    with open(audio_path, "rb") as fogg:
        data = fogg.read(1024)
        while data:
            yield data
            data = fogg.read(1024)
