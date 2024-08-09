import nltk
import pandas as pd

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

def read_dictionary(file_path):
    """
    Read a dictionary of word pairs from an excel file (the first and the second columns)
    """
    df = pd.read_excel(file_path)
    return list(zip(df.iloc[:, 0], df.iloc[:, 1]))

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