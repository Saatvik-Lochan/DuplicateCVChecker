from pyresparser import ResumeParser
from select_cvs import select_batch


def parse_cv(file_path):
    data = ResumeParser(file_path).get_extracted_data()
    data['name'] = " ".join([name.capitalize() for name in data['name'].split(" ")])
    data = (data['name'], data['email'], data['mobile_number'])
    return data


if __name__ == '__main__':
    print(parse_cv(select_batch()[0]))