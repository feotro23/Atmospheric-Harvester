import wave
import math
import struct
import random

def generate_lofi_beat(filename, duration=10.0, sample_rate=44100):
    num_samples = int(duration * sample_rate)
    
    # 86 BPM
    beats = duration * (86 / 60)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2) # Stereo
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # 1. Base drone (E minor 9)
            # E (82.4), G (98), B (123.5), D (146.8), F# (185)
            # Low fidelity: add some sine waves
            freqs = [164.81, 196.00, 246.94, 293.66] # E3, G3, B3, D4
            drone = 0
            for f in freqs:
                # Add slight detune for lo-fi wobble
                wobble = math.sin(t * 3) * 0.5
                drone += math.sin(2 * math.pi * (f + wobble) * t)
            
            drone *= 0.1 # quieter
            
            # 2. Vinyl Crackle (Noise)
            noise = (random.random() - 0.5) * 0.05
            
            # 3. Simple Kick drum (every 2 beats approx)
            # Simple decay sine at 60Hz
            beat_t = (t * (86/60)) % 1.0 # 1 beat cycle
            kick = 0
            if beat_t < 0.2:
                kt = beat_t / 0.2
                kick = math.sin(2 * math.pi * 60 * beat_t) * (1.0 - kt) * 0.5
            
            # Mix
            sample = drone + noise + kick
            
            # Clipping/Saturation for "warmth"
            if sample > 0.8: sample = 0.8
            if sample < -0.8: sample = -0.8
            
            # Convert to 16-bit
            val = int(sample * 32767)
            data = struct.pack('<hh', val, val) # Left Right same
            wav_file.writeframes(data)

if __name__ == "__main__":
    import os
    if not os.path.exists("assets/sfx"):
        os.makedirs("assets/sfx")
    generate_lofi_beat("assets/sfx/music_loop.wav")
    print("Generated lo-fi beat.")
