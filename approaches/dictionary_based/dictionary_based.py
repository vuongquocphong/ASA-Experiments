from ..utils import util
from nltk.tokenize import word_tokenize
from collections import defaultdict
import os
from .coressponding_pair import bead_score_new

def get_ch_content_words(ch_sentence):
    """
    Get content words from a Chinese sentence.
    """
    return [
        word for word in word_tokenize(ch_sentence)
        if any(
            ord(word) in range(start, end + 1)
            for start, end in [
                (0x4e00, 0x9fff),
                (0xf900, 0xfaff),
                (0x20000, 0x2A6DF)
            ]
        )
    ]

def get_vn_content_words(vn_sentence):
    marks = [',', '.', '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '"', "'", '“', '”', '‘', '’', '...', '…', '–', '-', '—']
    """
    Get content words from a Vietnamese sentence.
    """
    return [word.lower().replace("-", " ") for word in word_tokenize(vn_sentence) if word not in marks]

from typing import List

available_pair = [ (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), (1, 13), (1, 14), (1, 15),
                   (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (2, 12), (2, 13), (2, 14), (2, 15),
                   (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (3, 13), (3, 14), (3, 15), ]

# Scoring Bead
def bead_score_no_remove( Chinese_sentences: List[any], Vietnamese_sentences: List[any], a: int, b: int, x: int, y: int, dictionary: dict ) -> float:
    source_words = set()
    target_words = set()
    for i in range(a - x + 1, a + 1):
        source_words.update( Chinese_sentences[i] )
    for i in range(b - y + 1, b + 1):
        target_words.update( Vietnamese_sentences[i] )
    len_x = len( source_words )
    len_y = len( target_words )
    score = 0
    for source_word in source_words:
        definitions: List[str] = dictionary.get( source_word, None )
        if definitions is None:
            continue
        for definition in definitions:
            for target_word in target_words:
                if definition.find( target_word ) != -1:
                    score += 1
    return score / ( len_x + len_y )

def bead_score_remove( Chinese_sentences: List[any], Vietnamese_sentences: List[any], a: int, b: int, x: int, y: int, dictionary: dict ) -> float:
    source_words = set()
    target_words = set()
    for i in range(a - x + 1, a + 1):
        source_words.update( Chinese_sentences[i] )
    for i in range(b - y + 1, b + 1):
        target_words.update( Vietnamese_sentences[i] )
    len_x = len( source_words )
    len_y = len( target_words )
    score = 0
    target_removed = set()
    for source_word in source_words:
        definitions: List[str] = dictionary.get( source_word, None )
        if definitions is None:
            continue
        for definition in definitions:
            for target_word in target_words - target_removed:
                if definition.find( target_word ) != -1:
                    score += 1
                    target_removed.add( target_word )
    return score / ( len_x + len_y )

# DP function
def BSA( Chinese_sentences: List[any], Vietnamese_sentences: List[any], dictionary) -> List[any]:
    n = len( Chinese_sentences )
    m = len( Vietnamese_sentences )

    Chinese_sentences = [ get_ch_content_words( sentence ) for sentence in Chinese_sentences ]
    Vietnamese_sentences = [ get_vn_content_words( sentence ) for sentence in Vietnamese_sentences ]

    # Add dummy sentences to the beginning of the sentences
    Chinese_sentences = [ None ] + Chinese_sentences
    Vietnamese_sentences = [ None ] + Vietnamese_sentences

    # Initialization
    H = dict()
    H[(0, 0)] = 0

    backtrace = dict()
    backtrace[(0, 0)] = (0, 0)

    for i in range( 0, n + 1):
        H[(i, 0)] = 0
        backtrace[(i, 0)] = (0, 0)
    
    for j in range( 0, m + 1):
        H[(0, j)] = 0
        backtrace[(0, j)] = (0, 0)

    # Calculate
    for a in range( 1, n + 1 ):
        for b in range( 1, m + 1 ):
            # print( "Calculating: ", a, b )
            max_score = 0
            max_x, max_y = 1, 1
            for x, y in available_pair:
                if a - x < 0 or b - y < 0:
                    continue
                # print(bead_score_new( Chinese_sentences, Vietnamese_sentences, a, b, x, y, dictionary ))
                score = H[(a - x, b - y)] + bead_score_new( Chinese_sentences, Vietnamese_sentences, a, b, x, y, dictionary )
                if score > max_score:
                    max_score = score
                    max_x, max_y = x, y
                # Set the threshold
                if max_score - score > 0.1:
                    break
            H[(a, b)] = max_score
            backtrace[(a, b)] = ( a - max_x, b - max_y )

    # Backtrace
    split_position = []
    
    a, b = n, m
    while a > 0 and b > 0:
        a, b = backtrace[(a, b)]
        split_position.append( (a, b) )
        # print( "Splitting point: ", a, b )    
    return split_position[::-1]

def aligner(corpus_x, corpus_y):
    dictionary = util.read_dictionary()
    alignments = []
    for src, trg in zip(util.readFile(corpus_x), util.readFile(corpus_y)):
        assert src[1] == trg[1]
        print(src[1])
        split_position = BSA( src[0], trg[0], dictionary )
        cur_src = 0
        cur_trg = 0
        for a, b in split_position:
            src_sentence = " ".join( src[0][cur_src:a] )
            trg_sentence = " ".join( trg[0][cur_trg:b] )
            # print(src_sentence, trg_sentence)
            if src_sentence != "" and trg_sentence != "":
                alignments.append( ( src_sentence, trg_sentence ) )
            cur_src = a
            cur_trg = b
    return alignments

def main(corpus_x, corpus_y, golden):
    # get the file name of corpus_x and corpus_y
    corpus_x_file: str = os.path.basename(corpus_x)
    if corpus_x_file.find('MT') != -1:
        output_path = "./results/MT-results/lexical-matching/"
    elif corpus_x_file.find('QTTY') != -1:
        output_path = "./results/QTTY-results/lexical-matching/"
    
    output_file_name = os.path.splitext(corpus_x_file)[0] + "-output.txt"
    errors_file_name = os.path.splitext(corpus_x_file)[0] + "-errors.txt"
    dictionary = util.read_dictionary()
    goldens = util.read_golden(golden)
    alignments = aligner(corpus_x, corpus_y)
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

