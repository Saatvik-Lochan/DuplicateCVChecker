from sqlitedict import SqliteDict
import possible_duplicate
import hashing_cvs
import settings

current_settings = settings.Settings()
current_settings.json_deserialise()

# To store the applicants in the form [uid : applicant object]
applicant_db = SqliteDict(f'{current_settings.database_folder_path}/applicants.sqlite', autocommit=True)

# To store hashes so we don't have to do a linear time search of applicants|in the form [fingerprint : [uid, uid, ...]]
hashes = SqliteDict(f"{current_settings.database_folder_path}/hashes.sqlite", autocommit=True)

# To store numbers in the form [number : uid]
numbers = SqliteDict(f"{current_settings.database_folder_path}/numbers.sqlite", autocommit=True)

# To store emails in the form [email : uid]
emails = SqliteDict(f"{current_settings.database_folder_path}/emails.sqlite", autocommit=True)


def check_duplicate(applicant, match_value):
    report = []

    if applicant.hash in applicant_db:
        report.append(possible_duplicate.PossibleDuplicate("exact match"))
        return report

    if applicant.number in numbers:
        report.append(possible_duplicate.PossibleDuplicate("number match"))

    if applicant.email in emails:
        report.append(possible_duplicate.PossibleDuplicate("email match"))

    keys_of_fingerprint = applicant.fingerprint

    possible_matches = set()

    # checks for matches in the winnowing in the hashes db
    for key in keys_of_fingerprint:
        if key in hashes:
            for uid in hashes[key]:
                possible_matches.add(uid)

    for uid in possible_matches:
        match = hashing_cvs.fingerprint_match(applicant.fingerprint, applicant_db[uid].fingerprint)
        if match > match_value:
            report.append(possible_duplicate.FingerprintMatch(applicant_db[uid], match))

    return report


def add_applicant(applicant):  # should be used with check_duplicate
    applicant_db[applicant.hash] = applicant
    emails[applicant.email] = applicant.hash
    numbers[applicant.number] = applicant.hash

    # add to the hashes db
    for hash in applicant.fingerprint:
        if hash in hashes:
            hashes[hash].append(applicant.hash)
        else:
            hashes[hash] = [applicant.hash]


def print_all():
    for app in applicant_db:
        print(applicant_db[app], end="\n\n")


