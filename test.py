import re

def clean(text):
    clean_text = re.sub(r'[\W]', '', text)
    return clean_text

dirty_text = input("Give me some text to clean: ")
print(clean(dirty_text))