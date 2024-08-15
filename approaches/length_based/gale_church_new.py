# -*- coding: utf8 -*-

"""
An implementation of Gale-Church algorithm with variable mean/variance.

GaChalign-v1.1: Fixed some bugs, compacted the code
Fixed some bugs, now the code runs on command line. 
- removed the evaluation modules, users just want to align their documents.
- simplified gacha to the best configuration (i.e. optimized mean with character).
- removed demo, follow the homepage instructions for usage.
"""

import math, codecs
from collections import defaultdict
from ..utils import util
import pandas as pd

output_path = "./results/MT-results/length-based/modified/"
output_file_name = "MT3-output.txt"
errors_file_name = "MT3-errors.txt"

try:
    import scipy.stats
    norm_logsf = scipy.stats.norm.logsf
except ImportError:
    from minimath import norm_cdf, norm_logsf

LOG2 = math.log(2)

BEAD_COSTS = {
    (1, 1): 0,
    (2, 1): 230,
    (1, 2): 230,
    (0, 1): 450,
    (1, 0): 450,
    (2, 2): 440,
}

def length_cost(sx, sy, mean_xy, variance_xy):
    """
    Calculate length cost given 2 sentence. Lower cost = higher prob.

    The original Gale-Church (1993:pp. 81) paper considers l2/l1 = 1 hence:
     delta = (l2-l1*c)/math.sqrt(l1*s2)

    If l2/l1 != 1 then the following should be considered:
     delta = (l2-l1*c)/math.sqrt((l1+l2*c)/2 * s2)
     substituting c = 1 and c = l2/l1, gives the original cost function.
    """
    lx, ly = sum(sx), sum(sy)
    m = (lx + ly * mean_xy) / 2
    try:
        delta = (lx - ly * mean_xy) / math.sqrt(m * variance_xy)
    except ZeroDivisionError:
        return float("-inf")
    return -100 * (LOG2 + norm_logsf(abs(delta)))

def _align(x, y, mean_xy, variance_xy, bead_costs):
    """
    The minimization function to choose the sentence pair with
    cheapest alignment cost.
    """
    m = {}
    for i in range(len(x) + 1):
        for j in range(len(y) + 1):
            if i == j == 0:
                m[0, 0] = (0, 0, 0)
            else:
                m[i, j] = min(
                    (
                        m[i - di, j - dj][0]
                        + length_cost(
                            x[i - di : i], y[j - dj : j], mean_xy, variance_xy
                        )
                        + bead_cost,
                        di,
                        dj,
                    )
                    for (di, dj), bead_cost in BEAD_COSTS.items()
                    if i - di >= 0 and j - dj >= 0
                )

    i, j = len(x), len(y)
    while True:
        (c, di, dj) = m[i, j]
        if di == dj == 0:
            break
        yield (i - di, i), (j - dj, j)
        i -= di
        j -= dj

def sent_length(sentence):
    """Returns sentence length without spaces."""
    return sum(1 for c in sentence if c != " ")

def align(sx, sy, mean_xy, variance_xy, bc):
    """Main alignment function."""
    cx = list(map(sent_length, sx))
    cy = list(map(sent_length, sy))
    for (i1, i2), (j1, j2) in reversed(list(_align(cx, cy, mean_xy, variance_xy, bc))):
        yield " ".join(sx[i1:i2]), " ".join(sy[j1:j2])

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

def calculateMean(srcfile, trgfile):
    """Calculate mean length: mean = len(trgfile) / len(srcfile)."""
    srcfile = codecs.open(srcfile, "r", "utf8").read().replace(" ", "")
    trgfile = codecs.open(trgfile, "r", "utf8").read().replace(" ", "")
    return len(trgfile) / float(len(srcfile))

def calculateVariance(srcfile, trgfile):
    """Calculates covariance between len(srcfile) and len(trgfile)."""
    try:
        from pylab import polyfit
    except ImportError:
        import os
        os.system("sudo pip install -U --force-reinstall scipy")
    diffsquares = [
        math.pow(
            len("".join(src[0]).replace(" ", ""))
            - len("".join(trg[0]).replace(" ", "")),
            2,
        )
        for src, trg in zip(readFile(srcfile), readFile(trgfile))
    ]
    src_paragraph_len = [len(i[0]) for i in readFile(srcfile)]
    (m, _) = polyfit(src_paragraph_len, diffsquares, 1)
    return m

def classify_alignments(golden_file):
    """Classify and count alignment types using the golden file in xlsx format"""
    alignment_counts = defaultdict(int)

    # Read the Excel file
    df = pd.read_excel(golden_file, header=None)

    # Assuming the Excel file has two columns: 'Source' and 'Target'
    for src, trg in zip(df[0], df[2]):

        len_x = len(src.replace(" ", ""))
        len_y = len(trg.replace(" ", ""))

        if len_x > 0 and len_y > 0:
            if len_x == len_y:
                alignment_counts[(1, 1)] += 1
            elif len_x > len_y:
                alignment_counts[(2, 1)] += 1
            else:
                alignment_counts[(1, 2)] += 1
        elif len_x == 0:
            alignment_counts[(0, 1)] += 1
        elif len_y == 0:
            alignment_counts[(1, 0)] += 1

    return alignment_counts

def estimate_costs(alignment_counts):
    """Estimate costs from alignment counts"""
    total_alignments = sum(alignment_counts.values())
    bead_costs = {}
    for (di, dj), count in alignment_counts.items():
        probability = count / total_alignments
        z_score = -math.log(probability)
        cost = int(z_score * 100)
        bead_costs[(di, dj)] = cost
    return bead_costs

def main(corpusx, corpusy, golden, mean='gacha', variance=6.8, bc=BEAD_COSTS):
    if mean == "gacha":
        mean = calculateMean(corpusx, corpusy)
    mean, variance = list(map(float, [mean, variance]))

    # Calculate BEAD_COSTS
    alignment_counts = classify_alignments(golden)
    bead_costs = estimate_costs(alignment_counts)

    # read len of golden
    gold = util.read_golden(golden)
    alignment = []
    errors = []

    for src, trg in zip(readFile(corpusx), readFile(corpusy)):
        assert src[1] == trg[1]
        # print(src[1])
        # Output to file
        for sentence_x, sentence_y in align(src[0], trg[0], mean, variance, bead_costs):
            alignment.append((sentence_x, sentence_y))
            if (sentence_x, sentence_y) not in gold:
                errors.append((sentence_x, sentence_y))
    with open(output_path + output_file_name, "w", encoding="utf8") as f:
        for sent_x, sent_y in alignment:
            f.write(sent_x + "\t" + sent_y + "\n")
    with open(output_path + errors_file_name, "w", encoding="utf8") as f:
        for sent_x, sent_y in errors:
            f.write(sent_x + "\t" + sent_y + "\n")
                
    print("Precision: ", util.precision(alignment, gold))
    print("Recall: ", util.recall(alignment, gold))
    print("F1: ", util.f_one(alignment, gold))
    print("Alignment: ", len(alignment))

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        print("Usage: python gacha.py <corpus_x> <corpus_y> <golden> <mean>")
        sys.exit(1)

    corpusx = sys.argv[1]
    corpusy = sys.argv[2]
    golden = sys.argv[3]
    mean = sys.argv[4]

    main(corpusx, corpusy, golden, mean)
