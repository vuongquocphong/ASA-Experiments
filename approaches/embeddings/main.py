from ..utils import util
from nltk.tokenize import word_tokenize
from collections import defaultdict
import os
import re
from laserembeddings import Laser
from scipy.spatial.distance import cosine

# Initialize LASER
laser = Laser()

def embeddings_score(ch_sentences, vn_sentences, a, b, x, y, dictionary):
    """
    Calculate the score for a pair of sentence beads using LASER embeddings similarity.
    This function replaces or combines the original score with a LASER-based similarity score.
    """

    # Join the source and target segments
    src_segment = " ".join(ch_sentences[a - x : a])
    print("src_segment: ", src_segment)
    trg_segment = " ".join(vn_sentences[b - y : b])
    print("trg_segment: ", trg_segment)
    # Encode the segments using LASER
    src_embedding = laser.embed_sentences(src_segment, lang="zh")
    trg_embedding = laser.embed_sentences(trg_segment, lang="vi")

    # Calculate cosine similarity (1 - cosine distance)
    similarity = 1 - cosine(src_embedding.ravel(), trg_embedding.ravel())

    # Define a weight for combining similarity score with original scoring if needed
    weight = 0.5  # Adjust weight as necessary to balance existing and similarity-based scores
    original_score = (
        0  # Assuming an existing score calculation (replace or combine as needed)
    )

    # Combine the scores (adjust the combination logic as per your use case)
    combined_score = weight * similarity + (1 - weight) * original_score

    return combined_score


def remove_notes(sentence):
    """
    Remove notes in a sentence (inside parentheses). If open but not close, remove from the open to the end of the sentence.
    If close but not open, remove from the beginning of the sentence to the close.
    Also, ensure there are no multiple adjacent spaces.
    """
    result = []
    open_parentheses = 0
    has_unmatched_close = False

    for char in sentence:
        if char == "(":
            if open_parentheses == 0:
                has_unmatched_close = (
                    False  # Reset in case we found unmatched close earlier
                )
            open_parentheses += 1
        elif char == ")":
            open_parentheses -= 1
            if open_parentheses < 0:
                has_unmatched_close = True
                open_parentheses = 0
                result = []  # Reset the result if we found unmatched close
                has_unmatched_close = False
            continue  # Do not add this character to the result if we're closing a parenthesis
        if open_parentheses == 0 and not has_unmatched_close:
            result.append(char)

    # If unmatched closing parenthesis was found, return only the part before it
    cleaned_sentence = "".join(result)

    # Replace multiple spaces with a single space
    cleaned_sentence = re.sub(r"\s+", " ", cleaned_sentence)

    return cleaned_sentence.strip()


def get_ch_content_words(ch_sentence):
    """
    Get content words from a Chinese sentence.
    """
    tokens = word_tokenize(remove_notes(ch_sentence))
    res = []
    for token in tokens:
        if len(token) > 1:
            continue
        if (
            ord(token) in range(0x4E00, 0x9FFF)
            or ord(token) in range(0xF900, 0xFAFF)
            or ord(token) in range(0x20000, 0x2A6DF)
        ):
            res.append(token)
    return res
    # return [
    #     word for word in word_tokenize(remove_notes(ch_sentence))
    #     if any(
    #         ord(word) in range(start, end + 1)
    #         for start, end in [
    #             (0x4e00, 0x9fff),
    #             (0xf900, 0xfaff),
    #             (0x20000, 0x2A6DF)
    #         ]
    #     )
    # ]


def get_vn_content_words(vn_sentence):
    """
    Get content words from a Vietnamese sentence.
    """
    marks = [
        ",",
        ".",
        "?",
        "!",
        ":",
        ";",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        '"',
        "'",
        "“",
        "”",
        "‘",
        "’",
        "...",
        "…",
        "–",
        "-",
        "—",
    ]
    return [
        word
        for word in word_tokenize(remove_notes(vn_sentence.lower().replace("-", " ")))
        if word not in marks
    ]


from typing import List

threshold = 0.03
callback_X = 3
callback_Y = 0


