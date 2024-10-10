import os
import re
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ..utils import util


model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

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

def LM(src_paragraph: List[str], trg_paragraph: List[str]) -> List[Tuple[int, int]]:
    # Preprocess the source and target paragraphs
    src_paragraph = [remove_notes(sent) for sent in src_paragraph]
    trg_paragraph = [remove_notes(sent) for sent in trg_paragraph]
    
    # Encode sentences to get their embeddings
    src_embeddings = model.encode(src_paragraph, convert_to_tensor=True)
    trg_embeddings = model.encode(trg_paragraph, convert_to_tensor=True)
    
    n = len(src_paragraph)
    m = len(trg_paragraph)
    
    # Initialize DP table H and backtrace dictionary
    H = dict()
    backtrace = dict()
    
    # Add dummy sentences at index 0
    H[(0, 0)] = 0
    backtrace[(0, 0)] = (0, 0)
    
    # Initialize the first row and column of the DP table
    for i in range(1, n + 1):
        H[(i, 0)] = 0
        backtrace[(i, 0)] = (i - 1, 0)
    
    for j in range(1, m + 1):
        H[(0, j)] = 0
        backtrace[(0, j)] = (0, j - 1)

    # Calculate the DP table
    for a in range(1, n + 1):
        for b in range(1, m + 1):
            max_score = 0
            max_x, max_y = 1, 1

            # Compare sentences based on their embeddings
            for x in range(1, a + 1):
                for y in range(1, b + 1):
                    score = cosine_similarity(
                        src_embeddings[a - x : a].cpu().numpy(),  # Source range
                        trg_embeddings[b - y : b].cpu().numpy()   # Target range
                    ).mean()
                    
                    total_score = H[(a - x, b - y)] + score
                    
                    if total_score > max_score:
                        max_score = total_score
                        max_x, max_y = x, y

            # Update the DP table and backtrace
            H[(a, b)] = max_score
            backtrace[(a, b)] = (a - max_x, b - max_y)

    # Backtrace to get the split positions
    a, b = n, m
    split_positions = [(a, b)]
    
    while a > 0 and b > 0:
        a, b = backtrace[(a, b)]
        split_positions.append((a, b))
    
    return split_positions[::-1]

def aligner(corpus_x, corpus_y):
    alignments = []
    for src, trg in zip(util.readFile(corpus_x), util.readFile(corpus_y)):
        assert src[1] == trg[1]
        print(src[1])
        split_position = LM(src[0], trg[0])
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
        output_path = "./results/MT-results/LM/"
    elif corpus_x.find('QTTY') != -1:
        output_path = "./results/QTTY-results/LM/"
    
    output_file_name = os.path.splitext(corpus_x_file)[0] + "-output.txt"
    errors_file_name = os.path.splitext(corpus_x_file)[0] + "-errors.txt"
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
