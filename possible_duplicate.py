class PossibleDuplicate:

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class FingerprintMatch(PossibleDuplicate):

    def __init__(self, match, percent):
        self.match = match
        self.percent = percent

    def __str__(self):  # come back and change
        return f"{self.percent}% fingerprint match with {self.match.name}"
