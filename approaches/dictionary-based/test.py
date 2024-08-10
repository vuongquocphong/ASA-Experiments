import nltk

ch_example = "子 曰 ："
vn_example = "Sách Hán Thư viết :  Từ thời đại ( thái_bình của ) vua Thành_Khang đến nay , cũng gần 1000 năm , có nhiều bậc vua chúa muốn được vậy , thế mà cảnh thái bình ấy không thể hưng_khởi trở lại , tại vì sao ?"

def get_ch_content_words(ch_sentence):
    """
    Get content words from a Chinese sentence.
    """
    return [word for word in nltk.word_tokenize(ch_sentence) if word > "\u4e00" and word < "\u9fff"]

def get_vn_content_words(vn_sentence):
    marks = [',', '.', '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '"', "'"]
    """
    Get content words from a Vietnamese sentence.
    """
    return [word for word in nltk.word_tokenize(vn_sentence) if word not in marks]

ch_content_words = get_ch_content_words(ch_example)
vn_content_words = get_vn_content_words(vn_example)

print(ch_content_words)
print(vn_content_words)

from ..utils import util

dictionary = util.read_dictionary()

print(len(dictionary))
print(dictionary)