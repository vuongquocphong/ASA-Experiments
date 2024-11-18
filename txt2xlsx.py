import pandas as pd

def convert(txt_file, xlsx_file):
    with open(txt_file, 'r', encoding='utf-8') as f:
        data = f.readlines()
    data = [line.split('\t') for line in data]
    df = pd.DataFrame(data)
    df.to_excel(xlsx_file, header=False, index=False)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python txt2xlsx.py input.txt output.xlsx")
        sys.exit(1)
    txt_file = sys.argv[1]
    xlsx_file = sys.argv[2]
    convert(txt_file, xlsx_file)
    print(f"Converted {txt_file} to {xlsx_file}")