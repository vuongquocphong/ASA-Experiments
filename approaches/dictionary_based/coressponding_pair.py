# =====================================================================================
import nltk
from nltk.tokenize import word_tokenize

def get_ch_content_words(ch_sentence):
    """
    Get content words from a Chinese sentence.
    """
    return [
        word for word in word_tokenize(ch_sentence)
        if any(
            ord(word) in range(start, end + 1)
            for start, end in [
                (0x4e00, 0x9fff),
                (0xf900, 0xfaff),
                (0x20000, 0x2A6DF)
            ]
        )
    ]

def get_vn_content_words(vn_sentence):
    marks = [',', '.', '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '"', "'", '“', '”', '‘', '’', '...', '…', '–', '-', '—']
    """
    Get content words from a Vietnamese sentence.
    """
    return [word.lower().replace("-", " ") for word in word_tokenize(vn_sentence) if word not in marks]
# =====================================================================================


from typing import List

assigned, visited, adjective = None, None, None
time = 0

def visit( u: int ) -> bool:

    global visited, adjective, assigned
    
    if visited[u] == time:
        return False
    visited[u] = time

    for v in adjective[u]:
        if not assigned[v] or visit( assigned[v] ):
            assigned[v] = u
            return True
    
    return False

def bead_score_new( Chinese_sentences: List[any], Vietnamese_sentences: List[any], a: int, b: int, x: int, y: int, dictionary: dict ) -> float:
    
    # Initialization
    source_words = []
    target_words = []
    result = 0

    # Get content words
    for i in range(a - x + 1, a + 1):
        source_words += Chinese_sentences[i]

    for i in range(b - y + 1, b + 1):
        target_words += Vietnamese_sentences[i]

    if len( source_words ) == 0 or len( target_words ) == 0:
        return 0

    available_Chinese_words = [ word for word in source_words if word in dictionary.keys() ]
    
    Vietnamese_domains = [ dictionary[word] for word in available_Chinese_words ]
    Vietnamese_domains = [ item for sublist in Vietnamese_domains for item in sublist ]
    Vietnamese_domains = list( set( Vietnamese_domains ) )

    available_Vietnamese_words = [ word for word in target_words if word in Vietnamese_domains ]
    unavailable_Vietnamese_words = [ word for word in target_words if word not in Vietnamese_domains ]

    # Add abundance words ( combine two consecutive words )
    abundance_words = [unavailable_Vietnamese_words[i - 1] + " " + unavailable_Vietnamese_words[i] for i in range(1, len(unavailable_Vietnamese_words))]
    abundance_words = [ word for word in abundance_words if word in Vietnamese_domains ]
    available_Vietnamese_words += abundance_words

    # Create a bipartite graph
    global assigned, visited, time, adjective

    m, n = len( available_Chinese_words ), len( available_Vietnamese_words )
    adjective = [ [] for _ in range( m ) ]
    assigned = [ None for _ in range( n ) ]
    visited = [ 0 for _ in range( m ) ]

    for i in range( m ):
        for j in range( n ):
            if available_Vietnamese_words[j] in dictionary[ available_Chinese_words[i] ]:
                adjective[i].append( j )

    # Find the maximum matching
    for i in range( m ):
        time += 1
        result += visit( i )
    
    return result / ( len( source_words ) + len( target_words ) )