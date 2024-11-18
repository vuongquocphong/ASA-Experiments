# each par start with #{num}, contains num sentences
# read the file, concatenate the sentences into paragraphs

def split_paragraphs(input_txt):
    """
    Split Chinese paragraphs from a file.
    """
    paragraphs = []
    paragraph = ""
    for line in input_txt:
        line = line.strip()
        if line == "":
            continue
        if line[0] == "#":
            if paragraph != "":
                paragraphs.append(paragraph)
                paragraph = ""
        else:
            if paragraph != "":
                paragraph += " "
            paragraph += line
    if paragraph != "":
        paragraph.replace(" ", "")
        paragraphs.append(paragraph)
    return paragraphs

if __name__ == "__main__":
    import sys
    import os
    if len(sys.argv) < 2:
        print("Usage: python snt2par.py <input_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print("File not found: {}".format(input_file))
        sys.exit(1)
    with open(input_file, "r", encoding="utf-8") as f:
        input_txt = f.readlines()
    paragraphs = split_paragraphs(input_txt)
    with open(input_file + ".par", "w", encoding="utf-8") as f:
        for paragraph in paragraphs:
            f.write(paragraph + "\n")