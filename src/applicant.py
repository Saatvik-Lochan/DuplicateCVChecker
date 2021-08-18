import hashlib
from datetime import datetime
import parse_cvs
import hashing_cvs


class Applicant:

    def __init__(self, info, fingerprint):  # info is a tuple in the form (name, email, number)
        self.name, self.email, self.number = info
        self.hash = repr(self.create_hash().digest())
        self.creation_date = datetime.now()  # marks application date
        self.fingerprint = fingerprint

    def create_hash(self):
        base = self.name + self.email + self.number
        return hashlib.sha1(base.encode())  # use of SHA1 since it gives a smaller hash

    def __str__(self):
        string = f"Name: {self.name}\nEmail: {self.email}\nNumber: {self.number}"
        return string


def applicant_from_pdf(file_path):
    fingerprint = hashing_cvs.extract_keys_from_pdf(file_path)
    info = parse_cvs.parse_cv(file_path)
    return Applicant(info, fingerprint)
