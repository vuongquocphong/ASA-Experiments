from approaches.utils import util

def eval(alignments_path, golden_path):
    alignments = []
    with open(alignments_path, 'r', encoding='utf-8') as f:
        data = f.readlines()
        for i in range(len(data)):
            data[i] = data[i].strip()
            first_part = ""
            second_part = ""
            for char in data[i]:
                if char == "\t":
                    second_part = data[i][data[i].index(char) + 1:]
                    break
                first_part += char
            alignments.append((first_part, second_part))
    # for i in range(len(alignments)):
    #     alignments[i][0] = alignments[i][0].strip()
    #     # alignments[i][0] = ' '.join(alignments[i][0].split())
    #     alignments[i][1] = alignments[i][1].strip()
    
    golden = []
    with open(golden_path, "r", encoding="utf-8") as f:
        data = f.readlines()
        for i in range(len(data)):
            data[i] = data[i].strip()
            first_part = ""
            second_part = ""
            for char in data[i]:
                if char == "\t":
                    second_part = data[i][data[i].index(char) + 1:]
                    break
                first_part += char
            golden.append((first_part, second_part))

    match = 0
    for alignment in alignments:
        for gold in golden:
            if alignment[0] == gold[0] and alignment[1] == gold[1]:
                match += 1
                break

    precision = match / len(alignments) if len(alignments) > 0 else 0
    recall = match / len(golden) if len(golden) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    with open("result.txt", "a", encoding="utf-8") as f:
        f.write(f"Align with trans source snts using bertalign baseline" + "\n")
        f.write("Precision: " + str(precision) + "\n")
        f.write("Recall: " + str(recall) + "\n")
        f.write("F1: " + str(f1) + "\n")
        f.write("------------------\n")

if __name__ == '__main__':
    import sys
    alignments_path = sys.argv[1]
    golden_path = sys.argv[2]
    eval(alignments_path, golden_path)
