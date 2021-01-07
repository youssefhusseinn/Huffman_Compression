from collections import deque
from time import time

from input_reader import InputReader
from misc import *


class OutputWriter:

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.output_buffer = []
        self.file = open(file_name, "w", encoding=ENCODING)

    def write_to_file(self, character: str):
        if len(self.output_buffer) + len(character) < KB_SIZE:
            self.output_buffer.append(character)
        else:
            self.output_buffer.append(character)
            self.file.write("".join(self.output_buffer))
            self.output_buffer.clear()

    def write_meta_data(self, huffman_codes: dict):
        pairs_list = []
        for key, value in huffman_codes.items():
            pairs_list.append(key + value + DELIM)
        char_count = self.__huffman_codes_car_length(huffman_codes)
        pairs_line = str(char_count) + DELIM + "".join(pairs_list)
        self.file.write(pairs_line)

    def __huffman_codes_car_length(self, huffman_codes: dict):
        sum = 2 * len(huffman_codes)
        for value in huffman_codes.values():
            sum += len(value)
        return sum

    def write_path(self, path: str):
        line = str(len(path)) + DELIM + path
        self.file.write(line)

    def __compressed_str_char_bits(self, txt: str, huffman_codes: dict):
        result = 0
        for c in txt:
            result += len(huffman_codes[c])
        return result

    def __compress_bits_to_chars(self, buffer_dq: deque):
        while len(buffer_dq) >= 8:
            byte_binary = [buffer_dq.popleft() for i in range(8)]
            ascii_code = list_to_ascii(byte_binary)

            out_char = chr(ascii_code)
            self.file.write(str(out_char))

    def write_compressed_data(self, huffman_codes: dict, file_name: str):
        input_reader = InputReader(file_name, False)
        bits = 0

        while input_reader.fill_buffer():
            bits += self.__compressed_str_char_bits(input_reader.buffer, huffman_codes)

        char_count, readable_from_last_char = bits // 8, bits % 8
        line = str(char_count) + DELIM + str(readable_from_last_char) + DELIM

        self.file.write(line)

        input_reader = InputReader(file_name, False)
        buffer_dq = deque([])
        ts = time()
        chunck = 0
        while input_reader.fill_buffer():
            print(chunck)
            chunck += 1
            for character in input_reader.buffer:
                code = huffman_codes[character]
                for bit in code:
                    buffer_dq.append(int(bit))
                    self.__compress_bits_to_chars(buffer_dq)

        if len(buffer_dq) > 0:
            while len(buffer_dq) != 8:
                buffer_dq.append(0)
            self.__compress_bits_to_chars(buffer_dq)
        te = time()
        print(f'time= {te - ts}')

    def close(self):
        self.file.close()