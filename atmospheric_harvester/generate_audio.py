import wave
import math
import random
import struct
import os

def generate_sine_wave(filename, frequency, duration, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            value = int(volume * 32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

def generate_white_noise(filename, duration, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            value = int(volume * 32767.0 * (random.random() * 2.0 - 1.0))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

def ensure_assets_dir():
    if not os.path.exists("assets"):
        os.makedirs("assets")
    if not os.path.exists("assets/sfx"):
        os.makedirs("assets/sfx")

def generate_assets():
    ensure_assets_dir()
    print("Generating audio assets...")
    
    # UI Click (Short high pitch)
    generate_sine_wave("assets/sfx/click.wav", 880, 0.1, 0.3)
    
    # Upgrade Buy (Ascending tone - simulated by just a higher pitch for now)
    generate_sine_wave("assets/sfx/upgrade.wav", 1200, 0.2, 0.4)
    
    # Wind Loop (White noise, long)
    generate_white_noise("assets/sfx/wind_loop.wav", 2.0, 0.2)
    
    # Rain Loop (White noise, slightly louder)
    generate_white_noise("assets/sfx/rain_loop.wav", 2.0, 0.3)
    
    print("Audio assets generated.")

if __name__ == "__main__":
    generate_assets()
