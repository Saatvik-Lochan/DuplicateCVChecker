from winnowing import winnow
from tika import parser
import os

os.environ['TIKA_SERVER_JAR'] = 'https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.19/tika-server-1.19.jar'


def fingerprint_pdf(file_path):
    return fingerprint_text(extract_content(file_path))


def extract_content(file_path):
    return parser.from_file(file_path)['content'].strip()


def fingerprint_text(text):
    return winnow(text)


def extract_keys_from_fingerprint(fingerprint):  # to store in the 'hash' db for fast lookup
    return {dhash[1] for dhash in fingerprint}


def extract_keys_from_pdf(file_path):
    return extract_keys_from_fingerprint(fingerprint_pdf(file_path))


def fingerprint_match(fingerprint1, fingerprint2):
    matches = len(fingerprint1.intersection(fingerprint2))
    min_length = min(len(fingerprint1), len(fingerprint2))
    return matches / min_length * 100
