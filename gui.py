import PySimpleGUI as sg
import select_cvs
import applicant
import os
import key_value_lookup
import download
import settings
import possible_duplicate

# set theme
sg.theme('SystemDefault')

# unpack settings
current_settings = settings.Settings()
current_settings.json_deserialise()

main_menu = [[sg.Button("Settings"), sg.Button("Upload CVs"), sg.Button("View Current Applicants")]]

upload_cvs = [[sg.Text("Select a method to upload files (pdf or docx):")],
              [sg.Button("Upload Files")],
              [sg.Button("Upload Folder")]]

check_parse_results = [[sg.Text("Make sure the following seem correct: ", key='-PROMPT-', visible=False)],
                       [sg.ProgressBar(0, key='-PROGRESS BAR-', visible=True)],
                       [sg.Frame("One second, please wait while the CVs are being parsed",
                                 layout=[[sg.Text("Name: "), sg.InputText(key="-NAME-", expand_x=True)],
                                         [sg.Text("Email: "), sg.InputText(key="-EMAIL-", expand_x=True)],
                                         [sg.Text("Number: "), sg.InputText(key='-NUMBER-', expand_x=True)]],
                                 key='-FRAME-')],
                       [sg.Button("Open This CV"), sg.Button("Next")]]

verify_check_level = [[sg.Text("The checker will flag applicants who are at least"),
                       sg.InputText("75", justification='right', size=(3, 1), key='-CHECK LEVEL-'),
                       sg.Text("% similar to a previous applicant.")],
                      [sg.Button('Next')]]

adding_to_database = [[sg.Text("Adding applicants to the database", key='-STATUS-')],
                      [sg.ProgressBar(0, key='-PROGRESS BAR-')],
                      [sg.Button('View Summary', visible=False)]]

uploaded_applicants = [[sg.Button("Create CSV", key='-UP CSV-'), sg.Button("Create Excel File", key='-UP XL-')],
                       [sg.Frame("Applicant",
                                 layout=[[sg.Text("Name"), sg.Text("NA", key="-UP NAME-")],
                                         [sg.Button("Applicant Info", key='-UP A INFO-')]],
                                 key='-UP FRAME-')],
                       [sg.Button("Previous", key='-UP PREV-'), sg.Button("Next", key='-UP NEXT-')]]

flagged_applicants = [[sg.Button("Create CSV", key='-F CSV-'), sg.Button("Create Excel File", key='-F XL-')],
                      [sg.Frame("Applicant",
                                layout=[[sg.Text("Name"), sg.Text("NA", key="-F NAME-")],
                                        [sg.Button("Applicant Info", key='-F A INFO-'), sg.Button("Duplicate Info")]],
                                key='-F FRAME-')],
                      [sg.Button("Previous", key="-F PREV-"), sg.Button("Next", key="-F NEXT-")]]

summary = [[sg.Text("Here is the summary of the procedure")],
           [sg.TabGroup(
               [[sg.Tab("Uploaded Applicants", uploaded_applicants, key='-UPLOADED-'),
                 sg.Tab("Flagged Applicants", flagged_applicants, key='-FLAGGED-')]],
               tab_location='topleft'
           )],
           [sg.Button("Exit Program")]]

window = sg.Window('Duplicate CV Checker - Saatvik', main_menu)
current_window = 'main_menu'
check_level = 75


# window creator functions
def create_temp_applicant_window(applicant):
    layout = [[sg.Text("Name:"), sg.Text(applicant.name)],
              [sg.Text("Email:"), sg.Text(applicant.email)],
              [sg.Text("Number:"), sg.Text(applicant.number)],
              [sg.Text("Date Enrolled:"), sg.Text(applicant.creation_date.strftime("%d/%m/%y"))],
              [sg.Button("Exit"), sg.Button("Download Text File")]]
    window = sg.Window(f"{applicant.name} - applicant info", layout, modal=True)
    while True:
        temp_event, temp_values = window.read(timeout=10)

        if temp_event == 'Exit':
            window.close()
            return

        if temp_event == sg.WINDOW_CLOSED:
            window.close()
            return


