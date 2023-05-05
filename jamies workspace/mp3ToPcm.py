import numpy as np
import librosa
import scipy.signal

def load_and_preprocess(filename, duration=None):
    y, sr = librosa.load(filename, duration=duration)
    return y, sr

def create_clip(audio, sr, start_seconds, duration_seconds):
    start_frame = start_seconds * sr
    end_frame = start_frame + (duration_seconds * sr)
    return audio[start_frame:end_frame]

def cross_correlation(signal1, signal2):
    correlation = scipy.signal.correlate(signal1, signal2)
    return correlation

def calculate_similarity(correlation):
    max_correlation = np.max(correlation)
    if max_correlation < 0:
        # if the maximum correlation is negative, flip the correlation
        correlation = -correlation
        max_correlation = np.max(correlation)
    # find the highest peak within the correlation score
    peak_idx = np.argmax(correlation)
    peak_val = correlation[peak_idx]
    # normalize the peak value to be between 0 and 1
    similarity = (peak_val / max_correlation + 1) / 2
    return similarity


def main():
    # Load full song
    full_song, sr = load_and_preprocess('drake.mp3')

    part_song, sr = load_and_preprocess('pickupphone.mp3')
    # Create a clip from the full song
    # part_song = create_clip(full_song, sr, start_seconds=0, duration_seconds=10)

    # Calculate cross-correlation
    correlation = cross_correlation(full_song, part_song)
    # Calculate similarity
    similarity = calculate_similarity(correlation)

    print(f'Similarity score: {similarity}')

if __name__ == '__main__':
    main()
