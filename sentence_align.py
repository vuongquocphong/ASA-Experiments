import shutil
from approaches.dictionary_based.dictionary_based import *
from approaches.dictionary_based.dictionary_based import aligner as dictionary_based_aligner
from approaches.length_based.gale_church import aligner as length_based_aligner
from approaches.ch_preprocessor.chinese_sentence_segment import split_ch_sentences
from approaches.vn_preprocessor.preprocessor import Preprocessor, Language
from approaches.utils.util import read_dictionary

# =====================================================================================

import nltk

def main(source, target, method):
    # Create tmp folder to store the preprocessed files
    if not os.path.exists("./tmp"):
        os.makedirs("./tmp")

    # Read the paragraphs in the source and target files
    source_txt = open(source, "r", encoding="utf-8").readlines()

    # Preprocess the source file
    source_splitted = split_ch_sentences(source_txt)

    # Insert "# Start" and "# End" to the beginning and the end of the source file
    source_processed = ["# Start\n"]
    source_processed.extend(source_splitted+["\n"])
    source_processed.append("# End")

    # Store the preprocessed source file
    with open("./tmp/source.txt", "w", encoding="utf-8") as f:
        for line in source_processed:
            line = line.strip()
            if line != "":
                f.write(line + "\n")
    
    # Preprocess the target file
    p = Preprocessor(Language.vietnamese)
    p.segment_files_to_sentences(target, "./tmp/target.txt", {'overwrite': True})

    # Insert "# Start" and "# End" to the beginning and the end of the target file
    target_txt = open("./tmp/target.txt", "r", encoding="utf-8").readlines()
    target_processed = ["# Start\n"]
    target_processed.extend(target_txt+["\n"])
    target_processed.append("\n# End")

    # Store the preprocessed target file
    with open("./tmp/target.txt", "w", encoding="utf-8") as f:
        for line in target_processed:
            if line.strip() != "":
                f.write(line)
    alignments = None
    # Run the alignment method
    if method == "dictionary_based":
        dictionary = read_dictionary()
        alignments = dictionary_based_aligner("./tmp/source.txt", "./tmp/target.txt", dictionary)
    elif method == "length_based":
        alignments = length_based_aligner("./tmp/source.txt", "./tmp/target.txt")
    else:
        raise ValueError("Invalid method name. Please choose 'dictionary_based' or 'length_based'.")

    # Write the alignments to a file
    with open("alignments.txt", "w", encoding="utf-8") as f:
        for src, trg in alignments:
            src = re.sub(r'\s+', '', src)
            trg = re.sub(r'\s+', ' ', trg)
            f.write(src + "\t" + trg + "\n")

    # Remove the tmp folder
    # shutil.rmtree("./tmp")

# =====================================================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python sentence_align.py <source_file> <target_file> <method>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])