# import nltk

# ch_example = "子 曰 ："
# vn_example = "Sách Thể Luận viết : Người quân-tử tu dưỡng lòng chẳng gì tốt bằng (chân) thành."

# def get_ch_content_words(ch_sentence):
#     """
#     Get content words from a Chinese sentence.
#     """
#     return [word for word in nltk.word_tokenize(ch_sentence) if word > "\u4e00" and word < "\u9fff"]

# def get_vn_content_words(vn_sentence):
#     marks = [',', '.', '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '"', "'", '“', '”', '‘', '’', '...', '…', '–', '-', '—']
#     """
#     Get content words from a Vietnamese sentence.
#     """
#     return [word.lower().replace("-", " ") for word in nltk.word_tokenize(vn_sentence) if word not in marks]

# ch_content_words = get_ch_content_words(ch_example)
# vn_content_words = get_vn_content_words(vn_example)

# print(ch_content_words)
# print(vn_content_words)

# for i in range(1, 3):
#     for j in range(1, 16):
#         print(f'({i}, {j}), ', end='')

import re

import re

import re

def remove_notes(sentence):
    """
    Remove notes in a sentence (inside parentheses). If open but not close, remove from the open to the end of the sentence.
    If close but not open, remove from the beginning of the sentence to the close.
    Also, ensure there are no multiple adjacent spaces.
    """
    result = []
    open_parentheses = 0
    has_unmatched_close = False

    for char in sentence:
        if char == '(':
            if open_parentheses == 0:
                has_unmatched_close = False  # Reset in case we found unmatched close earlier
            open_parentheses += 1
        elif char == ')':
            open_parentheses -= 1
            if open_parentheses < 0:
                has_unmatched_close = True
                open_parentheses = 0
                result = []  # Reset the result if we found unmatched close
                has_unmatched_close = False
            continue  # Do not add this character to the result if we're closing a parenthesis
        if open_parentheses == 0 and not has_unmatched_close:
            result.append(char)

    # If unmatched closing parenthesis was found, return only the part before it
    cleaned_sentence = ''.join(result)

    # Replace multiple spaces with a single space
    cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence)
    
    return cleaned_sentence.strip()

# Example usage:
example_sentence = "This is   an example sentence (with a note) and  (another one."
print(remove_notes(example_sentence))  # Output: "This is an example sentence and"

test_1 = "aasc (asdjkhsasd) asd"
test_2 = "aasc asd (asdjkhsasd)"
test_3 = "aasc asd asdjkhsasd (asdjkhasdkjh"
test_4 = "(aasc asd asdjkhsasd asdjkhasdkjh)) (asjdskasjdh) kjlka"
test_5 = "aasc asd asdjkhsasd asdjkhasdkjh"
test_6 = "aaa ((a) (b)) a"

print(remove_notes(test_1))
print(remove_notes(test_2))
print(remove_notes(test_3))
print(remove_notes(test_4))
print(remove_notes(test_5))
print(remove_notes(test_6))