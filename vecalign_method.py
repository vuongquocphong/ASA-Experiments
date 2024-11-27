from approaches.ch_preprocessor.chinese_sentence_segment import (
    split_ch_sentences_keep_space,
)
from approaches.vn_preprocessor.preprocessor import Preprocessor, Language
import re
from scipy.spatial.distance import cosine
from laserembeddings import Laser
import numpy as np
from approaches.utils.util import readFile

laser = Laser()

def compute_cosine_similarity(embedding1, embedding2):
    """
    Compute cosine similarity between two embeddings.
    """
    return 1 - cosine(embedding1, embedding2)


def align_sentences(source_sentences, target_sentences, src_lang="zh", trg_lang="vi"):
    """
    Align source and target sentences based on LASER embeddings and cosine similarity.
    Handles cases where the number of sentences differs.
    """

    # Compute embeddings for all sentences
    src_embeddings = laser.embed_sentences(source_sentences, lang=src_lang)
    trg_embeddings = laser.embed_sentences(target_sentences, lang=trg_lang)

    # Compute similarity matrix
    similarity_matrix = np.zeros((len(source_sentences), len(target_sentences)))
    for i, src_emb in enumerate(src_embeddings):
        for j, trg_emb in enumerate(trg_embeddings):
            similarity_matrix[i, j] = compute_cosine_similarity(src_emb, trg_emb)

    # Find best alignments
    alignments = []
    used_source = set()
    used_target = set()

        # Iterate to find the best alignment for each source-target pair
    while np.any(similarity_matrix > -1):  # Continue as long as there's a valid score
        # Find the maximum similarity
        max_index = np.unravel_index(similarity_matrix.argmax(), similarity_matrix.shape)
        src_idx, trg_idx = max_index

        # Check if the similarity is above the threshold
        if similarity_matrix[src_idx, trg_idx] <= 0.5:  # Adjust threshold as needed
            break  # Stop if no further valid alignments exist

        # Add the alignment
        alignments.append((source_sentences[src_idx], target_sentences[trg_idx]))
        used_source.add(src_idx)
        used_target.add(trg_idx)

        # Invalidate aligned rows and columns by setting similarities to -1
        similarity_matrix[src_idx, :] = -1
        similarity_matrix[:, trg_idx] = -1

    # Handle unaligned sentences
    for i in range(len(source_sentences)):
        if i not in used_source:
            alignments.append((source_sentences[i], ""))  # Source sentence with no target
    for j in range(len(target_sentences)):
        if j not in used_target:
            alignments.append(("", target_sentences[j]))  # Target sentence with no source

    return alignments


def read_sentences_from_file(file_path):
    """
    Read sentences from a file between # Start and # End markers.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        start_idx = lines.index("# Start\n") + 1
        end_idx = lines.index("# End\n")
        sentences = [line.strip() for line in lines[start_idx:end_idx]]
    return sentences


# Main alignment function
def aligner(source_file, target_file):
    """
    Align sentences from the source and target files.
    """
    source_sentences = read_sentences_from_file(source_file)
    target_sentences = read_sentences_from_file(target_file)

    alignments = align_sentences(source_sentences, target_sentences)
    return alignments


def align(book_name, type):
    ch_golden = []
    vn_golden = []
    chinese_pars = []
    sinoviet_pars = []
    translation_pars = []
    to_ret = []
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
    with open(f"./{book_name}/ch_golden.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            ch_golden.append(line)
    with open(f"./{book_name}/vn_golden.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            vn_golden.append(line)
    import os
    # Create tmp_pre to store the preprocessed files
    tmp_dir = f"./tmp_pre/{book_name}"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
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
        source_txt = open(
            f"{tmp_dir}/source_tmp.txt", "r", encoding="utf-8"
        ).readlines()
        source_splitted = split_ch_sentences_keep_space(source_txt)
        # Insert "# Start" and "# End" to the beginning and the end of the source file
        source_processed = ["# Start\n"]
        source_processed.extend(source_splitted + ["\n"])
        source_processed.append("# End")
        with open("./tmp/source.txt", "w", encoding="utf-8") as f:
            for line in source_processed:
                line = line.strip()
                if line != "":
                    f.write(line + "\n")
        # Preprocess the target file
        p = Preprocessor(Language.vietnamese)
        p.segment_files_to_sentences(
            f"{tmp_dir}/target_tmp.txt", "./tmp/target.txt", {"overwrite": True}
        )
        # Insert "# Start" and "# End" to the beginning and the end of the target file
        target_txt = open("./tmp/target.txt", "r", encoding="utf-8").readlines()
        target_processed = ["# Start\n"]
        target_processed.extend(target_txt + ["\n"])
        target_processed.append("\n# End\n")
        # Store the preprocessed target file
        with open("./tmp/target.txt", "w", encoding="utf-8") as f:
            for line in target_processed:
                if line.strip() != "":
                    f.write(line)
        alignments = aligner("./tmp/source.txt", "./tmp/target.txt")
        for a, b in alignments:
            to_ret.append((a, b))
        save_file_name = ""
        if type == "ch_sino":
            save_file_name = "alignments_ch_sino_vec.txt"
        elif type == "ch_vn":
            save_file_name = "alignments_ch_vn_vec.txt"
        with open(f"./{book_name}/{save_file_name}", "a", encoding="utf-8") as f:
            f.write(f"Paragraph {idx}\n")
            print(f"Paragraph {idx}")
            for src, trg in alignments:
                src = re.sub(r"\s+", "", src)
                trg = re.sub(r"\s+", " ", trg)
                f.write(src + "\t" + trg + "\n")
            f.write("\n")
        idx += 1
    return to_ret


if __name__ == "__main__":
    books = ["dvsk"]
    for book in books:
        full_alignments = align(book, "ch_vn")
        # Print 10 first alignments
        ch_golden = []
        vn_golden = []
        with open(f"./{book}/ch_golden.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                ch_golden.append(line)
        with open(f"./{book}/vn_golden.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                vn_golden.append(line)
        import approaches.utils.util as util

        golden = []
        for i in range(len(ch_golden)):
            golden.append((ch_golden[i], vn_golden[i]))
        for i in range(len(full_alignments)):
            full_alignments[i] = (
                full_alignments[i][0] + "\n",
                full_alignments[i][1] + "\n",
            )
        precision = util.precision(full_alignments, golden)
        recall = util.recall(full_alignments, golden)
        f1 = util.f_one(full_alignments, golden)
        print(f"Precision: {precision}, Recall: {recall}, F1: {f1}")
        print(f"Alignments: {len(full_alignments)}")