def create_temp_duplicate_window(report, applicant):  # report is a list of PossibleDuplicate objects
    number_of_issues = len(report)
    current_issue = 1
    layout = [[sg.Text(f"Flagged Applicant: {applicant.name}")],
              [sg.Frame(f"Issue 1/{number_of_issues}",
                        layout=[
                            [sg.Multiline(str(report[0]), key="-DESCRIPTION-")],
                             [sg.Button("View Match Info",
                                        visible=(type(report[0]) == possible_duplicate.FingerprintMatch))]
                        ])],
              [sg.Button("Prev"), sg.Button("Next")],
              [sg.Button("Exit"), sg.Button("Download Text File")]]

    window = sg.Window(f"{applicant.name} - flag info", layout=layout, modal=True)

    while True:
        temp_event, temp_values = window.read(timeout=10)

        if temp_event == "Next":
            if current_issue < number_of_issues:
                current_issue += 1
                if type(report[current_issue - 1]) == possible_duplicate.FingerprintMatch:
                    window["View Match Info"].update(visible=True)
                else:
                    window["View Match Info"].update(visible=False)
                window['-DESCRIPTION-'].update(str(report[current_issue - 1]))

        if temp_event == "Prev":
            if current_issue > 1:
                current_issue -= 1
                if type(report[current_issue - 1]) == possible_duplicate.FingerprintMatch:
                    window["View Match Info"].update(visible=True)
                else:
                    window["View Match Info"].update(visible=False)
                window['-DESCRIPTION-'].update(str(report[current_issue - 1]))

        if temp_event == "View Match Info":
            create_temp_applicant_window(report[current_issue - 1].match)

        if temp_event == "Exit":
            window.close()
            return

        if temp_event == sg.WINDOW_CLOSED:
            window.close()
            return


def check_settings_values(settings_object):
    report = ""
    if not os.path.isdir(settings_object.download_folder_path) or not os.path.isdir(settings_object.database_folder_path):
        report += "Please enter valid directories\n"
    try:
        if not 0 <= settings_object.default_check_level <= 100:
            report += "Please enter a match level from 0 to 100\n"
    except ValueError:
        report += "Please enter an integer as the match level"
    return report


def create_settings_window():
    layout = [[sg.Text("Downloads Folder:"), sg.InputText(current_settings.download_folder_path, key="-FILE PATH-"), sg.Button("Select Folder", key="-SF1-")],
              [sg.Text("Database Folder:"), sg.InputText(current_settings.database_folder_path, key="-DB PATH-"), sg.Button("Select Folder", key="-SF2-")],
              [sg.Text("Default Match Level:"), sg.InputText(current_settings.default_check_level,size=(3, 1), key='-MATCH LEVEL-'), sg.Text("%")],
              [sg.Text("Automatically Download Summary?"),
               sg.Radio("Yes", "AD", key="-AUTO DOWNLOAD1-", default=current_settings.auto_download_summary),
               sg.Radio("No", "AD", key="-AUTO DOWNLOAD2-", default=not current_settings.auto_download_summary)],
              [sg.Text("Include Dev Values in Report?"),
               sg.Radio("Yes", "ID", key="-INCLUDE DEV1-", default=current_settings.include_dev_values),
               sg.Radio("No", "ID", key="-INCLUDE DEV2-", default=not current_settings.include_dev_values)],
              [sg.Text("Preferred File Format"),
               sg.Radio("CSV", "CSV", key="-FILE FORMAT1-", default=current_settings.csv),
               sg.Radio("Excel", "CSV", key="-FILE FORMAT2-", default=not current_settings.csv)],
              [sg.Button("Save Settings")]]

    window = sg.Window("Edit Settings", layout=layout, modal=True)

    while True:

        temp_event, temp_values = window.read(timeout=10)

        if temp_event == "Save Settings" or temp_event == sg.WINDOW_CLOSED:

            temp_settings = settings.Settings(
                download_folder_path=temp_values['-FILE PATH-'],
                database_folder_path=temp_values['-DB PATH-'],
                default_check_level=int(temp_values['-MATCH LEVEL-']),
                auto_download_summary=temp_values['-AUTO DOWNLOAD1-'],
                include_dev_values=temp_values['-INCLUDE DEV1-'],
                csv=temp_values['-FILE FORMAT1-']
            )

            check = check_settings_values(temp_settings)
            print(check)

            if check != "":
                sg.Popup(check)
                continue

            window.close()
            return temp_settings

        if temp_event == "-SF1-":
            directory = select_cvs.choose_directory()
            window['-FILE PATH-'].update(directory)

        if temp_event == "-SF2-":
            directory = select_cvs.choose_directory()
            window['-DB PATH-'].update(directory)


