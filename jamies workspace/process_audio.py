import os
import psycopg2
from pydub import AudioSegment
import numpy as np
import config 

def snip_first_30_seconds(input_file, output_file):
    print(f"Snipping the first 30 seconds of '{input_file}'...")
    audio = AudioSegment.from_mp3(input_file)
    snipped_audio = audio[:30000]  # First 30 seconds
    snipped_audio.export(output_file, format='mp3')
    print(f"Snipped audio saved to '{output_file}'")


def mp3_to_pcm(file_path):
    print(f"Converting MP3 file '{file_path}' to PCM data...")
    audio = AudioSegment.from_mp3(file_path)
    print(f"Original audio info: Channels: {audio.channels}, Frame rate: {audio.frame_rate}, Length: {len(audio)} ms")
    
    # Convert stereo to mono by averaging the channels
    if audio.channels == 2:
        left_channel = audio.split_to_mono()[0]
        right_channel = audio.split_to_mono()[1]
        mixed_audio = left_channel.overlay(right_channel)
        audio = mixed_audio - 3  # Adjust the volume to avoid clipping
    
    # audio = audio.set_frame_rate(256000)  # Set sample rate
    pcm_data = np.array(audio.get_array_of_samples())  # Get PCM data
    print(f"Converted audio info: Channels: {audio.channels}, Frame rate: {audio.frame_rate}, Length: {len(audio)} ms")
    print(f"PCM data info: Size: {len(pcm_data)}, First 5 elements: {pcm_data[:5]}")
    return pcm_data


def create_db():
    print("Creating the database...")
    conn = psycopg2.connect(database=config.DATABASE["name"], user=config.DATABASE["user"], password=config.DATABASE["password"], host=config.DATABASE["host"], port=config.DATABASE["port"])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS audio_files (id SERIAL PRIMARY KEY, pcm_data BYTEA);''')
    conn.commit()
    conn.close()
    print("Database created successfully.")

def store_pcm_data(pcm_data):
    print("Storing PCM data in the database...")
    conn = psycopg2.connect(database=config.DATABASE["name"], user=config.DATABASE["user"], password=config.DATABASE["password"], host=config.DATABASE["host"], port=config.DATABASE["port"])
    c = conn.cursor()
    binary_data = pcm_data.tobytes()  # Convert NumPy array to bytes
    
    # Log the size of the data and the first 5 elements
    print(f"PCM data before storing: Size: {len(pcm_data)}, First 5 elements: {pcm_data[:5]}")
    
    c.execute('''INSERT INTO audio_files (pcm_data) VALUES (%s)''', (psycopg2.Binary(binary_data),))
    conn.commit()
    conn.close()
    print(f"PCM data stored successfully. Size: {len(pcm_data)}, First 5 elements: {pcm_data[:5]}")

def fetch_pcm_data():
    print("Fetching PCM data from the database...")
    conn = psycopg2.connect(database=config.DATABASE["name"], user=config.DATABASE["user"], password=config.DATABASE["password"], host=config.DATABASE["host"], port=config.DATABASE["port"])
    c = conn.cursor()
    c.execute('''SELECT * FROM audio_files''')
    rows = c.fetchall()
    conn.close()
    pcm_data_list = [np.frombuffer(row[1], dtype=np.int16) for row in rows]  # Convert bytes back to NumPy array
    print("PCM data fetched successfully.")
    for i, pcm_data in enumerate(pcm_data_list):
        print(f"PCM data {i}: Size: {len(pcm_data)}, First 5 elements: {pcm_data[:5]}")
    return pcm_data_list



def similarity_score(pcm_data1, pcm_data2, downsample_factor=100):
    print("Calculating similarity score...")

    # Downsample the PCM data to speed up the calculation
    pcm_data1_downsampled = pcm_data1[::downsample_factor]
    pcm_data2_downsampled = pcm_data2[::downsample_factor]

    correlation = np.correlate(pcm_data1_downsampled, pcm_data2_downsampled, mode='valid')[0]
    return correlation


if __name__ == "__main__":
    # Create the database
    create_db()

    # Snip the first 10 seconds of the input file and create a new audio file
    input_file = 'drake.mp3'
    snipped_file = 'tmp/pickupphone.mp3'
    os.makedirs('tmp', exist_ok=True)
    snip_first_30_seconds(input_file, snipped_file)

    # Extract PCM data from the main file and store it in the database
    main_pcm_data = mp3_to_pcm(input_file)
    print(f"Storing PCM data in the database... {main_pcm_data}")
    
    store_pcm_data(main_pcm_data)

    # Extract PCM data from the 10-second clip
    # snipped_pcm_data = mp3_to_pcm(snipped_file)
    snipped_pcm_data = mp3_to_pcm(input_file)
    # Fetch PCM data from the database
    stored_pcm_data_list = fetch_pcm_data()

        # Compare the PCM data from the 10-second clip to the stored PCM data
    max_similarity = -1
    best_match_index = -1
    for i, stored_pcm_data in enumerate(stored_pcm_data_list):
        similarity = similarity_score(snipped_pcm_data, stored_pcm_data)
        print(f"Similarity score with stored PCM data {i}: {similarity}")

        if similarity > max_similarity:
            max_similarity = similarity
            best_match_index = i

    print(f"\nBest match found: Stored PCM data {best_match_index}")
    print(f"Highest similarity score: {max_similarity}")

