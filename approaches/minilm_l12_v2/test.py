from typing import List, Tuple
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the pre-trained model
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Helper function to clean or preprocess sentences if necessary
def remove_notes(sentence):
    # Example of preprocessing. Customize as needed
    return sentence

# Function to align sentences with multiple possible matches
def LM(src_paragraph: List[str], trg_paragraph: List[str]) -> List[Tuple[int, int]]:
    # Preprocess the source and target paragraphs
    src_paragraph = [remove_notes(sent) for sent in src_paragraph]
    trg_paragraph = [remove_notes(sent) for sent in trg_paragraph]
    
    # Encode sentences to get their embeddings
    src_embeddings = model.encode(src_paragraph, convert_to_tensor=True)
    trg_embeddings = model.encode(trg_paragraph, convert_to_tensor=True)
    
    n = len(src_paragraph)
    m = len(trg_paragraph)
    
    # Initialize DP table H and backtrace dictionary
    H = dict()
    backtrace = dict()
    
    # Add dummy sentences at index 0
    H[(0, 0)] = 0
    backtrace[(0, 0)] = (0, 0)
    
    # Initialize the first row and column of the DP table
    for i in range(1, n + 1):
        H[(i, 0)] = 0
        backtrace[(i, 0)] = (i - 1, 0)
    
    for j in range(1, m + 1):
        H[(0, j)] = 0
        backtrace[(0, j)] = (0, j - 1)

    # Calculate the DP table
    for a in range(1, n + 1):
        for b in range(1, m + 1):
            max_score = 0
            max_x, max_y = 1, 1

            # Compare sentences based on their embeddings
            for x in range(1, a + 1):
                for y in range(1, b + 1):
                    score = cosine_similarity(
                        src_embeddings[a - x : a].cpu().numpy(),  # Source range
                        trg_embeddings[b - y : b].cpu().numpy()   # Target range
                    ).mean()
                    
                    total_score = H[(a - x, b - y)] + score
                    
                    if total_score > max_score:
                        max_score = total_score
                        max_x, max_y = x, y

            # Update the DP table and backtrace
            H[(a, b)] = max_score
            backtrace[(a, b)] = (a - max_x, b - max_y)

    # Backtrace to get the split positions
    a, b = n, m
    split_positions = [(a, b)]
    
    while a > 0 and b > 0:
        a, b = backtrace[(a, b)]
        split_positions.append((a, b))
    
    return split_positions[::-1]

# Example usage:
src_paragraph = ["The cat sat on the mat.", "It was a sunny day.", "The dog barked."]
trg_paragraph = ["The cat was on the mat too.", "The cat is sitting on a mat.", "It was sunny.", "The day was sunny and bright.", "A dog was barking."]

split_positions = LM(src_paragraph, trg_paragraph)
cur_src = 0
cur_trg = 0
for a, b in split_positions:
    src_sentence = " ".join(src_paragraph[cur_src:a])
    trg_sentence = " ".join(trg_paragraph[cur_trg:b])
    print(src_sentence + " ||| " + trg_sentence)
    cur_src = a
    cur_trg = b
