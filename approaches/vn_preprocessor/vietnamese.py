__author__ = 'Tran Thanh Nam'

# -*- coding: utf-8 -*-
# ========================================================================
import re

# Vietnamese accent values
NON_ACC = 0  # Không dấu
ACU_ACC = 1  # Dấu sắc
GRA_ACC = 2  # Dấu huyền
QUE_ACC = 3  # Dấu hỏi
TIL_ACC = 4  # Dấu ngã
HEA_ACC = 5  # Dấu nặng

# ========================================================================
# Classified single vowels in Vietnamese (with accent) aby accent
acu_vows = u'á ắ ấ é ế í ó ố ớ ú ứ ý'  # Dấu sắc
gra_vows = u'à ằ ầ è ề ì ò ồ ờ ù ừ ỳ'  # Dấu huyền
que_vows = u'ả ẳ ẩ ẻ ể ỉ ỏ ổ ở ủ ử ỷ'  # Dấu hỏi
til_vows = u'ã ẵ ẫ ẽ ễ ĩ õ ỗ ỡ ũ ữ ỹ'  # Dấu ngã
hea_vows = u'ạ ặ ậ ẹ ệ ị ọ ộ ợ ụ ự ỵ'  # Dấu nặng

ACCENT_VOW_LIST = [acu_vows, gra_vows, que_vows, til_vows, hea_vows]

# Classified single vowels in Vietnamese by root vowels
# ( a vowel do not have accent)
VOWS_DICT = {
    u'a': u'a á à ả ã ạ',
    u'ă': u'ă ắ ằ ẳ ẵ ặ',
    u'â': u'â ấ ầ ẩ ẫ ậ',
    u'e': u'e é è ẻ ẽ ẹ',
    u'ê': u'ê ế ề ể ễ ệ',
    u'i': u'i í ì ỉ ĩ ị',
    u'o': u'o ó ò ỏ õ ọ',
    u'ô': u'ô ố ồ ổ ỗ ộ',
    u'ơ': u'ơ ớ ờ ở ỡ ợ',
    u'u': u'u ú ù ủ ũ ụ',
    u'ư': u'ư ứ ừ ử ữ ự',
    u'y': u'y ý ỳ ỷ ỹ ỵ'
}

# All consonant in Vietnamese
SINGLE_CONSONANT = u'b c d đ g h k l m n p q s r t v x'
ALL_CONSONANT = SINGLE_CONSONANT + 'ch gi kh ng ngh gh nh ph qu th tr'
ALL_CHARACTER = u'b c d đ g h k l m n p q s r t v x a ă â e ê i o ô ơ u ư y'


def get_all_char_acc(encode='unicode'):
    """
    Return a list of Vietnames characters
    :param encode: Encoding
    """
    result = []
    if encode == 'unicode':
        for k in VOWS_DICT:
            result = result + VOWS_DICT[k].split(' ')

        result = result + SINGLE_CONSONANT.split(' ')
    else:
        for k in VOWS_DICT:
            result = result + VOWS_DICT[k].decode('utf-8').split(' ')

        result = result + SINGLE_CONSONANT.decode('utf-8').split(' ')

    return result


def get_all_char(encode='unicode'):
    """
    Return list of all Vietnamese characters
    :param encode: Encoding
    """

    if encode == 'utf-8':
        return ALL_CHARACTER.decode('utf-8').split(' ')
    elif encode == 'unicode':
        return ALL_CHARACTER.split(' ')


# =================================================================
def get_accent_char_u(u_char):
    """
    Return accent of a vowel character
    :param u_char: unicode
    return: int in range 1->6
    """
    for id_acc, vows_acc in enumerate(ACCENT_VOW_LIST):
        if u_char in vows_acc or u_char in vows_acc.upper():
            # Dau bat dau tu 1, vi tri trong list bat dau tu 0
            return id_acc + 1
    return NON_ACC


def get_accent_syl_u(syllable):
    """
    Return accent of syllabe
    return: int in range 0->6
    """
    for ch in syllable:
        acc = get_accent_char_u(ch)
        if acc > 0:
            return acc

    return NON_ACC


