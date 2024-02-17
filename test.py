import re

def clean(text):
    text = re.sub(r' ', '_zzzzzspacezzzzz_', text)
    text = re.sub(r'-', '_zzzzzdashzzzzz_', text)
    text = re.sub(r'[\W]', '', text)
    text = re.sub(r'_zzzzzspacezzzzz_', ' ', text)
    text = re.sub(r'_zzzzzdashzzzzz_', '-', text)
    return text

dirty_text = input("Give me some text to clean: ")
print(clean(dirty_text))