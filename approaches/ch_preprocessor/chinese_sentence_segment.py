ch_marks = ["。", "；", "，", "：", "？", "！", "!", ":", "、", "?"]

def split_ch_sentences(file_path):
    """
    Split Chinese sentences from a file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    sentences = []
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        for mark in ch_marks:
            line = line.replace(mark, mark + "\n")
        sentences.extend(line.split("\n"))
    return sentences

print(split_ch_sentences("./approaches/ch_preprocessor/test.txt"))