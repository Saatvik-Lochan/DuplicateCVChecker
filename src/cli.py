import key_value_lookup
import select_cvs
import applicant

names = select_cvs.select_batch()
issues = []

for file in names:
    app = applicant.applicant_from_pdf(file)
    report = key_value_lookup.check_duplicate(app, 75)
    if len(report) != 0:
        issues.append(report)
    else:
        key_value_lookup.add_applicant(app)

for issue in issues:
    for rep in issue:
        print(rep)
    print("")

key_value_lookup.print_all()
