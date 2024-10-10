excel_file = "./thanglong-GOLD.xlsx"

# Read data from excel file
import pandas as pd
df = pd.read_excel(excel_file)
print(df)

# Get the first column
column = df.columns[0]

from approaches.ch_preprocessor.chinese_sentence_segment import split_ch_sentences
source_splitted = split_ch_sentences(df[column])
print(len(source_splitted))

# Save the preprocessed source file to thanglong_src.txt
with open("thanglong_src1.txt", "w", encoding="utf-8") as f:
    for line in df[column]:
        line = line.strip()
        if line == "":
            continue
        f.write(line + "\n")