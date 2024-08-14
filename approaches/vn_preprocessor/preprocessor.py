__author__ = 'Nguyen Hoang Long'

# Ref: Alex
# Ref: Tran Thanh Nam for [normalize_accent]

import codecs
import json
import operator
import re
import hashlib
import unicodedata
from enum import Enum
from pathlib import Path

from .vietnamese import *


# Enumartors
class Language(Enum):
    """
    Language enumators
    """
    english = 'en'
    vietnamese = 'vi'


class Preprocessor:
    # Path constants
    RESOURCE_DIR = Path('approaches/vn_preprocessor/resource')
    HONORIFIC_DIR = RESOURCE_DIR.joinpath('honorifics')
    REPLACEMENT_DIR = RESOURCE_DIR.joinpath('replacement')
    COMMON_REPLC_FILE = REPLACEMENT_DIR.joinpath('common.json')
    EMOJI_REPLC_FILE = REPLACEMENT_DIR.joinpath('emoji.json')
    ARRAYS_FILE = RESOURCE_DIR.joinpath('arrays.json')
    STRINGS_FILE = RESOURCE_DIR.joinpath('strings.json')

    CAPITAL_LETTER = 'AÂĂBCDĐEÊFGHIJKLMNOÔƠPQRSTUƯVWXYZ'
    # Name of replacement dictionaries
    GENERAL = 'general'
    ABBREVIATION = 'abbrv'
    SHORT_FULL_FRM = 'short_full_frm'
    SHORT_FRM_MSTKE = 'short_frm_mistake'
    TYPE_MISTAKE = 'type_mistake'
    # Name of string
    URL_REGEX_STR = 'url_regex'

    EMOJI_PATTERN = ':{0}:'

    # Newline characters
    DELIM_CR = '\r'
    DELIM_LF = '\n'

    # List of honorifics
    __honorifics = {
        Language.english: None,
        Language.vietnamese: None
    }

    __replc_dict = {}
    __emoji_dict = {}
    __arr_lst = {}
    __str_lst = {}

    __url_regex = None
    __email_regex = None

    def __init__(self, lang: Language):
        # Load resources
        # Load replacements dictionary
        # Common
        if not Preprocessor.__replc_dict:
            with open(
                    Preprocessor.COMMON_REPLC_FILE, 'r', encoding='utf8') as f:
                Preprocessor.__replc_dict = json.load(f)
        self.__replc_dict = Preprocessor.__replc_dict
        # Particular language
        replc_lang_file = Preprocessor.REPLACEMENT_DIR.joinpath(
            lang.value + '.json')
        if replc_lang_file.is_file():
            # File exists
            replc_dict = {}
            with open(replc_lang_file, 'r', encoding='utf8') as f:
                replc_dict = json.load(f)
                for name, subdict in replc_dict.items():
                    if name in self.__replc_dict:
                        self.__replc_dict.update(subdict)
        # Load arrays list
        with open(Preprocessor.ARRAYS_FILE, 'r', encoding='utf8') as f:
            Preprocessor.__arr_lst = json.load(f)
        # Load strings list
        with open(Preprocessor.STRINGS_FILE, 'r', encoding='utf8') as f:
            Preprocessor.__str_lst = json.load(f)

    def __normalize_short_form(self, sentence):
        """Fix typing errors: English short forms.

        Args:
            sentence (str): Input sentence.

        Returns:
            str: Sentence has been normalized.
        """
        return Preprocessor.__replace_substr(
            self, sentence, Preprocessor.SHORT_FRM_MSTKE)

    def __replace_substr(self, sentence, dict_name):
        """Replace all substrings that are keys in global replacement dictionary
        with corresponding value.

        Args:
            sentence (str): Input sentence.
            dict_name (str): Name of dictionary to use.

        Returns:
            str: Sentence after replacing substring.
        """
        if dict_name in self.__replc_dict:
            dic = self.__replc_dict[dict_name]
        else:
            return sentence

        return Preprocessor.replace_substr(sentence, dic)

    def __process_plaintext(self, text):
        """Preprocess plain text withou URL

        Args:
            text (str): Input plain text to preprocess

        Returns:
            str: Preprocessed text
        """
        text = Preprocessor.__replace_substr(
            self, text, Preprocessor.GENERAL)
        text = Preprocessor.normalize_accent(text)
        text = Preprocessor.process_punc(self, text)
        text = Preprocessor.replace_emoji(text)
        text = Preprocessor.remove_adjacent_whitespaces(text)

        return text

    def __process_dot(self, sent):
        """Process dots:
            - Dot as punctuation.
            - Dot in honorfics, abbreviation, etc.s

        Args:
            sent (str): Sentence to process.

        Results:
            str: Sentence after processing.
        """
        # Add whitespace before dot at the end of the sentence
        if (len(sent) > 3 and sent[-1] == '.' and
                sent[-2] != '.' and sent[-3] != '.'):
            sent = sent[:-1] + ' ' + '.'

        for i in range(1, len(sent) - 1):
            if sent[i] == '.':
                if ' ' in sent[:i]:
                    idx_capital_letter = sent.rindex(' ', 0, i)
                    capital_letter = sent[idx_capital_letter + 1]
                else:
                    capital_letter = sent[i - 1]
                if sent[i - 1].isalpha() and capital_letter.isupper():
                    if sent[i + 1] is not ' ':
                        if capital_letter in Preprocessor.CAPITAL_LETTER:
                            if (i < len(sent) - 2 and
                                    (sent[i + 1].isupper() or
                                     sent[i + 1].isnumeric())):
                                # Add whitespace after dot
                                sent = sent[:i] + '. ' + sent[i + 1:]
                        else:
                            # 'TP.HCM' -> 'TP. HCM', 'Q.7' -> 'Q. 7',
                            # 'P.2' -> 'P. 2'
                            sent = sent[:i] + '. ' + sent[i + 1:]
                    elif capital_letter in Preprocessor.CAPITAL_LETTER:
                        # 'C. ' --> 'C . '
                        # H. Potter, co gai ten Th. da
                        if (i + 3 < len(sent) and
                                (sent[i + 2].isupper() or sent[i + 2] == '(') and
                                sent[i + 3].islower()):
                            pass
                        elif (i + 2 < len(sent) and
                              (sent[i + 2].islower() or
                               sent[i + 2] in '(-[')):
                            pass
                        else:
                            sent = sent[:i] + ' . ' + sent[i + 1:]
                    # 'A.1.' -> 'A . 1.'
                # '하고..' --> '하고 . .'
                elif (i + 2 < len(sent) and sent[i + 1] == '.' and
                      sent[i - 1] != '.' and sent[i + 2] != '.'):
                    sent = sent[:i] + ' . ' + sent[i + 1:]
                # 'a. Phương pháp' -> 'a . Phương pháp'
                elif sent[i - 1].isdigit() and sent[i + 1] is ' ':
                    # '1. ' -> '1 . '
                    # '1.1.' -> '1 . 1.'
                    sent = sent[:i] + ' . ' + sent[i + 1:]
            elif sent[i] == '/':
                if (sent[i - 1].isdigit() and
                        not (sent[i + 1].isdigit()) and sent[i + 1] != ' '):
                    if sent[i + 1].islower():  # 'm3/giờ' -> 'm3 / giờ'
                        sent = sent[:i] + ' / ' + sent[i + 1:]
                elif not (sent[i - 1].isdigit()) and not (sent[i + 1].isdigit()):
                    if sent[i - 1] != ' ' and sent[i + 1] != ' ':
                        sent = sent[:i] + ' / ' + sent[i + 1:]
            elif sent[i] == '-':
                if sent[i - 1].isdigit() and sent[i + 1].isdigit():
                    sent = sent[:i] + ' - ' + sent[i + 1:]
            elif sent[i] == '+':
                if sent[i - 1].isdigit() and sent[i + 1].isdigit():
                    sent = sent[:i] + ' + ' + sent[i + 1:]
            elif (sent[i] == 'm' and sent[i - 1].isdigit() and
                  (sent[i + 1] == ' ' or sent[i + 1].isdigit() or
                   sent[i + 1] in self.__replc_dict['mark'])):
                sent = sent[:i] + ' ' + sent[i] + ' ' + sent[i + 1:]

        return sent

    def __preprocess(self, sentence):
        """Main preprocessing method (private)

        Args:
            sentence (str): Input sentence to preprocess

        Returns:
            str: Preprocessed sentence
        """
        # Trim whitespaces
        sentence = sentence.strip()

        if sentence != '':
            # Remove BOM character if exist
            sentence = sentence.encode('utf-8').decode('utf-8-sig')

            # Convert composite unicode characters to
            # precomposed unicode characters
            sentence = unicodedata.normalize('NFC', sentence)

            # Find all URL indices in sentence
            if self.__url_regex is None:
                # self.__url_regex = re.compile(self.__str_lst[Preprocessor.URL_REGEX_STR])
                self.__url_regex = re.compile(r'(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?')
            url_ranges = [
                (m.start(0), m.end(0)) for
                m in self.__url_regex.finditer(sentence)
            ]

            # Find all email indices in sentence
            if self.__email_regex is None:
                # self.__email_regex = re.compile(self.__str_lst[Preprocessor.EMAIL_REGEX_STR])
                self.__email_regex = re.compile(r'[a-z][a-z0-9_\.]*@[a-z0-9]{1,}(\.[a-z0-9]{1,}){1,5}')
            email_ranges = [
                (m.start(0), m.end(0)) for
                m in self.__email_regex.finditer(sentence)
            ]

            # Replace URLs by special strings
            url_ranges.sort(key=operator.itemgetter(0), reverse = True)
            url_mark_lst = []
            for (url_st_idx, url_ed_idx) in url_ranges:
                url = sentence[url_st_idx:url_ed_idx]
                hash_url = hashlib.sha1(url.encode('utf-8')).hexdigest()
                hash_url_mark = 'BURL' + hash_url + 'URLE'
                sentence = sentence[:url_st_idx] + hash_url_mark + sentence[url_ed_idx:]
                url_mark_lst.append((hash_url_mark, url))

            # Replace emails by special strings
            email_ranges.sort(key=operator.itemgetter(0), reverse=True)
            email_mark_lst = []
            for (email_st_idx, email_ed_idx) in email_ranges:
                email = sentence[email_st_idx:email_ed_idx]
                hash_email = hashlib.sha1(email.encode('utf-8')).hexdigest()
                hash_email_mark = 'BEMAIL' + hash_email + 'EMAILE'
                sentence = sentence[:email_st_idx] + hash_email_mark + sentence[email_ed_idx:]
                email_mark_lst.append((hash_email_mark, email))

            sentence = Preprocessor.__process_plaintext(self, sentence)

            # Reverse special strings to URLs
            for hash_url_mark, url in url_mark_lst:
                sentence = sentence.replace(hash_url_mark, url)

            # Reverse special strings to emails
            for hash_email_mark, email in email_mark_lst:
                sentence = sentence.replace(hash_email_mark, email)

        return sentence

    @staticmethod
    def __process_meas_ccy_unit(sentence):
        """Process measurement and currency unit.

        Args:
            sentence (str): Input sentence.

        Returns:
            str: Processed sentence.
        """

        # Find all SPECIAL MASKS in sentence
        special_regex = re.compile(r'(BURL|BEMAIL)[A_Za-z0-9]*(URLE|EMAILE)')
        special_ranges = [
            (m.start(0), m.end(0)) for
            m in special_regex.finditer(sentence)
        ]

        #  Add whitespace before measurement and currency unit
        m_index = 0
        for m_unit in Preprocessor.__arr_lst['meas_ccy_unit']:
            m_index = sentence.find(m_unit, 1)
            while m_index > 0:
                check_inside_special = 0    # Check if the unit is generated by hashlib, if yes then do nothing
                for (special_st_idx, special_ed_idx) in special_ranges:
                    if special_st_idx <= m_index <= special_ed_idx:
                        check_inside_special = 1
                        break
                if not check_inside_special:
                    if sentence[m_index - 1].isnumeric():
                        sentence = sentence[:m_index] + ' ' + sentence[m_index:]
                m_index = sentence.find(m_unit, m_index + len(m_unit) + 1)

        return sentence

    @staticmethod
    def __get_honorifics(langs):
        """Get list of honorifics of input language.

        Args:
            lang (str): Language to get.

        Returns:
            None: If found nothing
            list: List of honorifics if found any.
        """
        honorifics = []

        for lang in langs:
            if (lang in Preprocessor.__honorifics and
                    Preprocessor.__honorifics[lang] is not None):
                # Get from loaded dict.
                honorifics.extend(Preprocessor.__honorifics[lang])
            else:
                # Get honorifics fromm files
                h_path = Preprocessor.HONORIFIC_DIR.joinpath(lang.value)
                if h_path.exists():
                    # File exists
                    h_lns = codecs.open(h_path, 'r', 'utf-8').readlines()
                    Preprocessor.__honorifics[lang] = []
                    for h_ln in h_lns:
                        honorific = h_ln[:-1]
                        honorifics.append(honorific)
                        # Store to reuse without reloading files
                        Preprocessor.__honorifics[lang].append(honorific)

        if not honorifics:
            # List of honorifics is empty
            honorifics = None

        return honorifics

    @staticmethod
    def __normalize_honorific(sentence, honorific):
        """Normalize sentence with honorific.

        Args:
            sentence (str): Input sentence.
            honorific (list): List of honorifics.

        Returns:
            str: Sentence that has been normalized with honorific.
        """
        if honorific is not None:
            for h in honorific:
                new_h = h[:-1] + " ."

                if new_h in sentence:
                    sentence = sentence.replace(new_h, h)

        return sentence

    @staticmethod
    def __normalize_propername(sent):
        """Normalize typing errors: Proper name.

        Args:
            sent (str): Input sentence.

        Returns:
            str: Sentence has normalized proper name.
        """
        # "S .p. A" --> "S.p.A"
        # "S.P.K" --> "S . P. K"
        rs = sent
        i = 0
        honorifics_en = Preprocessor.__get_honorifics([Language.english])
        while i < len(rs):
            if rs[i] == '.':
                f_change = True
                for t in honorifics_en:
                    ln = len(t)
                    if sent[i - ln + 1:i + 1] == t:
                        f_change = False
                        break
                if f_change is True:
                    if (i > 2 and i + 1 < len(rs) and
                            rs[i - 1] == ' ' and rs[i - 2].isupper() and
                            rs[i + 1].islower()):
                        rs = rs[:i - 1] + rs[i:]
                        i -= 1
                    if (i < len(rs) - 2 and rs[i + 1] == ' ' and
                            rs[i + 2].isupper() and rs[i - 1].islower() and
                            not rs[i - 2].lower()):
                        rs = rs[:i + 1] + rs[i + 2:]
                    if (i > 2 and i + 2 < len(rs) and
                            rs[i - 1] == ' ' and rs[i - 2].isupper() and
                            rs[i + 1] == ' ' and rs[i + 2].isupper()):
                        rs = rs[:i - 1] + '.' + rs[i + 2:]
                    if (i > 1 and i + 2 < len(rs) and
                            rs[i - 1].isupper() and rs[i + 1] == ' ' and
                            rs[i + 2].isupper()):
                        rs = rs[:i + 1] + rs[i + 2:]

            i += 1
        return rs

    @staticmethod
    def __replace_y_i(string):
        """
        Replace 'y' to 'i'
        :param st: sentence
        :return: new sentence
        """
        if not string:
            return string

        f_upper = False
        if string.isupper():
            st = string.lower()
            f_upper = True
        else:
            st = string

        consonant = ['k', 'l', 'm', 'n', 'qu', 's', 't', 'v', 'x']
        vowel_i = ['i', 'í', 'ì', 'ỉ', 'ĩ', 'ị']
        vowel_y = ['y', 'ý', 'ỳ', 'ỷ', 'ỹ', 'ỵ']

        a = st[0]
        for i in range(1, len(st)):
            i_i = 0
            a += st[i]
            if st[i] != ' ':
                for v in vowel_y:
                    if (st[i] == v and
                            (i == len(st) - 1 or st[i + 1] == ' ' or
                             st[i + 1] == '_')):
                        if any(st[i - 1] == c for c in consonant):
                            a = a[:-1] + vowel_i[i_i]
                        elif i > 2 and st[i - 2:i] == 'qu':
                            a = a[:-1] + vowel_i[i_i]
                        elif (st[i - 1] == 'h' and i > 1 and
                              all(st[i - 2].lower() != w
                                  for w in
                                  ['t', 'p', 'g', 'k', 'c', 'n'])):
                            a = a[:-1] + vowel_i[i_i]
                    i_i += 1

        # English word
        a = a.replace('siti ', 'sity ')
        a = a.replace(' citi', ' city')
        a = a.replace(' Citi', ' City')
        a = a.replace(' empti', ' empty')
        a = a.replace(' Empti', ' Empty')

        if f_upper:
            a = a.upper()
        return a

    @staticmethod
    def __process_url(url: str):
        """Process URL.

        Args:
            url (str): URL string.

        Returns:
            str: Processed URL.
        """
        if url[-1] in '.)]':
            # Add whitespace before ending mark
            url = url[:-1] + ' ' + url[-1]

        return url

    def __preprocess_file(self, inp_file, out_file, options=None):
        """Preprocess a list of sentences in a file. Each sentence on one line.

        Args:
            inp_file (Path): Path to input file.
            out_file (Path): Path to output file.
            options (dict):
                overwrite (bool): If True then overwrite if file exists,
                                    else raise FileExistsError.
                                    Default value is False.
                replace_y_i (bool): If True then replace y by i.
                                    Default value is False.

        Raises:
            FileNotFoundError: Input file does not exist.
            FileExistsError: Output file already exists.
        """
        # Prepare options
        # Define default options
        default_options = {
            'overwrite': False,
            'replace_y_i': False
        }
        if options is not None:
            # Fill in missing options by their default values
            for key, value in default_options.items():
                if key not in options:
                    options[key] = value
        else:
            # Use default options
            options = default_options

        if inp_file.is_file():
            # Check output path
            if out_file.exists() and not options['overwrite']:
                raise FileExistsError('Output file already exists.')
            else:
                with open(inp_file, 'r', encoding='utf8') as f:
                    # Read from file
                    sents = f.readlines()
                sents = self.preprocess_list(sents, options['replace_y_i'])
                # Write processed sentences to file
                # Create folder if not exist
                out_file.parents[0].mkdir(parents=True, exist_ok=True)
                sents_cnt = len(sents)
                with open(out_file, 'w', encoding='utf-8') as fo:
                    for idx in range(0, sents_cnt):
                        fo.write(sents[idx].strip())
                        if idx < sents_cnt - 1:
                            fo.write(Preprocessor.DELIM_LF)
        else:
            raise FileNotFoundError('Cannot find input file.')

    def __segment_file_to_sentences(
            self, inp_path, out_path, options=None):
        """Segment text in a file to sentences. Accept only UTF-8 encoding.

        Args:
            inp_path (str): Path to input file or directory.
            out_path (str): Path to output file or directory.
            options (dict):
                overwrite (bool): If True then overwrite if file exists,
                                    else raise FileExistsError.
                                    Default value is False.
                preprocess (bool): If True then preprocess before segmentation.
                                    Default value is False.
                replace_y_i (bool): Only affect when preprocess option is True.
                                    If True then replace y by i.
                                    Default value is False.

        Raises:
            FileNotFoundError: Input file or directory does not exist.
            FileExistsError: Output file or directory already exists.
        """
        # Prepare options
        # Define default options
        default_options = {
            'overwrite': False,
            'preprocess': False,
            'replace_y_i': False
        }
        if options is not None:
            # Fill in missing options by their default values
            for key, value in default_options.items():
                if key not in options:
                    options[key] = value
        else:
            # Use default options
            options = default_options

        # Check output path
        if out_path.exists() and not options['overwrite']:
            raise FileExistsError(
                'Output file or directory already exists.')
        else:
            with open(inp_path, 'r', encoding='utf8') as f:
                # Read from file
                text = f.read()
            sents = self.segment_to_sentences(
                text, options['preprocess'], options['replace_y_i'])
            # Write processed sentences to file
            # Create folder if not exist
            out_path.parents[0].mkdir(parents=True, exist_ok=True)
            sents_cnt = len(sents)
            with open(out_path, 'w', encoding='utf-8') as fo:
                for idx in range(0, sents_cnt):
                    fo.write(sents[idx])
                    if idx < sents_cnt - 1:
                        fo.write(Preprocessor.DELIM_LF)

    def fix_type_mistake(self, sentence: str):
        """Fix type mistakes.

        :param a: input sentence
        :return: new sentence
        """
        return Preprocessor.__replace_substr(
            self, sentence, Preprocessor.TYPE_MISTAKE)

    def process_punc(self, sentence: str):
        """Process punctuation marks.

        Args:
            sentence (str): Input sentence.

        Returns:
            str: Sentence contains processed punctuation marks.
        """
        import html

        if not sentence or sentence.strip() == '':
            return ''

        tmp = html.unescape(sentence)

        # TODO: Cannot understand why Mr. Alex must unescape HTML twice
        # if '&amp;' in tmp:
        #     tmp = html.unescape(tmp)

        #  Process measurement and currency unit
        tmp = Preprocessor.__process_meas_ccy_unit(tmp)

        # Replace 2 whitespaces with 1 whitespace
        tmp = tmp.replace('  ', ' ')

        # Replace mark
        tmp = self.__replace_substr(tmp, 'mark')
        # Add space around dot
        tmp = re.sub(r'([^.\d])\.([^.\d])', r'\1 . \2', tmp)

        tmp = Preprocessor.__process_dot(self, tmp)

        # Metre at the end
        if tmp.endswith('m'):
            if tmp[-2].isdigit():
                tmp = tmp[:-1] + ' m'

        # Replace all double whitespace with single one
        tmp = Preprocessor.remove_adjacent_whitespaces(tmp)

        if tmp.endswith('..'):
            tmp = tmp[:-2] + ' . .'
        elif tmp.endswith('.'):
            tmp = tmp[:-1] + ' .'
        elif tmp.endswith('. !'):
            tmp = tmp[:-3] + ' . !'
        elif tmp.endswith('. ?'):
            tmp = tmp[:-3] + ' . ?'

        # Normalize honorifics in English and Vietnamese.
        # Example: 'TS .' -> 'TS.'
        tmp = Preprocessor.normalize_honorific(
            tmp, [Language.vietnamese, Language.english])

        # Normalize short form for English
        tmp = Preprocessor.__normalize_short_form(self, tmp)

        # Time
        tmp = Preprocessor.normalize_en_time(tmp)

        # Proper name (S.p.tmp)
        tmp = Preprocessor.__normalize_propername(tmp)
        tmp = Preprocessor.__normalize_short_form(self, tmp)

        # Fix abbreviation
        tmp = Preprocessor.__replace_substr(
            self, tmp, Preprocessor.ABBREVIATION)

        tmp = Preprocessor.fix_type_mistake(self, tmp)

        return tmp

    @staticmethod
    def replace_substr(sentence, replc_dic):
        """Replace all substrings that are keys in input dictionary.
        with corresponding value.

        Args:
            sentence (str): Input sentence.
            replc_dic (dictionary): Dictionary to search for keys.

        Returns:
            str: Sentence after replacing substring.
        """
        tmp_str = sentence
        for key, value in replc_dic.items():
            tmp_str = tmp_str.replace(key, value)

        return tmp_str

    @staticmethod
    def normalize_accent(sent):
        """Normalize Vietnamese accents.

        Args:
            sent (str): Input sentence.

        Returns:
            str: Sentence after accent normalization.
        """
        new_sent = normalize_u(sent, sign_type=1).strip()
        new_sent = new_sent.replace("Ủy ", "Uỷ ")

        return new_sent

    @staticmethod
    def remove_adjacent_whitespaces(sentence: str):
        """Replace multiple adjacent whitespaces with single one.

        Args:
            sentence (str): Input sentence.

        Results:
            str: Processed sentence.
        """
        if sentence is not None and sentence.strip() != '':
            while '  ' in sentence:
                sentence = sentence.replace('  ', ' ')

        return sentence

    @staticmethod
    def replace_emoji(sentence, reload_dict=False):
        """Replace emoji with a pattern

        Args:
            sentence (str): Sentence to processs

        Returns:
            Sentence that not has emoji characters
        """
        if not Preprocessor.__emoji_dict or reload_dict:
            # Load emoji replacements dictionary
            with open(
                    Preprocessor.EMOJI_REPLC_FILE, 'r', encoding='utf8') as f:
                Preprocessor.__emoji_dict = json.load(f)

        for key, value in Preprocessor.__emoji_dict.items():
            sentence = sentence.replace(
                key, Preprocessor.EMOJI_PATTERN.format(value))

        return sentence

    @staticmethod
    def normalize_en_time(sentence):
        """Fix time typing errors.

        Args:
            sentence (str): Input sentence.

        Returns:
            str: Sentence that has been time-normalized.
        """
        # Normalize A.M. and P.M. symbols
        am_pm_symbols = {
            'a.m.': 'A.M. ',
            'a.m .': 'A.M.',
            'a.m': 'A.M. ',
            'A.M .': 'A.M.',
            'a . m .': 'A.M.',
            'a . m ': 'A.M. ',
            'p.m.': 'P.M. ',
            'p.m .': 'P.M.',
            'p.m': 'P.M. ',
            'P.M .': 'P.M.',
            'P. M.': 'P.M.',
            'p . m .': 'P.M.',
            'p . m ': 'P.M. ',
        }

        for key, val in am_pm_symbols.items():
            sentence = sentence.replace(key, val)

        parts = sentence.split(' ')
        for i in range(1, len(parts) - 1):
            if parts[i] == 'am':
                if parts[i - 1].isdigit():
                    parts[i] = 'A.M.'
            if parts[i] == 'pm':
                if parts[i - 1].isdigit():
                    parts[i] = 'P.M.'

        sentence = ' '.join(parts)

        return sentence

    @staticmethod
    def normalize_honorific(sentence, langs):
        """Normalize sentence with honorific.

        Args:
            sentence (str): Input sentence.
            langs (Language): Languages to get honorifics.

        Returns:
            str: Sentence that has been normalized with honorific.
        """
        honorific = Preprocessor.__get_honorifics(langs)

        return Preprocessor.__normalize_honorific(sentence, honorific)

    def preprocess(self, sentence, replace_y_i=False):
        """Preprocess a sentence.

        Args:
            sentence (str): Sentence to preprocess.
            replace_y_i (bool): Do replace y with i and vice versa.

        Returns:
            str: Preprocessed sentence.
        """
        sentence = Preprocessor.__preprocess(self, sentence)

        if replace_y_i and sentence != '':
            # Replace y with i and vice versa
            sentence = Preprocessor.__replace_y_i(sentence)

        return sentence

    def preprocess_list(self, sentences, replace_y_i=False):
        """Preprocess a list of sentences.

        Args:
            sentences (list): List of sentences.
            replace_y_i (bool): Do replace y with i and vice versa.

        Returns:
            list: List of preprocessed sentences.
        """
        result = []

        for sent in sentences:
            sent = Preprocessor.preprocess(self, sent, replace_y_i)
            result.append(sent)

        return result

    def preprocess_files(
            self, inp_path, out_path, options=None):
        """Segment texts in files to sentences. Accept only UTF-8 encoding.

        Args:
            inp_path (str): Path to input file or directory.
            out_path (str): Path to output file or directory.
            options (dict):
                overwrite (bool): If True then overwrite if file exists,
                                    else raise FileExistsError.
                                    Default value is False.
                replace_y_i (bool): If True then replace y by i.
                                    Default value is False.

        Raises:
            FileNotFoundError: Input file or directory does not exist.
            FileExistsError: Output file or directory already exists.
        """
        inp_path = Path(inp_path)
        out_path = Path(out_path)
        if inp_path.exists():
            if inp_path.is_file():
                # Input path is file
                self.__preprocess_file(
                    inp_path, out_path, options)
            else:
                # Input path is directory
                for i_path in inp_path.glob('**/*.*'):
                    o_path = out_path.joinpath(i_path.relative_to(inp_path))
                    self.__preprocess_file(
                        i_path, o_path, options)
        else:
            raise FileNotFoundError('Cannot find input file or directory.')

    def segment_to_sentences(self, text, preprocess=False, replace_y_i=False):
        """Segment text to list of sentences

        Args:
            text (str): Input text.
            preprocess (bool): If True then preprocess before segmentation.
                                Default value is False.
            replace_y_i (bool): Affect only when preprocess parameter is True.
                                If True then replace y by i.
                                Default value is False.

        Returns:
            list: List of sentences.
        """

        if preprocess:
            text = self.preprocess(text, replace_y_i)

        sentence_lst = []

        # Remove all new-line characters
        # text = text.replace(Preprocessor.DELIM_CR, ' ')
        # text = text.replace(Preprocessor.DELIM_LF, ' ')

        # Split text into lines
        text = text.replace(' . ', ' .' + Preprocessor.DELIM_CR)
        lines = text.splitlines()

        for line in lines:
            # Replace non-breaking whitespace with normal whitespace
            line = line.replace(u'\xa0', u' ')
            # Replace … with ...
            line = line.replace('…', '...')
            # Strip text
            line = line.strip()

            # Get honorifics list
            honorifics = Preprocessor.__get_honorifics([Language.vietnamese, Language.english])
            # Define honorific exception
            honor_exc_dict = {
                'case-insensitive': [
                    'chương', 'phần', 'mục'
                ],
                'case-sensitive': [
                    'anh', 'chị', 'em', 'cô', 'chú', 'ông', 'bà'
                ]
            }
            # Find punctuation
            punc_matches = re.finditer(
                r'(?:([^\s]+)\s+)?(?:([^\s]+)\s+)?([^\s]*([.!?]))(\s*)(?=([^\s]|$))',
                line)
            st_idx = 0
            pre_chr = ''
            for m in punc_matches:
                punc = m.group(4)
                is_adjacent_chr = m.group(5) is None or len(m.group(5)) == 0
                next_chr = m.group(6)
                # Get punctuation index in text
                punc_idx = m.start(4)
                if punc == '.':
                    token_1 = m.group(1)
                    token_2 = m.group(2)
                    token_3 = m.group(3)
                    # Last charater is a dot
                    # Check exception (honorifics, etc.) before processing
                    if next_chr in '-([' or next_chr.islower():
                        # After dot is -,{,[ or a lower charater
                        # Don't split
                        continue
                    elif token_3 in honorifics:
                        if token_2 is None:
                            continue
                        # There is honorifics before dot
                        if ((token_2.lower() not in
                             honor_exc_dict['case-insensitive']) and
                                (token_2 not in
                                 honor_exc_dict['case-sensitive'])):
                            # Token before honorific-candidate is not in exception
                            # Then don't split
                            continue
                    # Check roman numeral to avoid splitting
                    last_token = token_3[:-1]
                    if not last_token and token_2 and token_1:
                        last_token = token_2

                    # Check number and header to avoid splitting
                    if last_token:
                        if (last_token.isdigit() and pre_chr != last_token and
                                not token_1 and not token_2):
                            # Header
                            continue
                        elif (last_token[-1].isdigit() and
                              is_adjacent_chr and next_chr.isdigit()):
                            # Decimal and thousands separators
                            # Don't split
                            pre_chr = next_chr
                            continue

                elif punc == '!' and next_chr in '=' and is_adjacent_chr:
                    # Punctuation is ! and next character is =
                    # Don't split
                    continue

                # Get substring in text from st_idx to punctuation index and strip
                tmp = line[st_idx:punc_idx + 1].strip()
                # Add substring to list
                sentence_lst.append(tmp)
                # Upadte start index st_idx
                st_idx = punc_idx + 1
                pre_chr = ''

            # Get the last sentence
            if st_idx < len(line):
                sentence_lst.append(line[st_idx:].strip())

        return sentence_lst

    def segment_files_to_sentences(
            self, inp_path, out_path, options=None):
        """Segment texts in files to sentences. Accept only UTF-8 encoding.

        Args:
            inp_path (str): Path to input file or directory.
            out_path (str): Path to output file or directory.
            options (dict):
                overwrite (bool): If True then overwrite if file exists,
                                    else raise FileExistsError.
                                    Default value is False.
                preprocess (bool): If True then preprocess before segmentation.
                                    Default value is False.
                replace_y_i (bool): Affect only when preprocess option is True.
                                    If True then replace y by i.
                                    Default value is False.

        Raises:
            FileNotFoundError: Input file or directory does not exist.
            FileExistsError: Output file or directory already exists.
        """
        inp_path = Path(inp_path)
        out_path = Path(out_path)
        if inp_path.exists():
            if inp_path.is_file():
                # Input path is file
                self.__segment_file_to_sentences(
                    inp_path, out_path, options)
            else:
                # Input path is directory
                for i_path in inp_path.glob('**/*.*'):
                    o_path = out_path.joinpath(i_path.relative_to(inp_path))
                    self.__segment_file_to_sentences(
                        i_path, o_path, options)
        else:
            raise FileNotFoundError('Cannot find input file or directory.')

# End of file
