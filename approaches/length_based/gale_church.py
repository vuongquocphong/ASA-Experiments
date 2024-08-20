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
from ..utils import util

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


def calculateMean(srcfile, trgfile):
    """Caluclate mean length: mean = len(trgfile) / len(srcfile)."""
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

def aligner(corpus_x, corpus_y, mean=1.0, variance=6.8, bc=BEAD_COSTS):
    alignments = []
    for src, trg in zip(util.readFile(corpus_x), util.readFile(corpus_y)):
        assert src[1] == trg[1]
        for sentence_x, sentence_y in align(src[0], trg[0], mean, variance, bc):
            alignments.append((sentence_x, sentence_y))
    return alignments

def main(corpusx, corpusy, golden, mean=1.0, variance=6.8, bc=BEAD_COSTS):
    output_path = ""
    if corpusx.find("MT") != -1:
        output_path = "./results/MT-results/length-based/original/"
    elif corpusx.find("QTTY") != -1:
        output_path = "./results/QTTY-results/length-based/original/"
    import os
    extract_file_name = os.path.basename(corpusx).split(".")[0]
    errors_file_name = extract_file_name + "-errors.txt"
    output_file_name = extract_file_name + "-output.txt"

    if mean == "gacha":
        mean = calculateMean(corpusx, corpusy)
        variance = calculateVariance(corpusx, corpusy)
    mean, variance = list(map(float, [mean, variance]))
    
    # read len of golden
    gold = util.read_golden(golden)
    alignments = []

    for src, trg in zip(readFile(corpusx), readFile(corpusy)):
        assert src[1] == trg[1]
        print(src[1])
        # for sentence_x, sentence_y in align(src[0], trg[0], mean, variance, bc):
        #     print(sentence_x + "\t" + sentence_y)
        # Output to file
        for sentence_x, sentence_y in align(src[0], trg[0], mean, variance, bc):
            alignments.append((sentence_x, sentence_y))
    with open(output_path + output_file_name, "w", encoding="utf8") as f:
        for sent_x, sent_y in alignments:
            f.write(sent_x + "\t" + sent_y + "\n")
    with open(output_path + errors_file_name, "w", encoding="utf8") as f:
        for sent_x, sent_y in alignments:
            if (sent_x, sent_y) not in gold:
                f.write(sent_x + "\t" + sent_y + "\n")

    print("Precision: ", util.precision(alignments, gold))
    print("Recall: ", util.recall(alignments, gold))
    print("F1: ", util.f_one(alignments, gold))
    print("Alignment: ", len(alignments))



if __name__ == "__main__":
    import sys

    if len(sys.argv) not in list(range(4, 7)):
        sys.stderr.write(
            "Usage: %srcfile corpus.x corpus.y gold"
            "(mean) (variance) (bead_costs)\n" % sys.argv[0]
        )
        sys.exit(1)
    main(*sys.argv[1:])
