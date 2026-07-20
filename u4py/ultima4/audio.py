import math
import struct
import pygame
import threading
from typing import Union, Tuple

_enabled = False

def init_audio() -> None:
    """Initialize the pygame mixer if it hasn't been initialized already."""
    global _enabled
    if _enabled:
        return
    try:
        # Check if pygame mixer is already initialized
        if not pygame.mixer.get_init():
            # Standard low-latency retro setting: 22050Hz, 16-bit signed, mono
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        _enabled = True
    except Exception as e:
        print(f"[audio] Failed to initialize mixer: {e}")
        _enabled = False

def play_tone(frequency: Union[float, Tuple[float, float]], duration: float, volume: float = 0.3) -> None:
    """Play a tone with a static frequency or a frequency sweep (start, end).
    
    Generates raw wave data matching pygame mixer's active output format and plays it asynchronously.
    """
    if not _enabled:
        return

    def _generate_and_play():
        try:
            mix = pygame.mixer.get_init()
            if not mix:
                return
            sample_rate, fmt, channels = mix
            
            num_samples = int(sample_rate * duration)
            if num_samples <= 0:
                return
                
            is_16bit = (fmt == -16)
            
            # Parse frequency (static or sweep)
            if isinstance(frequency, tuple):
                start_freq, end_freq = frequency
            else:
                start_freq = end_freq = frequency
                
            buf = bytearray()
            phase = 0.0
            
            for i in range(num_samples):
                # Fade in/out envelope to prevent click sounds at start/end
                envelope = 1.0
                fade_len = min(100, num_samples // 4)
                if i < fade_len:
                    envelope = i / fade_len
                elif i > num_samples - fade_len:
                    envelope = (num_samples - i) / fade_len
                    
                # Linearly interpolate frequency for sweep, and accumulate phase
                progress = i / num_samples
                curr_freq = start_freq + (end_freq - start_freq) * progress
                phase += 2.0 * math.pi * curr_freq / sample_rate
                
                val = math.sin(phase) * volume * envelope
                
                # Pack based on format (signed 16-bit vs unsigned 8-bit)
                if is_16bit:
                    sval = int(val * 32767)
                    sval = max(-32768, min(32767, sval))
                    packed = struct.pack("<h", sval)
                else:
                    uval = int(128 + val * 127)
                    uval = max(0, min(255, uval))
                    packed = struct.pack("B", uval)
                    
                # Support mono/stereo duplication
                for _ in range(channels):
                    buf.extend(packed)
                    
            sound = pygame.mixer.Sound(buffer=bytes(buf))
            sound.play()
        except Exception:
            # Defensive coding: ignore any audio playback errors to ensure game stability
            pass

    # Run synthesis and playback in background to prevent blocking the game UI thread
    t = threading.Thread(target=_generate_and_play, daemon=True)
    t.start()

# --- Specialized Sound Effects ---

def play_footstep() -> None:
    """Retro low footstep bump."""
    play_tone(100.0, 0.04, volume=0.15)

def play_open() -> None:
    """Rising open/unlock creak."""
    play_tone((300.0, 600.0), 0.12, volume=0.25)

def play_close() -> None:
    """Falling close latch."""
    play_tone((400.0, 200.0), 0.10, volume=0.25)

def play_cast() -> None:
    """Ascending magic spell sound."""
    play_tone((600.0, 1600.0), 0.25, volume=0.2)

def play_fizzle() -> None:
    """Disappointing fizzle sound on failed spell recipe."""
    play_tone((150.0, 80.0), 0.35, volume=0.3)

def play_hit() -> None:
    """Slightly distorted combat hit impact."""
    play_tone((800.0, 300.0), 0.08, volume=0.3)

def play_miss() -> None:
    """Whoosh of a swing missing target."""
    play_tone((400.0, 150.0), 0.12, volume=0.15)

def play_damage() -> None:
    """Descending pain sound when player is hit or enters hazard."""
    play_tone((500.0, 180.0), 0.22, volume=0.3)

def play_level_up() -> None:
    """Ascending fanfare chord for Level Up / Elevation."""
    # Play a quick progression of rising notes
    def _fanfare():
        for freq in [523.25, 659.25, 783.99, 1046.50]:  # C5, E5, G5, C6
            play_tone(freq, 0.15, volume=0.25)
            pygame.time.wait(120)
    threading.Thread(target=_fanfare, daemon=True).start()
