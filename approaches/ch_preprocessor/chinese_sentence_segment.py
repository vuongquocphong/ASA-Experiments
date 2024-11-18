ch_marks = ["。", "；", "？", "！", "!", "?", "."]

def split_ch_sentences(input_txt):
    """
    Split Chinese sentences from a file.
    """
    sentences = []
    for line in input_txt:
        line = line.replace(" ", "")
        line = ' '.join(line)
        line = line.strip()
        if line == "":
            continue
        for mark in ch_marks:
            line = line.replace(mark, mark + "\n")
        sentences.extend(line.split("\n"))
    return sentences