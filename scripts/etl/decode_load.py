"""
A script that decodes the unprocessed file from the s3 folder input--load/

You can provide the downloaded file path, and chosen decoded file destination.
"""

import json
import pickle
from collections import deque

import lz4.frame


def lz4_pickle_decode_and_save(file_path: str, output_file: str):
    try:
        # Read the compressed pickle data from the file
        with open(file_path, "rb") as f:
            compressed_data = f.read()

        # Decompress the LZ4 data
        decompressed_data = lz4.frame.decompress(compressed_data)

        # Unpickle the decompressed data
        decoded_data = pickle.loads(decompressed_data)

        # If the data is wrapped in a deque, convert it to a list
        if isinstance(decoded_data, deque):
            decoded_data = list(decoded_data)

        # Save the decoded data to a file
        with open(output_file, "w") as json_file:
            json.dump(decoded_data, json_file, indent=2, default=str)

        print(f"Decoded transaction(s) saved to {output_file}")  # noqa

        return decoded_data

    except lz4.frame.LZ4FrameError as e:
        print(f"LZ4 decompression error: {e}")  # noqa
    except pickle.UnpicklingError as e:
        print(f"Unpickling error: {e}")  # noqa
    except FileNotFoundError:
        print(f"File not found: {file_path}")  # noqa
    except Exception as e:
        print(f"An unexpected error occurred: {e}")  # noqa


# Example usage
if __name__ == "__main__":
    # Provide your file path and output file path here
    file_path = "unprocessed-11"
    output_file = "decoded_transaction.json"

    # Decode the data from the file and save it to JSON
    decoded_deque = lz4_pickle_decode_and_save(file_path, output_file)
