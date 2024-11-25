import os
import re
from ..utils import util
from laserembeddings import Laser
from scipy.spatial.distance import cosine
from nltk.tokenize import word_tokenize
import time
from typing import List

# Initialize LASER
laser = Laser()

def embeddings_score(ch_sentences, vn_sentences, a, b, x, y):
    """
    Calculate the score for a pair of sentence beads using LASER embeddings similarity.
    """
    # Join the source and target segments
    src_segment = " ".join(ch_sentences[a - x : a]).strip()
    trg_segment = " ".join(vn_sentences[b - y : b]).strip()

    # Skip empty segments to reduce unnecessary computation
    if not src_segment or not trg_segment:
        return 0

    # Encode the segments using LASER
    src_embedding = laser.embed_sentences(src_segment, lang="zh")
    trg_embedding = laser.embed_sentences(trg_segment, lang="vi")

    # Calculate cosine similarity (1 - cosine distance)
    similarity = 1 - cosine(src_embedding.ravel(), trg_embedding.ravel())

    # Define a weight for combining similarity score with original scoring if needed
    weight = 0.5  # Adjust weight as necessary to balance existing and similarity-based scores
    original_score = 0  # Assuming an existing score calculation (replace or combine as needed)
    combined_score = weight * similarity + (1 - weight) * original_score
    return combined_score

def remove_notes(sentence):
    """
    Remove notes in a sentence (inside parentheses).
    """
    result = []
    open_parentheses = 0
    for char in sentence:
        if char == "(":
            open_parentheses += 1
        elif char == ")":
            open_parentheses -= 1
            continue
        if open_parentheses == 0:
            result.append(char)
    cleaned_sentence = "".join(result)
    cleaned_sentence = re.sub(r"\s+", " ", cleaned_sentence)
    return cleaned_sentence.strip()

def get_ch_content_words(ch_sentence):
    tokens = word_tokenize(remove_notes(ch_sentence))
    return [token for token in tokens if len(token) == 1 and (
        0x4E00 <= ord(token) <= 0x9FFF or 
        0xF900 <= ord(token) <= 0xFAFF or 
        0x20000 <= ord(token) <= 0x2A6DF)]

def get_vn_content_words(vn_sentence):
    marks = {",", ".", "?", "!", ":", ";", "(", ")", "[", "]", "{", "}", '"', "'", "“", "”", "‘", "’", "...", "…", "–", "-", "—"}
    return [word for word in word_tokenize(remove_notes(vn_sentence.lower().replace("-", " "))) if word not in marks]

threshold = 0.03
callback_X = 3
callback_Y = 0

def BSA(Chinese_sentences: List[str], Vietnamese_sentences: List[str]) -> List[any]:
    n, m = len(Chinese_sentences), len(Vietnamese_sentences)
    Chinese_sentences = [""] + Chinese_sentences
    Vietnamese_sentences = [""] + Vietnamese_sentences
    H, backtrace = dict(), dict()
    H[(0, 0)], backtrace[(0, 0)] = 0, (0, 0)

    for i in range(n + 1):
        H[(i, 0)], backtrace[(i, 0)] = 0, (0, 0)
    for j in range(m + 1):
        H[(0, j)], backtrace[(0, j)] = 0, (0, 0)

    for a in range(1, n + 1):
        for b in range(1, m + 1):
            max_score, max_x, max_y = 0, 1, 1
            for x in range(1, min(a, callback_X) + 1):
                for y in range(1, min(b, callback_Y) + 1):
                    score = H[(a - x, b - y)] + embeddings_score(Chinese_sentences, Vietnamese_sentences, a, b, x, y)
                    if score > max_score:
                        max_score, max_x, max_y = score, x, y

            for x in range(1, min(a, callback_X) + 1):
                if H[(a - x, b)] > max_score:
                    max_score, max_x, max_y = H[(a - x, b)], x, 0

            for y in range(1, min(b, callback_Y) + 1):
                if H[(a, b - y)] > max_score:
                    max_score, max_x, max_y = H[(a, b - y)], 0, y

            H[(a, b)], backtrace[(a, b)] = max_score, (a - max_x, b - max_y)

    a, b, split_position = n, m, [(n, m)]
    while a > 0 and b > 0:
        a, b = backtrace[(a, b)]
        split_position.append((a, b))
    return split_position[::-1]

def aligner(corpus_x, corpus_y):
    alignments = []
    for src, trg in zip(util.readFile(corpus_x), util.readFile(corpus_y)):
        assert src[1] == trg[1]
        split_position = BSA(src[0], trg[0])
        cur_src, cur_trg = 0, 0
        for a, b in split_position:
            src_sentence = " ".join(src[0][cur_src:a]).strip()
            trg_sentence = " ".join(trg[0][cur_trg:b]).strip()
            if src_sentence and trg_sentence:
                alignments.append((src_sentence, trg_sentence))
            cur_src, cur_trg = a, b
    return alignments

def main(corpus_x, corpus_y, golden):
    alignments = aligner(corpus_x, corpus_y)
    goldens = util.read_golden(golden)
    precision = util.precision(alignments, goldens)
    recall = util.recall(alignments, goldens)
    f1 = util.f_one(alignments, goldens)
    print(f"Precision: {precision}, Recall: {recall}, F1: {f1}")
    print(f"Alignments: {len(alignments)}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        sys.stderr.write("Usage: %srcfile corpus.x corpus.y gold\n")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
