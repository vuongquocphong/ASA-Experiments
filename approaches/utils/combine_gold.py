import os

def combine_xlsx(folder_path):
    output_file_path = os.path.join(folder_path, "combine.xlsx")
    import pandas as pd
    df = pd.DataFrame()
    column_0 = []
    column_1 = []
    column_2 = []
    # Read all files in the folder, get the content and append to the dataframe
    for file in os.listdir(folder_path):
        if file.endswith(".xlsx"):
            content = pd.read_excel(os.path.join(folder_path, file), header=None)
            column_0.extend(content.iloc[:, 0].tolist())
            column_1.extend(content.iloc[:, 1].tolist())
            column_2.extend(content.iloc[:, 2].tolist())
    df["column_0"] = column_0
    df["column_1"] = column_1
    df["column_2"] = column_2
    df.to_excel(output_file_path, index=False, header=False)

if __name__ == "__main__":
    import sys

    folder_path = sys.argv[1]

    combine_xlsx(folder_path)
# =====================================================================================