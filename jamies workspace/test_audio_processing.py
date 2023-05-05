import unittest
import numpy as np
from mp3ToPcm_pydub import mp3_to_pcm  # Assuming your original script is named 'mp3ToPcm_pydub.py'

class TestAudioProcessing(unittest.TestCase):

    def test_mp3_to_pcm(self):
        test_file = 'pickupphone.mp3'  # Add a test audio file to your project directory
        pcm_data = mp3_to_pcm(test_file)

        # Check if the output is a NumPy array
        self.assertIsInstance(pcm_data, np.ndarray)
        print("Test 1 passed: The output is a NumPy array")

        # Check if the output array is not empty
        self.assertGreater(len(pcm_data), 0)
        print(f"Test 2 passed: The output array is not empty (Length: {len(pcm_data)})")

        # Check if the output array has the correct data type
        self.assertEqual(pcm_data.dtype, np.int16)
        print("Test 3 passed: The output array has the correct data type (int16)")

if __name__ == '__main__':
    unittest.main()


# python -m unittest test_audio_processing.py
