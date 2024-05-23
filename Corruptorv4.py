import random
import argparse
from tqdm import tqdm
import os
import json

def corrupt_byte(byte, method):
    if method == "flip_bit":
        bit_to_flip = 1 << random.randint(0, 7)
        return byte ^ bit_to_flip
    elif method == "increment":
        return (byte + 1) % 256
    elif method == "decrement":
        return (byte - 1) % 256
    elif method == "randomize":
        return random.randint(0, 255)
    else:
        raise ValueError(f"Unknown corruption method: {method}")

def corrupt_nes_rom(file_path, start_offset, end_offset, corruption_chance, method, pattern=None, chunk_size=1, save_original=False, log_file=None):
    try:
        if save_original:
            backup_path = f"{file_path}.bak"
            os.rename(file_path, backup_path)
            with open(backup_path, 'rb') as backup_file, open(file_path, 'wb') as rom_file:
                rom_file.write(backup_file.read())

        with open(file_path, 'r+b') as rom_file:
            rom_file.seek(0, 2)
            file_size = rom_file.tell()
            start_offset = max(0, min(file_size - 1, start_offset))
            end_offset = max(start_offset, min(file_size - 1, end_offset))

            rom_file.seek(start_offset)

            corruption_log = []

            for offset in tqdm(range(start_offset, end_offset + 1, chunk_size), desc="Corrupting", unit="byte"):
                if random.random() < corruption_chance:
                    for i in range(chunk_size):
                        if offset + i > end_offset:
                            break
                        rom_file.seek(offset + i)
                        byte = ord(rom_file.read(1))

                        if pattern:
                            byte = corrupt_byte(byte, pattern[offset % len(pattern)])
                        else:
                            byte = corrupt_byte(byte, method)

                        rom_file.seek(offset + i)
                        rom_file.write(bytes([byte]))

                        if log_file:
                            corruption_log.append({'offset': offset + i, 'original_byte': byte})

        if log_file:
            with open(log_file, 'w') as log:
                json.dump(corruption_log, log)

        print("Corruption completed successfully!")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corrupt a file by randomly modifying bytes.")
    parser.add_argument("file_path", type=str, help="Path to the file.")
    parser.add_argument("start_offset", type=int, help="Start offset (in bytes) for corruption.")
    parser.add_argument("end_offset", type=int, help="End offset (in bytes) for corruption.")
    parser.add_argument("corruption_chance", type=float, help="Chance (between 0 and 1) to corrupt each byte.")
    parser.add_argument("method", type=str, choices=["flip_bit", "increment", "decrement", "randomize"], help="Method of corruption.")
    parser.add_argument("--pattern", type=str, nargs='+', choices=["flip_bit", "increment", "decrement", "randomize"], help="Pattern of corruption methods.")
    parser.add_argument("--chunk_size", type=int, default=1, help="Size of data chunks to corrupt at a time.")
    parser.add_argument("--save_original", action="store_true", help="Save a backup of the original file.")
    parser.add_argument("--log_file", type=str, help="Path to save the corruption log.")

    args = parser.parse_args()

    corrupt_nes_rom(
        args.file_path,
        args.start_offset,
        args.end_offset,
        args.corruption_chance,
        args.method,
        pattern=args.pattern,
        chunk_size=args.chunk_size,
        save_original=args.save_original,
        log_file=args.log_file
    )
