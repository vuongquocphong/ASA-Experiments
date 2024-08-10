import nltk
import pandas as pd
import codecs

def read_textfile(path):
    """
    Read a text file and return its content as a list of strings
    """
    with open(path, 'r', encoding="utf8") as f:
        return f.read().splitlines()
    
def read_golden(path):
    """
    Read an excel file, which contains 3 columns: SinoNom, SinoVietnamse, Vietnamese
    Read the first and the third columns, and return the content as a list of tuples
    Read mode: no header
    """
    df = pd.read_excel(path, header=None)
    # Trim the strings
    df[0] = df[0].str.strip()
    df[2] = df[2].str.strip()
    return list(zip(df[0], df[2]))

def read_dictionary():
    """
    Read a dictionary of word pairs from an excel file (the first and the second columns)
    """
    dictionary_folder = "./data/dictionaries/"
    dictionary = dict()
    # Read all file in the dictionary folder
    import os
    files = os.listdir(dictionary_folder)
    for file in files:
        if file.endswith(".xlsx"):
            df = pd.read_excel(dictionary_folder + file)
            word_pairs = set(zip(df['Chinese'], df['Vietnamese'].str.strip().str.lower()))
            for pair in word_pairs:
                if pair[0] in dictionary:
                    dictionary[pair[0]].add(pair[1])
                else:
                    dictionary[pair[0]] = {pair[1]}
    return dictionary

def readFile(filename):
    """Yields sections off textfiles delimited by '#'."""
    paragraph = []
    doc = ""
    for line in codecs.open(filename, "r", "utf8"):
        if line.strip() == "#" or line[0] == "#":
            if paragraph != [] and doc != "":
                yield paragraph, doc
                paragraph = []
            doc = line.strip()  # line.strip().rpartition('/')[-1]
        else:
            paragraph.append(line.strip())
    if paragraph != [] and doc != "":
        yield paragraph, doc

def read_parallel_corpus(file_x, file_y):
    """Yields parallel paragraphs from two files."""
    paragraphs_x = list(readFile(file_x))
    paragraphs_y = list(readFile(file_y))
    
    min_len = min(len(paragraphs_x), len(paragraphs_y))
    
    for i in range(min_len):
        src_paragraph, _ = paragraphs_x[i]
        trg_paragraph, _ = paragraphs_y[i]
        yield "".join(src_paragraph), "".join(trg_paragraph)

def save_alignment(alignment, output_path):
    """
    Save the alignment to a file
    """
    with open(output_path, 'w', encoding="utf8") as f:
        for a, b in alignment:
            f.write(f'{a}\t{b}\n')

def intersect_count(alignment, gold):
    """
    Count the number of intersecting pairs between the alignment and the gold standard
    """
    intersect = 0
    for a, b in alignment:
        if (a, b) in gold:
            intersect += 1
    return intersect

def precision(alignment, gold):
    """
    Calculate the precision of the alignment
    """
    if len(alignment) == 0:
        return 0
    return intersect_count(alignment, gold) / len(alignment)

def recall(alignment, gold):
    """
    Calculate the recall of the alignment
    """
    if len(gold) == 0:
        return 0
    return intersect_count(alignment, gold) / len(gold)

def f_beta(alignment, gold, beta=1):
    """
    Calculate the F-beta score of the alignment
    """
    p = precision(alignment, gold)
    r = recall(alignment, gold)
    if p + r == 0:
        return 0
    return (1 + beta**2) * (p * r) / ((beta**2 * p) + r)

def f_one(alignment, gold):
    """
    Calculate the F1 score of the alignment
    """
    return f_beta(alignment, gold, beta=1)

def aer(alignment, gold):
    """
    Calculate the Alignment Error Rate (AER) of the alignment
    """
    return 1 - (intersect_count(alignment, gold) / (len(alignment) + len(gold)))