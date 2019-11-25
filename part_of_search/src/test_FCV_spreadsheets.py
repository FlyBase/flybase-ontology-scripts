import unittest
from FCA_spreadsheet_tools import generate_report


class TestFCAspreadsheets(unittest.TestCase):

    def test_generate_report(self):
        id_list = ['http://purl.obolibrary.org/obo/FBbt_00004172',
                   'http://purl.obolibrary.org/obo/FBbt_00004173',
                   'http://purl.obolibrary.org/obo/FBbt_00004174',
                   'http://purl.obolibrary.org/obo/FBbt_00004175',
                   'http://purl.obolibrary.org/obo/FBbt_00004176']

        generate_report(iri_list=id_list,
                        fbbt_path="./resources/fbbt-simple.json",
                        xlsx_out="test_report.xlsx")

if __name__ == '__main__':
    unittest.main()
