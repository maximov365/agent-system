"""Deterministic original PCM16 audio for the reference game; no external recordings."""
import math
import random
import struct
import wave
from pathlib import Path

RATE = 22050
OUT = Path(__file__).resolve().parents[1] / 'runtime'
OUT.mkdir(exist_ok=True)


def save(name, duration, sample):
    count = int(duration * RATE)
    values = [max(-.9, min(.9, sample(i / RATE, i, count))) for i in range(count)]
    with wave.open(str(OUT / (name + '.wav')), 'wb') as file:
        file.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        file.writeframes(struct.pack('<' + 'h' * count, *(round(v * 32767) for v in values)))


def bell(t, frequency, duration):
    if not 0 <= t < duration:
        return 0
    attack = min(1, t / .008)
    decay = math.exp(-8 * t / duration) * min(1, (duration - t) / .02)
    return attack * decay * (math.sin(math.tau * frequency * t) + .18 * math.sin(math.tau * frequency * 2 * t))


save('packed', .22, lambda t, i, n: .27 * bell(t, 783.99, .22))
save('complete', .65, lambda t, i, n: .20 * sum(bell(t - offset, note, .36)
     for offset, note in [(0, 523.25), (.10, 659.25), (.20, 783.99)]))
save('mistake', .24, lambda t, i, n: .20 * bell(t, 196, .24))
rng = random.Random(42)
filtered = 0
def sea(t, i, count):
    global filtered
    filtered = .95 * filtered + .05 * rng.uniform(-1, 1)
    window = math.sin(math.pi * i / (count - 1)) ** 2
    return .35 * filtered * window + .012 * math.sin(math.tau * 110 * t) * window
save('sea', 6, sea)
