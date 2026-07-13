import math
import os
import random
import struct
import uuid
import wave


ROOT = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(ROOT, "assets", "audio")
SAMPLE_RATE = 44100


def clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))


def ensure_len(samples, seconds):
    target = int(seconds * SAMPLE_RATE)
    if len(samples) < target:
        samples.extend([0.0] * (target - len(samples)))
    return samples


def add(dst, src, offset=0, gain=1.0):
    offset_samples = int(offset * SAMPLE_RATE)
    ensure_len(dst, (offset_samples + len(src)) / SAMPLE_RATE)
    for i, v in enumerate(src):
        dst[offset_samples + i] += v * gain


def envelope(t, attack, decay, sustain, release, duration):
    if t < attack:
        return t / max(attack, 0.0001)
    if t < attack + decay:
        k = (t - attack) / max(decay, 0.0001)
        return 1.0 + (sustain - 1.0) * k
    if t < duration - release:
        return sustain
    k = (duration - t) / max(release, 0.0001)
    return max(0.0, sustain * k)


def tone(freq, duration, gain=0.5, wave_type="sine", attack=0.01, decay=0.05, sustain=0.65, release=0.08):
    n = int(duration * SAMPLE_RATE)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        phase += freq / SAMPLE_RATE
        p = phase % 1.0
        if wave_type == "triangle":
            v = 4.0 * abs(p - 0.5) - 1.0
        elif wave_type == "square":
            v = 1.0 if p < 0.5 else -1.0
        else:
            v = math.sin(math.tau * p)
        v += 0.22 * math.sin(math.tau * p * 2.0)
        v += 0.08 * math.sin(math.tau * p * 3.0)
        out.append(v * gain * envelope(t, attack, decay, sustain, release, duration))
    return out


def pitch_sweep(start_freq, end_freq, duration, gain=0.5, noise=0.0):
    n = int(duration * SAMPLE_RATE)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        k = t / max(duration, 0.0001)
        freq = start_freq + (end_freq - start_freq) * k
        phase += freq / SAMPLE_RATE
        env = math.exp(-5.4 * k)
        v = math.sin(math.tau * phase) * env
        if noise:
            v += random.uniform(-1, 1) * noise * env
        out.append(v * gain)
    return out


def noise_burst(duration, gain=0.4, decay=8.0, lowpass=0.12):
    n = int(duration * SAMPLE_RATE)
    out = []
    last = 0.0
    for i in range(n):
        k = i / max(1, n - 1)
        raw = random.uniform(-1.0, 1.0)
        last += (raw - last) * lowpass
        out.append(last * gain * math.exp(-decay * k))
    return out


def normalize(samples, peak=0.88):
    m = max((abs(v) for v in samples), default=1.0)
    if m <= 0:
        return samples
    scale = peak / m
    return [clamp(v * scale) for v in samples]


def save_wav(name, samples):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    samples = normalize(samples)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        data = bytearray()
        for s in samples:
            data.extend(struct.pack("<h", int(clamp(s) * 32767)))
        f.writeframes(data)
    return path


def make_hit():
    random.seed(11)
    out = []
    add(out, pitch_sweep(1420, 420, 0.18, gain=0.38, noise=0.18), 0.0)
    add(out, noise_burst(0.12, gain=0.46, decay=15, lowpass=0.2), 0.15)
    add(out, pitch_sweep(155, 86, 0.18, gain=0.78, noise=0.08), 0.15)
    add(out, tone(635, 0.22, gain=0.22, wave_type="triangle", attack=0.0, decay=0.03, sustain=0.35, release=0.16), 0.18)
    add(out, tone(930, 0.16, gain=0.12, wave_type="triangle", attack=0.0, decay=0.04, sustain=0.25, release=0.1), 0.2)
    ensure_len(out, 0.55)
    return out


def make_success():
    out = []
    notes = [(523.25, 0.0), (659.25, 0.09), (783.99, 0.18), (1046.5, 0.3)]
    for freq, start in notes:
        add(out, tone(freq, 0.24, gain=0.42, wave_type="triangle", attack=0.004, decay=0.04, sustain=0.45, release=0.12), start)
    add(out, tone(1318.5, 0.26, gain=0.12, wave_type="sine", attack=0.003, decay=0.05, sustain=0.5, release=0.18), 0.34)
    ensure_len(out, 0.78)
    return out


def make_fail():
    out = []
    add(out, pitch_sweep(392, 185, 0.42, gain=0.46, noise=0.02), 0.0)
    add(out, tone(146.83, 0.34, gain=0.28, wave_type="triangle", attack=0.005, decay=0.12, sustain=0.32, release=0.18), 0.2)
    add(out, noise_burst(0.1, gain=0.18, decay=12, lowpass=0.08), 0.32)
    ensure_len(out, 0.72)
    return out


def pluck(freq, duration=0.36, gain=0.35):
    n = int(duration * SAMPLE_RATE)
    out = []
    phase = random.random()
    for i in range(n):
        t = i / SAMPLE_RATE
        k = t / duration
        phase += freq / SAMPLE_RATE
        p = phase % 1.0
        tri = 4.0 * abs(p - 0.5) - 1.0
        body = math.sin(math.tau * phase) * 0.45 + tri * 0.55
        click = random.uniform(-1, 1) * math.exp(-70 * t) * 0.08
        out.append((body + click) * gain * math.exp(-5.2 * k))
    return out


def make_bgm():
    random.seed(23)
    bpm = 116
    beat = 60.0 / bpm
    bars = 8
    total = bars * 4 * beat
    out = [0.0] * int(total * SAMPLE_RATE)
    progression = [
        [261.63, 329.63, 392.0],
        [293.66, 349.23, 440.0],
        [329.63, 392.0, 493.88],
        [392.0, 493.88, 587.33],
    ]
    melody = [659.25, 783.99, 880.0, 783.99, 659.25, 587.33, 523.25, 587.33]

    for bar in range(bars):
        chord = progression[bar % len(progression)]
        bar_start = bar * 4 * beat
        for b in range(4):
            start = bar_start + b * beat
            root = chord[0] / 2
            add(out, pluck(root, duration=0.42, gain=0.18), start)
            if b in (1, 3):
                add(out, noise_burst(0.06, gain=0.08, decay=18, lowpass=0.18), start)
            for j, freq in enumerate(chord):
                add(out, pluck(freq, duration=0.32, gain=0.12), start + j * beat / 5)

        for step in range(8):
            freq = melody[(bar + step) % len(melody)]
            add(out, pluck(freq, duration=0.22, gain=0.14), bar_start + step * beat / 2)

    # Short fade edges reduce clicks while keeping the loop feeling continuous.
    fade = int(0.035 * SAMPLE_RATE)
    for i in range(fade):
        k = i / fade
        out[i] *= k
        out[-1 - i] *= k
    return out


def write_directory_meta():
    meta_path = os.path.join(ROOT, "assets", "audio.meta")
    if os.path.exists(meta_path):
        return
    content = (
        "{\n"
        '  "ver": "1.2.0",\n'
        '  "importer": "directory",\n'
        '  "imported": true,\n'
        f'  "uuid": "{uuid.uuid4()}",\n'
        '  "files": [],\n'
        '  "subMetas": {},\n'
        '  "userData": {}\n'
        "}\n"
    )
    with open(meta_path, "w", encoding="ascii") as f:
        f.write(content)


def main():
    write_directory_meta()
    paths = [
        save_wav("arrow_hit.wav", make_hit()),
        save_wav("success.wav", make_success()),
        save_wav("fail.wav", make_fail()),
        save_wav("bgm_loop.wav", make_bgm()),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
