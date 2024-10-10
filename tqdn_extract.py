import pymupdf
import os
import fitz
ch_marks = {".", ";", "?", "!", "{", "}", "(", ")", "[", "]", "“", "”", "‘", "’", "…", "–", "-", "—", "。", "；", "？", "！", "!", "?", "《", "》", "（", "）", "【", "】", " ", "\n", "。", "，", "、", "："}

def chinese_length_count(text):
    for mark in ch_marks:
        text = text.replace(mark, "")
    return len(text)

def is_chinese_text(text):
    for mark in ch_marks:
        text = text.replace(mark, "")
    for char in text:
        if not ('\u4e00' <= char <= '\u9fff' or '\uf900' <= char <= '\ufaff' or '\U00020000' <= char <= '\U0002a6df'):
            return False
    return True

def sinoviet_count(text):
    count = 0
    marks = {".", ";", "?", "!", "{", "}", "(", ")", "[", "]", "“", "”", "‘", "’", "…", "–", "-", "—", "。", "；", "？", "！", "!", "?", "《", "》", "（", "）", "【", "】", "\n", "。", "，", ","}
    for mark in marks:
        text = text.replace(mark, "")
    text = text.strip().split(" ")
    for word in text:
        if word != "":
            count += 1
    return count


def read_pdf(file_path):
    pdf = fitz.open(file_path)
    chinese_pars = []
    sinoviet_pars = []
    translation_pars = []
    is_chinese = False
    is_sinoviet = False
    is_translation = False
    cur_chinese = ""
    cur_sinoviet = ""
    cur_translation = ""
    curr_sino_count = 0
    chinese_count = 0
    page_start = 3
    for i in range(page_start, pdf.page_count):
        is_chinese = False
        is_sinoviet = False
        is_translation = False
        page = pdf[i]
        # skip the page number
        text = page.get_text("text")
        lines = text.split("\n")
        lines = lines[1:]
        curr_line_idx = 0;
        while curr_line_idx < len(lines):
            # print(curr_line_idx)
            curr_line = lines[curr_line_idx].strip()
            if curr_line == "":
                curr_line_idx += 1
                continue
            # If the current line is "1"
            if curr_line == "1":
                # Skip the next 3 lines and set is_chinese to True
                curr_line_idx += 4
                is_chinese = True
                continue
            # If other numbers add cur_chinese, cur_sinoviet, cur_translation to the corresponding list, and reset them
            if curr_line.isdigit():
                if cur_chinese != "":
                    chinese_pars.append(cur_chinese)
                    cur_chinese = ""
                if cur_sinoviet != "":
                    sinoviet_pars.append(cur_sinoviet)
                    cur_sinoviet = ""
                if cur_translation != "":
                    translation_pars.append(cur_translation)
                    cur_translation = ""
                is_chinese = False
                is_sinoviet = False
                is_translation = False
                curr_sino_count = 0
                chinese_count = 0
                curr_line_idx += 1
                continue
            if not is_chinese and not is_sinoviet and not is_translation:
                if is_chinese_text(curr_line):
                    is_chinese = True
                else:
                    curr_line_idx += 1
                    continue
            if is_chinese:
                if is_chinese_text(curr_line):
                    cur_chinese += curr_line
                    chinese_count += chinese_length_count(curr_line)
                    curr_line_idx += 1
                else:
                    is_chinese = False
                    is_sinoviet = True
            if is_sinoviet:
                curr_sino_count += sinoviet_count(curr_line)
                if cur_sinoviet == "":
                    cur_sinoviet += curr_line
                else:
                    cur_sinoviet += " " + curr_line
                curr_line_idx += 1
                if curr_sino_count >= chinese_count:
                    is_sinoviet = False
                    is_translation = True
                    continue
            if is_translation:
                if cur_translation == "":
                    cur_translation += curr_line
                else:
                    cur_translation += " " + curr_line
                curr_line_idx += 1
    chinese_pars.append(cur_chinese)
    sinoviet_pars.append(cur_sinoviet)
    translation_pars.append(cur_translation)
    return chinese_pars, sinoviet_pars, translation_pars

def write_text(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in text:
            if item != " " or item != "":
                f.write(item)

if __name__ == "__main__":
    print("Hello")
    import sys
    if len(sys.argv) != 2:
        print("Usage: python tqdn_extract.py <file_path>")
        sys.exit(1)
    
    file_name = sys.argv[1]
    print(file_name)
    chinese_pars, sinoviet_pars, translation_pars = read_pdf(file_name)

    dir_name = file_name.split('.')[0]
    # Create directories if not exist
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open('./' + dir_name + '/' + 'chinese_pars.txt', 'w', encoding='utf-8') as f:
        for item in chinese_pars:
            f.write("%s\n" % item)

    with open('./' + dir_name + '/' + 'sinoviet_pars.txt', 'w', encoding='utf-8') as f:
        for item in sinoviet_pars:
            f.write("%s\n" % item)

    with open('./' + dir_name + '/' + 'translation_pars.txt', 'w', encoding='utf-8') as f:
        for item in translation_pars:
            f.write("%s\n" % item)