# DP function
def BSA(
    Chinese_sentences: List[any], Vietnamese_sentences: List[any], dictionary
) -> List[any]:
    n = len(Chinese_sentences)
    m = len(Vietnamese_sentences)

    # Initialization
    H = dict()
    H[(0, 0)] = 0

    backtrace = dict()
    backtrace[(0, 0)] = (0, 0)

    for i in range(0, n + 1):
        H[(i, 0)] = 0
        backtrace[(i, 0)] = (0, 0)

    for j in range(0, m + 1):
        H[(0, j)] = 0
        backtrace[(0, j)] = (0, 0)

    # Calculate
    for a in range(1, n + 1):
        for b in range(1, m + 1):

            max_score = 0
            max_x, max_y = 1, 1

            # The case when x, y > 0
            for x in range(1, a + 1):
                if a - x < 0:
                    continue
                if x - max_x >= callback_X:
                    continue

                preY = max_y

                # For safety purpose
                for y in range(max(preY - callback_Y, 1), preY):
                    if b - y < 0:
                        continue
                    score = H[(a - x, b - y)] + embeddings_score(
                        Chinese_sentences, Vietnamese_sentences, a, b, x, y, dictionary
                    )
                    if score > max_score:
                        max_score = score
                        max_x, max_y = x, y

                for y in range(preY, b + 1):
                    if b - y < 0:
                        continue
                    score = H[(a - x, b - y)] + embeddings_score(
                        Chinese_sentences, Vietnamese_sentences, a, b, x, y, dictionary
                    )
                    if score > max_score:
                        max_score = score
                        max_x, max_y = x, y
                    if max_score - score > threshold:
                        break

            # The case when y = 0
            for x in range(1, a + 1):
                if a - x < 0:
                    continue
                if H[(a - x, b)] > max_score:
                    max_score = H[(a - x, b)]
                    max_x, max_y = x, 0

            # The case when x = 0
            for y in range(1, b + 1):
                if b - y < 0:
                    continue
                if H[(a, b - y)] > max_score:
                    max_score = H[(a, b - y)]
                    max_x, max_y = 0, y

            # Update H and backtrace
            H[(a, b)] = max_score
            backtrace[(a, b)] = (a - max_x, b - max_y)

    # Backtrace
    a, b = n, m
    split_position = [(a, b)]

    while a > 0 and b > 0:
        a, b = backtrace[(a, b)]
        split_position.append((a, b))

    return split_position[::-1]


def aligner(corpus_x, corpus_y, dictionary):
    alignments = []
    for src, trg in zip(util.readFile(corpus_x), util.readFile(corpus_y)):
        assert src[1] == trg[1]
        print(src[1])
        split_position = BSA(src[0], trg[0], dictionary)
        cur_src = 0
        cur_trg = 0
        for a, b in split_position:
            src_sentence = " ".join(src[0][cur_src:a])
            trg_sentence = " ".join(trg[0][cur_trg:b])
            # print(src_sentence, trg_sentence)
            if src_sentence != "" and trg_sentence != "":
                alignments.append((src_sentence, trg_sentence))
            cur_src = a
            cur_trg = b
    return alignments


def main(corpus_x, corpus_y, golden):
    # get the file name of corpus_x and corpus_y
    output_path = ""
    corpus_x_file: str = os.path.basename(corpus_x)
    if corpus_x.find("MT") != -1:
        output_path = "./results/MT-results/lexical-matching/"
    elif corpus_x.find("QTTY") != -1:
        output_path = "./results/QTTY-results/lexical-matching/"

    output_file_name = os.path.splitext(corpus_x_file)[0] + "-output.txt"
    errors_file_name = os.path.splitext(corpus_x_file)[0] + "-errors.txt"
    dictionary = util.read_dictionary()
    with open("./dictionary.txt", "w", encoding="utf-8") as f:
        for key in dictionary:
            f.write(str(key))
            f.write("\t")
            f.write(",".join(dictionary[key]))
            f.write("\n")
    goldens = util.read_golden(golden)
    alignments = aligner(corpus_x, corpus_y, dictionary)
    with open(output_path + output_file_name, "w", encoding="utf8") as f:
        for sent_x, sent_y in alignments:
            f.write(sent_x + "\t" + sent_y + "\n")
    with open(output_path + errors_file_name, "w", encoding="utf8") as f:
        for sent_x, sent_y in alignments:
            if (sent_x, sent_y) not in goldens:
                f.write(sent_x + "\t" + sent_y + "\n")
    print(corpus_x_file)
    print("Dictionary length: ", len(dictionary))
    print("Precision: ", util.precision(alignments, goldens))
    print("Recall: ", util.recall(alignments, goldens))
    print("F1: ", util.f_one(alignments, goldens))
    print("Alignment: ", len(alignments))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        sys.stderr.write("Usage: %srcfile corpus.x corpus.y gold\n")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