def remove_accent_char_u(u_char):
    for root, s in VOWS_DICT.iteritems():
        if u_char in s:
            return root
    # Return original input character
    return u_char


def remove_accent(syl, encode='unicode'):
    if encode == 'utf-8':
        syl = syl.decode('utf-8')

    l_char = list(syl)
    for i, u_c in enumerate(l_char):
        l_char[i] = remove_accent_char_u(u_c)

    if encode == 'utf-8':
        return u''.join(l_char).encode('utf-8')
    else:
        return u''.join(l_char)


# =================================================================
def is_vowel_u(u_char):
    """
    Check if input unicode character is vowel or not
    :param u_char: unicode character
    :return: True if input character is vower, false for else
    """
    for k in VOWS_DICT.keys():
        if u_char in VOWS_DICT[k]:
            return True

    return False


def num_vow_char_in_syl_u(u_syl):
    num = 0
    for ch in u_syl:
        if is_vowel_u(ch):
            num += 1

    return num


def combine_char_accent_u(u_char, acc_value):
    """
    Combine alphabet character with an accent
    :param u_char: Unicode character
    :param acc_value: Accent value
    :return: Unicode character contains alphabet character and accent
    """
    if u_char in VOWS_DICT.keys():
        accent_list = VOWS_DICT[u_char].split(' ')
        return accent_list[acc_value]

    return u_char


def combine_vow_acc_u(u_syl, accent, sign_type=1):
    """
    Combine a vowel with an accent
    :param u_syl: Unicode character
    :param accent: Accent
    :return: Unicode character contains vowel and accent
    """
    if u_syl == '':
        return ''

    for i, c in enumerate(u_syl):
        if is_vowel_u(c):
            break
    u_vowel = u_syl[i:]
    u_cons = u_syl[:i]
    # Luật 3:
    # Dấu thanh luôn nằm trên kí tự 'ê' và 'ơ' nếu chúng xuất hiện trong tiếng
    if u'ê' in u_vowel:
        return u_cons + u_vowel.replace(
            u'ê', combine_char_accent_u(u'ê', accent))
    if u'ơ' in u_vowel:
        return u_cons + u_vowel.replace(
            u'ơ', combine_char_accent_u(u'ơ', accent))

    if u_vowel in [u'oa', u'oe', u'uy']:
        # Sign type 1: 'hòa' -> 'hoà'
        # Sign type 2: 'hoà' -> 'hòa'
        if sign_type == 1:
            return (u_cons + u_vowel[0] +
                    combine_char_accent_u(u_vowel[1], accent))
        else:
            return (u_cons +
                    combine_char_accent_u(u_vowel[0], accent) + u_vowel[1])

    num_vow_char = num_vow_char_in_syl_u(u_vowel)
    num_con_char = len(u_vowel) - num_vow_char

    # Luật 1: Nếu tiếng có hai nguyên âm thì dấu thanh nằm ở nguyên âm đầu tiên
    if num_vow_char == 1 or (num_vow_char == 2 and num_con_char == 0):
        return u_cons + combine_char_accent_u(u_vowel[0], accent) + u_vowel[1:]

    # Luật 2: Nếu tiếng có 3 nguyên âm thì dấu thanh nằm ở nguyên âm thứ 2
    if (num_vow_char == 2 and num_con_char > 0) or (num_vow_char == 3):
        return (u_cons + u_vowel[0] +
                combine_char_accent_u(u_vowel[1], accent) + u_vowel[2:])

    return (u_cons + u_vowel)  # Did not combine accent and vowel


