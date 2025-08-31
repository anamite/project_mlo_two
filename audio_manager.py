#!/usr/bin/env python3
"""
Audio Manager Module
Handles audio input/output operations including recording, playback, and TTS
"""

from fastapi import requests
import numpy as np
import sounddevice as sd
import queue
import sys
from kittentts import KittenTTS
import requests
import base64
import io
import soundfile as sf
import os
import time
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the .env file


class AudioManager:
    def __init__(self, samplerate=16000):
        self.samplerate = samplerate
        self.audio_queue = queue.Queue()
        self.wake_queue = queue.Queue()
        
        # Initialize TTS model
        print("Loading TTS model...")
        self.tts_model = KittenTTS("KittenML/kitten-tts-nano-0.2")
        
        # TTS voices
        self.voices = [
            'expr-voice-2-m', 'expr-voice-2-f', 'expr-voice-3-m', 'expr-voice-3-f',
            'expr-voice-4-m', 'expr-voice-4-f', 'expr-voice-5-m', 'expr-voice-5-f'
        ]
        self.current_voice = 'expr-voice-5-f'
        
    def set_voice(self, voice):
        """Set the TTS voice"""
        if voice in self.voices:
            self.current_voice = voice
        else:
            print(f"Warning: Voice '{voice}' not available. Using default.")
    
    def play_beep(self, frequency=800, duration=0.6):
        """Play a beep tone to indicate activation"""
        try:
            sample_rate = 24000
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = 0.3 * np.sin(frequency * 2 * np.pi * t)
            sd.play(wave, samplerate=sample_rate)
            sd.wait()
        except Exception as e:
            print(f"Beep error: {e}")

    # play low beep twice
    def play_low_beep(self):
        """Play a low beep tone to indicate deactivation"""
        self.play_beep(frequency=400, duration=0.3)

    def play_sound(self, file_path):
        """Play a sound file"""
        try:
            data, samplerate = sf.read(file_path, dtype='float32')
            sd.play(data, samplerate=samplerate)
            sd.wait()
        except Exception as e:
            print(f"Sound playback error: {e}")

    def speak(self, text):
        """Convert text to speech and play it"""
        try:
            print(f"🔊 Speaking: {text}")
            audio = self.tts_model.generate(text, voice=self.current_voice)
            sd.play(audio, samplerate=24000)
            sd.wait()  # Wait until audio finishes playing
        except Exception as e:
            print(f"TTS Error: {e}")

    def wake_word_callback(self, indata, frames, time, status):
        """Callback for wake word detection"""
        if status:
            print(status, file=sys.stderr)

        # Convert to int16 for openWakeWord
        audio_int16 = np.frombuffer(indata, dtype=np.float32) * 32767
        audio_int16 = audio_int16.astype(np.int16)
        self.wake_queue.put(audio_int16)

    def command_callback(self, indata, frames, time, status):
        """Callback for command recording (VOSK)"""
        if status:
            print(status, file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    def get_wake_audio(self):
        """Get audio data for wake word detection"""
        if not self.wake_queue.empty():
            return self.wake_queue.get_nowait()
        return None

    def get_command_audio(self, timeout=0.1):
        """Get audio data for command recognition"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def check_internet_connectivity(self, timeout=3):
        """Check if internet connection is available"""
        try:
            requests.get("https://www.google.com", timeout=timeout)
            return True
        except (requests.ConnectionError, requests.Timeout):
            return False

    def resemble_tts_speak(self, text, api_key="mqQeZH6Uo3aZhae5CFSmsgtt", voice_uuid="55592656"):
        """Use Resemble AI TTS to convert text to speech"""
        try:
            url = "https://f.cluster.resemble.ai/synthesize"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip"
            }
            data = {
                "voice_uuid": voice_uuid,
                "data": text,
                "sample_rate": 24000,
                "output_format": "wav"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            json_resp = response.json()
            if not json_resp.get("success", False):
                issues = json_resp.get("issues", ["Unknown error"])
                raise Exception(f"Resemble API error: {'; '.join(issues)}")
            
            # Decode base64 audio content
            audio_b64 = json_resp["audio_content"]
            audio_bytes = base64.b64decode(audio_b64)
            
            # Convert bytes to numpy array for playback
            audio_buffer = io.BytesIO(audio_bytes)
            audio_data, sample_rate = sf.read(audio_buffer)
            
            # Play the audio
            print(f"🔊 Speaking (Resemble AI): {text}")
            sd.play(audio_data, samplerate=sample_rate)
            sd.wait()
            
            return True
            
        except Exception as e:
            print(f"Resemble AI TTS Error: {e}")
            return False

    def auto_detect_speak(self, text, resemble_api_key=None, resemble_voice_uuid="55592656"):
        """
        Automatically detect internet connectivity and use Resemble AI TTS if available,
        otherwise fallback to KittenTTS
        
        Args:
            text (str): Text to convert to speech
            resemble_api_key (str): Resemble AI API key (can also be set via RESEMBLE_API_KEY env var)
            resemble_voice_uuid (str): Resemble AI voice UUID (default: "55592656")
        """
        
        # Get API key from parameter or environment variable
        if not resemble_api_key:
            resemble_api_key = os.getenv('RESEMBLE_API_KEY')
        # resemble_api_key = "mqQeZH6Uo3aZhae5CFSmsgtt"

        # Check if we have internet connectivity and API key
        if resemble_api_key and self.check_internet_connectivity():
            print("🌐 Internet detected, trying Resemble AI TTS...")
            
            # Try Resemble AI TTS
            # if self.stream_speak_Resemble(" .." +text+ "..", resemble_api_key, resemble_voice_uuid):
            #     return  # Success, we're done
            if self.speak_polly(" .." +text+ ".."):
                return  # Success, we're done
            else:
                print("⚠️ Resemble AI failed, falling back to KittenTTS...")
        else:
            if not resemble_api_key:
                print("⚠️ No Resemble AI API key found, using KittenTTS...")
            else:
                print("📶 No internet connection, using KittenTTS...")
        
        # Fallback to KittenTTS
        self.speak(" .." +text+ "..")
    
    def stream_speak_Resemble(self, text, api_key=None, voice_uuid="55592656", sample_rate=44100):
        """
        HTTP streaming TTS using Resemble AI with direct audio playback (no temp files)
        """
        try:
            if not api_key:
                api_key = os.getenv('RESEMBLE_API_KEY')
            
            if not api_key:
                print("❌ No Resemble AI API key found")
                return False
            
            url = "https://f.cluster.resemble.ai/stream"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "voice_uuid": voice_uuid,
                "data": text,
                "output_format": "wav",
                "sample_rate": sample_rate,
                "precision": "PCM_16"
            }
            
            print(f"🔊 HTTP Streaming (Resemble AI): {text}")
            start_time = time.time()
            
            response = requests.post(url, headers=headers, json=payload, timeout=(3, 30))
            response.raise_for_status()
            
            if response.status_code == 200 and 'audio/wav' in response.headers.get('content-type', ''):
                ttfb = time.time() - start_time
                print(f"⚡ Time to Response: {ttfb:.3f}s")
                
                # Get raw audio data
                audio_data = response.content
                
                # Skip WAV header (44 bytes) to get raw PCM data
                pcm_data = audio_data[44:]
                
                # Convert to numpy array for sounddevice
                audio_np = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Play directly with sounddevice (no temp files!)
                sd.play(audio_np, samplerate=sample_rate, blocking=False)
                
                total_time = time.time() - start_time
                print(f"🎵 Total Latency: {total_time:.3f}s")
                
                sd.wait()  # Wait for playback to complete
                print("✅ Streaming completed")
                return True
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Streaming Error: {e}")
            return False
    def speak_polly(self, text, voice_id="Matthew", output_format="pcm", sample_rate="16000"):
        """
        HTTP streaming TTS using Amazon Polly with direct audio playback (no temp files)
        """
        try:
            import boto3
            import sounddevice as sd
            import numpy as np
            import time
            
            # Initialize Polly client (uses AWS credentials from environment or AWS config)
            polly = boto3.client('polly',
                            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                            region_name=os.getenv('AWS_REGION', 'us-east-1'))

            print(f"🔊 HTTP Streaming (Amazon Polly): {text}")
            start_time = time.time()
            
            # Request speech synthesis
            response = polly.synthesize_speech(
                Text=text,
                OutputFormat=output_format,
                VoiceId=voice_id,
                Engine="generative"
            )
            
            ttfb = time.time() - start_time
            print(f"⚡ Time to Response: {ttfb:.3f}s")
            
            # Get audio stream
            audio_stream = response['AudioStream']
            audio_data = audio_stream.read()
            
            # Convert PCM data to numpy array for sounddevice
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Play directly with sounddevice (no temp files!)
            sd.play(audio_np, samplerate=int(sample_rate), blocking=False)
            
            total_time = time.time() - start_time
            print(f"🎵 Total Latency: {total_time:.3f}s")
            
            sd.wait()  # Wait for playback to complete
            print("✅ Streaming completed")
            return True
            
        except Exception as e:
            print(f"❌ Streaming Error: {e}")
            return False


