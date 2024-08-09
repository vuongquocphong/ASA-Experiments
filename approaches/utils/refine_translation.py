import os

dict = {",", ".", ":", ";", "!", "?", "(", ")", "[", "]", "{", "}"}

with open('./QTTY/Translation/QTTY6.txt', 'r', encoding="utf8") as f:
    texts = f.readlines()
    # remove the number and the dot if it exists at the beginning of the line
    for i, text in enumerate(texts):
        while text[0].isdigit() or text[0] == "." or text[0] == " ":
            text = text[1:]
        texts[i] = text
    
    # add space between punctuations and its neighboring characters
    for i, text in enumerate(texts):
        new_text = ""
        for j, char in enumerate(text):
            if char in dict:
                if j == 0:
                    if text[j + 1] != " ":
                        new_text += char + " "
                    else:
                        new_text += char
                elif j == len(text) - 1:
                    if text[j - 1] != " ":
                        new_text += " " + char
                    else:
                        new_text += char
                else:
                    if text[j - 1] != " ":
                        new_text += " " + char
                    elif text[j + 1] != " ":
                        new_text += char + " "
                    else:
                        new_text += char
            else:
                new_text += char
        texts[i] = new_text


with open('./QTTY/Translation/QTTY6_spaced.txt', 'w', encoding="utf8") as f:
    for text in texts:
        text = text.strip()
        f.write(text)
        f.write("\n")