import datetime
import os
import re

from service.logging_service import get_logger

logger = get_logger()

def find_and_replace_not_partially(text, word_to_find, replacement):

    # pattern = r"(?<!\w)`[^`]*?{}[^`]*`(?!\w)|\b{}\b".format(word_to_find, word_to_find)
    # pattern = r"(?<!\w)`[^`]*?{}[^`]*`(?!\w)|(?<!{{){}(?!}})".format(word_to_find, word_to_find)
    # pattern = r"(?<!\w)`[^`]*?{}[^`]*`(?!\w)|(?<!{{){}(?!}})".format(re.escape(word_to_find), re.escape(word_to_find))
    pattern = r"(?<!\{{)\b{}\b(?!\}})".format(re.escape(word_to_find))
    
    replaced_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    logger.debug("REPLACE NOT PARTIALLY ===========")
    logger.debug("TEXT: " + text )
    logger.debug("word_to_find: " + word_to_find )
    logger.debug("replaced_text: " + replaced_text )
    return replaced_text


def generate_result_file_path(name, format):
    home_path = os.path.expanduser('~')
    path = os.path.abspath(os.path.join(home_path, 'BigDebug/sessions/', "{}_{}.{}".format(str(datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")), name, format)))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    return path