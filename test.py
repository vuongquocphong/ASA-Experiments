# def normalize_u(u_text, sign_type=1) -> str:
#     # Map of replacement for different accent types based on sign_type
#     REPLACEMENTS = {
#         'òa': ('oà', 'òa'), 'óa': ('oá', 'óa'), 'ỏa': ('oả', 'ỏa'), 'õa': ('oã', 'õa'), 'ọa': ('oạ', 'ọa'),
#         'òe': ('oè', 'òe'), 'óe': ('oé', 'óe'), 'ỏe': ('oẻ', 'ỏe'), 'õe': ('oẽ', 'õe'), 'ọe': ('oẹ', 'ọe'),
#         'ùy': ('uỳ', 'ùy'), 'úy': ('uý', 'úy'), 'ủy': ('uỷ', 'ủy'), 'ũy': ('uỹ', 'ũy'), 'ụy': ('uỵ', 'ụy'),
#         'ùa': ('uà', 'ùa'), 'úa': ('uá', 'úa'), 'ủa': ('uả', 'ủa'), 'ũa': ('uã', 'ũa'), 'ụa': ('uạ', 'ụa'),
#         'uê': ('uề', 'uề'), 'uế': ('uế', 'uế'), 'uể': ('uể', 'uể'), 'uễ': ('uễ', 'uễ'), 'uệ': ('uệ', 'uệ')
#     }

#     for original, (type1, type2) in REPLACEMENTS.items():
#         if sign_type == 1:
#             u_text = u_text.replace(original, type1)
#         elif sign_type == 2:
#             u_text = u_text.replace(original, type2)

#     return u_text

# try:
#     assert normalize_u(u'hoè', 2) == u'hòe'
# except:
#     print('Test case 1 failed')

# def normalize_u(u_text, sign_type=1) -> str:
#     '''
#     Sign type 1:
#         'hòa' -> 'hoà'
#         'hòe' -> 'hoè'
#         ...
#     Sign type 2:
#         'hoà' -> 'hòa'
#         'hoè' -> 'hòe'
#         ...
#     '''

def normalize_u(u_text: str, sign_type=1) -> str:
    # Map of replacement for different accent types based on sign_type
    TWO_TO_ONE_REPLACEMENTS = {
        'òa': 'oà', 'óa': 'oá', 'ỏa': 'oả', 'õa': 'oã', 'ọa': 'oạ',
        'òe': 'oè', 'óe': 'oé', 'ỏe': 'oẻ', 'õe': 'oẽ', 'ọe': 'oẹ',
        'ùy': 'uỳ', 'úy': 'uý', 'ủy': 'uỷ', 'ũy': 'uỹ', 'ụy': 'uỵ',
        'ùa': 'uà', 'úa': 'uá', 'ủa': 'uả', 'ũa': 'uã', 'ụa': 'uạ',
        'uê': 'uề', 'uế': 'uế', 'uể': 'uể', 'uễ': 'uễ', 'uệ': 'uệ'
    }
    ONE_TO_TWO_REPLACEMENTS = {
        'oà': 'òa', 'oá': 'óa', 'oả': 'ỏa', 'oã': 'õa', 'oạ': 'ọa',
        'oè': 'òe', 'oé': 'óe', 'oẻ': 'ỏe', 'oẽ': 'õe', 'oẹ': 'ọe',
        'uỳ': 'ùy', 'uý': 'úy', 'uỷ': 'ủy', 'uỹ': 'ũy', 'uỵ': 'ụy',
        'uà': 'ùa', 'uá': 'úa', 'uả': 'ủa', 'uã': 'ũa', 'uạ': 'ụa',
        'uề': 'uê', 'uế': 'uế', 'uể': 'uể', 'uễ': 'uễ', 'uệ': 'uệ'
    }
    # Fix error in sign placing
    for original, replacement in TWO_TO_ONE_REPLACEMENTS.items():
        start = 0
        while u_text.find(original, start) != -1:
            cur = u_text.find(original, start)
            if cur + 2 < len(u_text) and u_text[cur + 2] != ' ':
                u_text = u_text.replace(original, replacement)
            start = u_text.find(original) + 2

    if sign_type == 1:
        for original, replacement in TWO_TO_ONE_REPLACEMENTS.items():
            start = 0
            while u_text.find(original, start) != -1:
                cur = u_text.find(original, start)
                if cur + 2 < len(u_text) and u_text[cur + 2] != ' ':
                    start = cur + 2
                    continue
                u_text = u_text[:cur] + replacement + u_text[cur + 2:]
                start = cur + 2
    elif sign_type == 2:
        for original, replacement in ONE_TO_TWO_REPLACEMENTS.items():
            start = 0
            while u_text.find(original, start) != -1:
                cur = u_text.find(original, start)
                if cur + 2 < len(u_text) and u_text[cur + 2] != ' ':
                    start = cur + 2
                    continue
                u_text = u_text[:cur] + replacement + u_text[cur + 2:]
                start = cur + 2
    return u_text

# Example usage:
text1 = 'hòa hòe thủy hoàng'
normalized_text1 = normalize_u(text1, sign_type=1)
print(normalized_text1)  # Output: "hoà hoè thuỷ hoàng"

text2 = 'huỳnh hòang phúc'
normalized_text2 = normalize_u(text2, sign_type=2)
print(normalized_text2)  # Output: "hòa hòe thủy hoàng"
