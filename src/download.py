import applicant
import xlsxwriter
import csv
from datetime import datetime


def download_csv(applicants, path, name, report=[], dev_values=False):
    with open(f"{path}/{datetime.now().strftime('%d-%m-%y-%H_%M')}_{name}.csv", "w", encoding='UTF8') as file:

        writer = csv.writer(file)
        header = ['name', 'email', 'number']
        if dev_values:
            header += ['fingerprint', 'hash']

        if report:
            header.append('reason for flag')

        writer.writerow(header)
        count = 0

        for applicant in applicants:
            row = [applicant.name, applicant.email, applicant.number]

            if dev_values:
                row += [repr(applicant.fingerprint), applicant.hash]

            if report:
                temp_str = ""
                for issue in report[count]:
                    temp_str += str(issue)
                    temp_str += " | "
                temp_str = temp_str[:-3]
                row.append(temp_str)
                count += 1

            writer.writerow(row)


def download_excel(applicants, path, name, report=[], dev_values=False):
    workbook = xlsxwriter.Workbook(f"{path}/{datetime.now().strftime('%d-%m-%y-%H_%M')}_{name}.xlsx")
    worksheet = workbook.add_worksheet("Info")

    row = 1
    col = 0

    worksheet.write(0, 0, 'name')
    worksheet.write(0, 1, 'email')
    worksheet.write(0, 2, 'number')
    if dev_values:
        worksheet.write(0, 3, 'fingerprint')
        worksheet.write(0, 4, 'hash')


    for applicant in applicants:
        worksheet.write(row, col, applicant.name)
        worksheet.write(row, col + 1, applicant.email)
        worksheet.write(row, col + 2, applicant.number)
        if dev_values:
            worksheet.write(row, col + 3, repr(applicant.fingerprint))
            worksheet.write(row, col + 4, applicant.hash)
        row += 1

    if dev_values:
        col = 5
    else:
        col = 3

    row = 1

    if report:
        worksheet.write(0, col, 'reason for flag')

    if report:
        for issues in report:
            temp_str = ""
            for issue in issues:
                temp_str += str(issue)
                temp_str += " | "
            temp_str = temp_str[:-3]
            worksheet.write(row, col, temp_str)
            row += 1

    workbook.close()
