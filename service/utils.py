import datetime
import re


def find_and_replace_not_partially(text, word_to_find, replacement):
    pattern = r"(?<!\w)`[^`]*?{}[^`]*`(?!\w)|\b{}\b".format(word_to_find, word_to_find)
    replaced_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return replaced_text


def generate_result_file_path(name, format):
 return "./sessions/{}_{}.{}".format(str(datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")), name, format)