# flag variables
cvs_loaded = False
database_started = False
summary_loaded = False
verify_loaded = False

while True:

    event, values = window.read(timeout=10)

    if current_window == 'main_menu':
        if event == 'Upload CVs':
            location = window.current_location()
            window.close()
            window = sg.Window('Duplicate CV Checker - Saatvik',
                               upload_cvs,
                               location=location)
            current_window = 'upload_cvs'
            continue
        if event == 'Settings':
            current_settings = create_settings_window()
            current_settings.json_serialise()

    if current_window == 'upload_cvs':
        if event == 'Upload Files':
            files = select_cvs.select_batch()
        if event == 'Upload Folder':
            files = select_cvs.select_folder()
        if event == 'Upload Folder' or event == 'Upload Files':
            location = window.current_location()
            window.close()
            window = sg.Window('Duplicate CV Checker - Saatvik',
                               check_parse_results,
                               location=location)
            current_window = 'check_parse_results'
            continue

    if current_window == 'check_parse_results':

        if not cvs_loaded:

            current_applicant = 1
            total_applicants = len(files)

            current_progress = 0
            window['-PROGRESS BAR-'].update(0, max=total_applicants)

            # load the cvs into applicant objects
            applicant_list = []
            for file_path in files:
                applicant_list.append(applicant.applicant_from_pdf(file_path))
                current_progress += 1
                window['-PROGRESS BAR-'].update(current_progress)

            window['-PROGRESS BAR-'].update(current_progress, visible=False)
            window['-PROMPT-'].update(visible=True)

            cvs_loaded = True

            window.refresh()

            # initialise starting applicant page

            window['-FRAME-'].update(f"Applicant {current_applicant}/{total_applicants}")
            window['-NAME-'].update(applicant_list[current_applicant - 1].name)
            window['-EMAIL-'].update(applicant_list[current_applicant - 1].email)
            window['-NUMBER-'].update(applicant_list[current_applicant - 1].number)

            continue

        if event == 'Next':

            # grab values from input box
            name = values['-NAME-']
            email = values['-EMAIL-']
            number = values['-NUMBER-']

            # edit applicant with new values
            applicant_list[current_applicant - 1].name = name
            applicant_list[current_applicant - 1].email = email
            applicant_list[current_applicant - 1].number = number

            # check if last applicant
            if current_applicant == total_applicants:
                location = window.current_location()
                window.close()
                window = sg.Window('Duplicate CV Checker - Saatvik',
                                   verify_check_level,
                                   location=location)
                current_window = 'verify_check_level'

                continue

            # otherwise move to next applicant
            current_applicant += 1
            window['-FRAME-'].update(f"Applicant {current_applicant}/{total_applicants}")
            window['-NAME-'].update(applicant_list[current_applicant - 1].name)
            window['-EMAIL-'].update(applicant_list[current_applicant - 1].email)
            window['-NUMBER-'].update(applicant_list[current_applicant - 1].number)

        if event == 'Open This CV':
            os.startfile(files[current_applicant - 1])

    if current_window == 'verify_check_level':

        if not verify_loaded:
            window['-CHECK LEVEL-'].update(str(current_settings.default_check_level))
            verify_loaded = True
            continue

        if event == 'Next':
            check_level = int(values['-CHECK LEVEL-'])

            location = window.current_location()
            window.close()
            window = sg.Window('Duplicate CV Checker - Saatvik',
                               adding_to_database,
                               location=location)
            current_window = 'adding_to_database'
            continue

    if current_window == 'adding_to_database':

        if not database_started:
            window['-PROGRESS BAR-'].update(0, max=total_applicants)
            progress_made = 0
            window['-PROGRESS BAR-'].update(progress_made)
            all_reports = []  # each report corresponds to an element in flagged
            flagged = []
            successful = []

            for applicant in applicant_list:
                current_report = key_value_lookup.check_duplicate(applicant, check_level)
                if len(current_report) == 0:
                    key_value_lookup.add_applicant(applicant)
                    successful.append(applicant)
                else:
                    all_reports.append(current_report)
                    flagged.append(applicant)

                progress_made += 1
                window['-PROGRESS BAR-'].update(progress_made)

            window['View Summary'].update(visible=True)
            window['-STATUS-'].update("Finished adding applicants to the database")
            database_started = True

        if event == 'View Summary':
            location = window.current_location()
            window.close()
            window = sg.Window('Duplicate CV Checker - Saatvik',
                               summary,
                               location=location)
            current_window = 'summary'
            continue

    if current_window == 'summary':

        if not summary_loaded:
            current_flagged = 1
            current_successful = 1

            total_successful = len(successful)
            total_flagged = len(flagged)

            # hides tabs if empty
            if total_successful == 0:
                window['-UPLOADED-'].update(disabled=True)

            if total_flagged == 0:
                window['-FLAGGED-'].update(visible=False)
                window['-FLAGGED-'].update(disabled=True)

            # update tab names
            window['-UPLOADED-'].update(f"Uploaded Applicants ({total_successful})")
            window['-FLAGGED-'].update(f"Flagged Applicants ({total_flagged})")

            # update frame names and
            # update initial frame states
            if total_successful != 0:
                window['-UP NAME-'].update(successful[0].name)
                window['-UP FRAME-'].update(f"Applicant {current_successful}/{total_successful}")
            else:
                window['-UP A INFO-'].update(disabled=True)

            if total_flagged != 0:
                window['-F NAME-'].update(flagged[0].name)
                window['-F FRAME-'].update(f"Applicant {current_flagged}/{total_flagged}")
            else:
                window['-F A INFO-'].update(disabled=True)
                window['Duplicate Info'].update(disabled=True)

            # auto downloads reports if required
            if current_settings.auto_download_summary:
                download_path = current_settings.download_folder_path
                if current_settings.csv:
                    download.download_csv(successful, download_path, "successful_summary",
                                          dev_values=current_settings.include_dev_values)
                    download.download_csv(flagged, download_path, "flagged_summary", all_reports,
                                          dev_values=current_settings.include_dev_values)
                else:
                    download.download_excel(successful, download_path, "successful_summary",
                                            dev_values=current_settings.include_dev_values)
                    download.download_excel(flagged, download_path, "flagged_summary", all_reports,
                                            dev_values=current_settings.include_dev_values)

            summary_loaded = True

        if event == '-UP NEXT-':
            if current_successful >= total_successful:
                continue
            else:
                current_successful += 1
                window['-UP NAME-'].update(successful[current_successful - 1].name)
                window['-UP FRAME-'].update(f"Applicant {current_successful}/{total_successful}")

        if event == '-UP PREV-':
            if current_successful <= 1:
                continue
            else:
                current_successful -= 1
                window['-UP NAME-'].update(successful[current_successful - 1].name)
                window['-UP FRAME-'].update(f"Applicant {current_successful}/{total_successful}")

        if event == '-F NEXT-':
            if current_flagged >= total_flagged:
                continue
            else:
                current_flagged += 1
                window['-F NAME-'].update(flagged[current_flagged - 1].name)
                window['-F FRAME-'].update(f"Applicant {current_flagged}/{total_flagged}")

        if event == '-F PREV-':
            if current_flagged <= 1:
                continue
            else:
                current_flagged -= 1
                window['-F NAME-'].update(flagged[current_flagged - 1].name)
                window['-F FRAME-'].update(f"Applicant {current_flagged}/{total_flagged}")

        if event == '-UP A INFO-':
            create_temp_applicant_window(successful[current_successful - 1])

        if event == '-F A INFO-':
            create_temp_applicant_window(flagged[current_flagged - 1])

        if event == 'Duplicate Info':
            create_temp_duplicate_window(all_reports[current_flagged - 1], flagged[current_flagged - 1])

        if event == 'Exit Program':
            exit()

        if event == '-UP CSV-':
            download_path = current_settings.download_folder_path
            download.download_csv(successful, download_path, "successful_summary",
                                  dev_values=current_settings.include_dev_values)

        if event == '-F CSV-':  # have to add error info
            download_path = current_settings.download_folder_path
            download.download_csv(flagged, download_path, "flagged_summary", all_reports,
                                  dev_values=current_settings.include_dev_values)

        if event == '-UP XL-':
            download_path = current_settings.download_folder_path
            download.download_excel(successful, download_path, "successful_summary",
                                    dev_values=current_settings.include_dev_values)

        if event == '-F XL-':  # have to add error info
            download_path = current_settings.download_folder_path
            download.download_excel(flagged, download_path, "flagged_summary", all_reports,
                                    dev_values=current_settings.include_dev_values)

    if event == sg.WINDOW_CLOSED:
        exit()
