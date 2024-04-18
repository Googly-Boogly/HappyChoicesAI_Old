# your_app/consumers.py
import os
from typing import Deque

from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import webrtcvad
from vosk import Model, KaldiRecognizer
from collections import deque
from ai.other.text_to_speech import read_speech_file, create_mp3_file, delete_speech_file
from global_code.helpful_functions import create_logger_error, log_it
logger = create_logger_error(file_path=os.path.abspath(__file__), name_of_log_file='name',
                                 log_to_console=True, log_to_file=False)


class AudioConsumer(AsyncWebsocketConsumer):
    """
    The Text to Speech consumer is used to handle the audio messages
    """
    async def connect(self):
        self.group_name = 'audio_group'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        # log_it(logger, error=None, custom_message=f'AudioConsumer: Connected')

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Add a new method for handling messages from the channel layer
    async def audiomessage(self, event):
        message = event['message']
        # If message is supposed to be a URL, ensure it's sent as such in a dictionary
        file_name = "speech.mp3"
        await self.send(text_data=json.dumps({
            'mp3Url': str(message),
            'Content-Disposition': 'attachment; filename="%s"' % file_name
        }))


class SpeechToTextConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.vad = webrtcvad.Vad(1)  # VAD with moderate aggressiveness
        # self.model = Model("/path/to/your/vosk-model-directory")  # Path to the Vosk model directory
        self.audio_buffer: Deque[bytes] = deque(maxlen=50)  # Buffer to hold audio frames

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code: int):
        pass

    async def receive(self, text_data: str = None, bytes_data: bytes = None):
        if bytes_data:
            pass
            # loop = asyncio.get_running_loop()
            #
            # # Add the incoming audio data to the buffer
            # self.audio_buffer.append(bytes_data)
            #
            # # Check for voice activity
            # is_speech = await loop.run_in_executor(None, self.check_vad, bytes_data)
            # if is_speech:
            #     # Convert buffer to bytes for wake word detection
            #     buffered_audio = b''.join(self.audio_buffer)
            #     has_wake_word = await loop.run_in_executor(None, self.detect_wake_word, buffered_audio)
            #
            #     if has_wake_word:
            #         # Clear the buffer after wake word detection or initiate further action
            #         self.audio_buffer.clear()
            #         await self.send(text_data=json.dumps({'message': 'Wake word detected. Start speaking now...'}))

        elif text_data:
            # Handle text data if needed
            pass

    def check_vad(self, audio_data: bytes) -> bool:
        # Assuming audio_data is a frame of width 2 (16 bit), mono, sampled at 16000 Hz
        return self.vad.is_speech(audio_data, 16000)

    def detect_wake_word(self, audio_data: bytes) -> bool:
        # Implement wake word detection with Vosk
        rec = KaldiRecognizer(self.model, 16000)
        rec.AcceptWaveform(audio_data)
        result = json.loads(rec.Result())
        return "jarvis" in result.get('text', '')

    async def transcribe_to_text(self, audio_data: bytes) -> str:
        # Placeholder for your transcription logic
        # Return the transcribed text from the audio data
        return "Transcribed text"  # Implement this



