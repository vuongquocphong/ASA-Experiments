import nltk

def readfile(file_path):
    """
    Read a file and tokenize it into sentences
    """
    with open(file_path, 'r') as f:
        text = f.read()
    return nltk.sent_tokenize(text)

def save_alignment(alignment, output_path):
    """
    Save the alignment to a file
    """
    with open(output_path, 'w') as f:
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
    return intersect_count(alignment, gold) / len(gold)

def f_beta(alignment, gold, beta=1):
    """
    Calculate the F-beta score of the alignment
    """
    p = precision(alignment, gold)
    r = recall(alignment, gold)
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