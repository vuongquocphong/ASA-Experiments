import nltk

ch_example = "子 曰 ："
vn_example = "Sách Thể Luận viết : Người quân-tử tu dưỡng lòng chẳng gì tốt bằng (chân) thành."

def get_ch_content_words(ch_sentence):
    """
    Get content words from a Chinese sentence.
    """
    return [word for word in nltk.word_tokenize(ch_sentence) if word > "\u4e00" and word < "\u9fff"]

def get_vn_content_words(vn_sentence):
    marks = [',', '.', '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '"', "'", '“', '”', '‘', '’', '...', '…', '–', '-', '—']
    """
    Get content words from a Vietnamese sentence.
    """
    return [word.lower().replace("-", " ") for word in nltk.word_tokenize(vn_sentence) if word not in marks]

ch_content_words = get_ch_content_words(ch_example)
vn_content_words = get_vn_content_words(vn_example)

print(ch_content_words)
print(vn_content_words)

for i in range(1, 3):
    for j in range(1, 16):
        print(f'({i}, {j}), ', end='')