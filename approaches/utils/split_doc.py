import os

def main(input_file, n):
    """
    Insert # {order} for every n lines
    """
    with open(input_file, "r", encoding="utf8") as f:
        lines = f.readlines()
    
    # get the directory of the input file
    directory = os.path.dirname(input_file)
    # get the filename of the input file
    filename = os.path.basename(input_file)
    # get the filename without extension
    filename_no_ext = os.path.splitext(filename)[0]
    # create a new filename
    new_filename = os.path.join(directory, filename_no_ext + "_splitted.txt")

    with open(new_filename, "w", encoding="utf8") as f:
        for i, line in enumerate(lines):
            if i % n == 0:
                f.write(f"# {i}\n")
            f.write(line)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python split_doc.py input_file n")
        sys.exit(1)

    input_file = sys.argv[1]
    n = int(sys.argv[2])
    main(input_file, n)