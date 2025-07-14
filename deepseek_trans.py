from openai import OpenAI
import os
import re

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def translate(text: str) -> str:
    messages = [
    {"role": "system", "content": """You are a professional translator specializing in Classical Chinese (文言文) and Vietnamese. Your task is to accurately and elegantly translate Classical Chinese texts into Vietnamese, maintaining historical, cultural, and philosophical nuances.
    At the end of the response, please self thinking about your translation and provide the confidence score of the translation, using the basis 0 - 100, where 0 means you are completely lost and provide an absolutely inaccurate translations, where 100 means you have excellently translated the couplet; in between, 50 means that your translation is just decent and some problems might need to be fixed.Please note that you're not encouraged to self provide score as an gradient (which means that you're not encourage to only rate 0, 100 or 50 only but to give some numbers like 35, 47, 78, 98).
    Please wrap the score with format: ###{score}###"""},
    {"role": "user", "content": """You are a professional translator specializing in Classical Chinese (文言文) and Vietnamese. Your task is to accurately and elegantly translate Classical Chinese texts into Vietnamese, maintaining historical, cultural, and philosophical nuances.
    At the end of the response, please self thinking about your translation and provide the confidence score of the translation, using the basis 0 - 100,
    where 0 means you are completely lost and provide an absolutely inaccurate translations, where 100 means you have excellently translated the couplet; in between, 50 means that your translation is just decent and some problems might need to be fixed.
    Please note that you're not encouraged to self provide score as an gradient (which means that you're not encourage to only rate 0, 100 or 50 only but to give some numbers like 35, 47, 78, 98).
    Please wrap the score with format: ###{x}### where x is your score.
    Please also give some explanation for the score, wrapped in %%%{explanation}%%%.
    The Classical Chinese couplet :""" + text},
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )
    match = re.search(r'"(.*?)"', response.choices[0].message.content)
    if match:
        vietnamese_translation = match.group(1)
        return vietnamese_translation

chinese_snts = []
with open("./data/dai_viet_su_ki/errors.txt", "r", encoding="utf8") as f:
    lines = f.readlines()
    for line in lines:
        chinese_snts.append(line.strip())

with open("./data/dai_viet_su_ki/deepseek_trans_src_snts.txt", "a", encoding="utf8") as f:
    for i in range(len(chinese_snts)):
        print(f"Processed sentence number {i}")
        print(translate(chinese_snts[i]).strip())
        # f.write(translate(chinese_snts[i]).strip() + "\n")
        # f.flush()
