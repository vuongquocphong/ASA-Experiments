import os
with open('./QTTY/SinoNom/QTTY6.txt', 'r', encoding="utf8") as f:
    text = f.read()
    # remove every " " in the text
    text = text.replace(" ", "")
with open('./QTTY/SinoNom/QTTY6_spaced.txt', 'w', encoding="utf8") as f:
    spaced = ' '.join(text)
    f.write(spaced)

trimmed_texts = []

with open('./QTTY/SinoNom/QTTY6_spaced.txt', 'r', encoding="utf8") as f:
    text = f.readlines()
    for line in text:
        trimmed = line.strip()
        trimmed_texts.append(trimmed)

with open('./QTTY/SinoNom/QTTY6_spaced.txt', 'w', encoding="utf8") as f:
    for trimmed in trimmed_texts:
        f.write(trimmed + '\n')



