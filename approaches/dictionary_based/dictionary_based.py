from ..utils import util
from nltk.tokenize import word_tokenize
from collections import defaultdict
import os
import re
from .coressponding_pair import bead_score_new

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
        if char == '(':
            if open_parentheses == 0:
                has_unmatched_close = False  # Reset in case we found unmatched close earlier
            open_parentheses += 1
        elif char == ')':
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
    cleaned_sentence = ''.join(result)

    # Replace multiple spaces with a single space
    cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence)
    
    return cleaned_sentence.strip()


def get_ch_content_words(ch_sentence):
    """
    Get content words from a Chinese sentence.
    """
    return [
        word for word in word_tokenize(remove_notes(ch_sentence))
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
    return [word for word in word_tokenize(remove_notes(vn_sentence.lower().replace("-", " "))) if word not in marks]

from typing import List

threshold = 0.05

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

            max_score = 0
            max_x, max_y = 1, 1
            for x in range( 1, a + 1 ):
                if a - x < 0: continue
                if x - max_x >= 3: continue
                for y in range( max( max_y - 5, 1 ), b + 1 ):
                    if b - y < 0: continue
                    score = H[(a - x, b - y)] + bead_score_new( Chinese_sentences, Vietnamese_sentences, a, b, x, y, dictionary )
                    if score > max_score:
                        max_score = score
                        max_x, max_y = x, y
                    if max_score - score > threshold: break

            H[(a, b)] = max_score
            backtrace[(a, b)] = (a - max_x, b - max_y)

    # Backtrace
    a, b = n, m
    split_position = [(a, b)]
    
    while a > 0 and b > 0:
        a, b = backtrace[(a, b)]
        split_position.append( (a, b) )

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
    output_path = ""
    corpus_x_file: str = os.path.basename(corpus_x)
    if corpus_x.find('MT') != -1:
        output_path = "./results/MT-results/lexical-matching/"
    elif corpus_x.find('QTTY') != -1:
        output_path = "./results/QTTY-results/lexical-matching/"
    
    output_file_name = os.path.splitext(corpus_x_file)[0] + "-output.txt"
    errors_file_name = os.path.splitext(corpus_x_file)[0] + "-errors.txt"
    dictionary = util.read_dictionary()
    with open('./dictionary.txt', 'w', encoding='utf-8') as f:
        for key in dictionary:
            f.write(str(key))
            f.write('\t')
            f.write(','.join(dictionary[key]))
            f.write('\n')
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

