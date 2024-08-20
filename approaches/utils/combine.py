import os

def combine(folder_path):
    # Get all files in the folder, and append to a combine.txt file
    output_file_path = os.path.join(folder_path, "combine.txt")
    with open(output_file_path, "w", encoding="utf-8") as f:
        index = 0
        for file in os.listdir(folder_path):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f2:
                content = f2.readlines()
                for line in content:
                    # if last line, add a newline
                    if line == content[-1] and line[-1] != "\n":
                        f.write(line + "\n")
                    elif line[0] == "#":
                        f.write(f'# {index}\n')
                        index += 1
                    else:
                        f.write(line)
                

# =====================================================================================

if __name__ == "__main__":
    import sys

    folder_path = sys.argv[1]

    combine(folder_path)