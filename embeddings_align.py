from approaches.ch_preprocessor.chinese_sentence_segment import split_ch_sentences
from approaches.vn_preprocessor.preprocessor import Preprocessor, Language
from approaches.utils.util import read_dictionary
import re

def align(book_name, dictionary, type):
    chinese_pars = []
    sinoviet_pars = []
    translation_pars = []
    with open(f"./{book_name}/chinese_pars.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            chinese_pars.append(line)
    with open(f"./{book_name}/sinoviet_pars.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            sinoviet_pars.append(line)
    with open(f"./{book_name}/translation_pars.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            translation_pars.append(line)
    import approaches.embeddings.main as em
    import os
    # Create tmpp_tqdn to store the preprocessed files
    tmp_dir = f"./tmp_tqdn/{book_name}"
    processed_dir = f"./tmp_tqdn/{book_name}/processed"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    idx = 0
    if type == "ch_sino":
        src_pars = chinese_pars
        trg_pars = sinoviet_pars
    elif type == "ch_vn":
        src_pars = chinese_pars
        trg_pars = translation_pars
    for src_par, trg_par in zip(src_pars, trg_pars):
        with open(f"{tmp_dir}/source_tmp.txt", "w", encoding="utf-8") as f:
            f.write(src_par)
        with open(f"{tmp_dir}/target_tmp.txt", "w", encoding="utf-8") as f:
            f.write(trg_par)
        source_txt = open(f"{tmp_dir}/source_tmp.txt", "r", encoding="utf-8").readlines()
        source_splitted = split_ch_sentences(source_txt)
        # Insert "# Start" and "# End" to the beginning and the end of the source file
        source_processed = ["# Start\n"]
        source_processed.extend(source_splitted+["\n"])
        source_processed.append("# End")
        with open("./tmp/source.txt", "w", encoding="utf-8") as f:
            for line in source_processed:
                line = line.strip()
                if line != "":
                    f.write(line + "\n")
        # Preprocess the target file
        p = Preprocessor(Language.vietnamese)
        p.segment_files_to_sentences(f"{tmp_dir}/target_tmp.txt", "./tmp/target.txt", {'overwrite': True})
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
        alignments = em.aligner("./tmp/source.txt", "./tmp/target.txt", dictionary)
        save_file_name = ""
        if type == "ch_sino":
            save_file_name = "alignments_ch_sino.txt"
        elif type == "ch_vn":
            save_file_name = "alignments_ch_vn.txt"
        with open(f"./{book_name}/{save_file_name}", "a", encoding="utf-8") as f:
            f.write(f"Paragraph {idx}\n")
            print(f"Paragraph {idx}")
            for src, trg in alignments:
                src = re.sub(r'\s+', '', src)
                trg = re.sub(r'\s+', ' ', trg)
                f.write(src + "\t" + trg + "\n")
            f.write("\n")
        idx += 1

if __name__ == "__main__":
    dictionary = read_dictionary()
    books = ["dvsk"]
    for book in books:
        align(book, dictionary, "ch_vn")