def normalize_u(u_text, sign_type=1):
    '''
    Sign type 1:
        'hòa' -> 'hoà'
        'hòe' -> 'hoè'
        ...
    Sign type 2:
        'hoà' -> 'hòa'
        'hoè' -> 'hòe'
        ...
    '''
    vows = [u'oa', u'oe', u'uy']
    d_conf_vow = dict()
    for vow in vows:
        for accent in range(0, 6):
            if sign_type == 1:
                err_vow = combine_vow_acc_u(vow[0], accent, sign_type) + vow[1]
                correct_vow = combine_vow_acc_u(vow, accent, sign_type)
                d_conf_vow[err_vow] = correct_vow
            else:
                err_vow = vow[0] + combine_vow_acc_u(vow[1], accent, sign_type)
                correct_vow = combine_vow_acc_u(vow, accent, sign_type)
                d_conf_vow[err_vow] = correct_vow

    for err_vow, correct_vow in d_conf_vow.items():
        u_text = re.sub(u'{0}(?=\W)'.format(err_vow), correct_vow, u_text)

    return u_text


def normalize(text, sign_type=1):
    return normalize_u(text.decode('utf-8'), sign_type).encode('utf-8')


def minimum_edit_dist(u1, u2):
    """
    Calculate minimum-edit distance using dynamic programming
    return: int
    """
    m = [[0.0 for x in range(len(u2) + 1)] for x in range(len(u1) + 1)]  # matrix

    for i in range(len(m)):
        m[i][0] = float(i)

    for j in range(len(m[0])):
        m[0][j] = float(j)

    for i in range(1, len(m)):
        for j in range(1, len(m[0])):
            temp = m[i - 1][j - 1] + int(u1[i - 1] != u2[j - 1])
            m[i][j] = min(temp, m[i - 1][j] + 1, m[i][j - 1] + 1)

    return m[len(m) - 1][len(m[0]) - 1]


def lower_utf8(s):
    return s.decode('utf-8').lower().encode('utf-8')


# =================================================================
def load_syllable_set(encode='unicode'):
    """
    Load danh sach cac tieng trong tieng Viet
    """
    SYL_FILE_PATH = '../lm/syllables.txt'

    with open(SYL_FILE_PATH, 'r') as f:
        lines = f.readlines()

    if encode == 'unicode':
        d = [l.strip().decode('utf-8') for l in lines[1:]]
    else:
        d = [l.strip() for l in lines[1:]]

    return set(d)


def load_vdict(encode='unicode'):
    """
    Tra ve cac tu co trong tieng
    Cac tieng noi nhau bang dau gach chan Vd: thong_nhat
    """
    VDIC_FILE_PATH = '../lm/VDic.txt'  # LINUX PATH
    with open(VDIC_FILE_PATH, 'r') as f:
        lines = f.readlines()

    if encode == 'unicode':
        d = [l.split('#')[0].decode('utf-8') for l in lines]
    else:
        d = [l.split('#') for l in lines]
    return set(d)


def get_around_dict(encode='unicode'):
    s_vdic = load_vdict(encode)
    d_before = dict()  # tu lien truoc
    d_after = dict()  # lu lien sau
    for w in s_vdic:
        l_syls = w.split('_')
        if len(l_syls) > 1:
            d_after[l_syls[0]] = d_after.get(l_syls[0], []) + l_syls[1:2]
            d_before[l_syls[1]] = d_before.get(l_syls[1], []) + l_syls[0:1]

    return d_before, d_after


def count_num_tone_sign(u_text):
    lst = [0, 0, 0, 0, 0, 0]
    for i, s_acc in enumerate(ACCENT_VOW_LIST):
        acc_id = i + 1
        for c_acc in s_acc.split(' '):
            lst[acc_id] += len([m.start() for m in re.finditer(c_acc, u_text)])

    num_all_syl = len([m.start() for m in re.finditer('\s\S+', u_text)])
    lst[0] = num_all_syl - sum(lst[1:])
    return lst


def count_vowel_non_acc(u_syl, u_text):
    num_occur = 0
    # List of syllables that have been added accents
    syl_acc_s = set([combine_vow_acc_u(u_syl, acc) for acc in range(0, 6)])

    for syl_acc in syl_acc_s:
        num_occur += len([m.start() for m in re.finditer(syl_acc, u_text)])

    return num_occur

# End of file
