from ..utils import util
import os

output_path = "./results/MT-results/dictionary-based/modified/"
output_file_name = "MT2-output.txt"
errors_file_name = "MT2-errors.txt"
dictionary_path = "./data/dictionaries/sample_dictionary.xlsx"

# print the directory of this file
dictionary = util.read_dictionary(dictionary_path)
print(dictionary)