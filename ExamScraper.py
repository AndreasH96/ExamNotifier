import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import soupsieve
class ExamScraper:
    def __init__(self):
        self.academys  = ["ETN","HOV","ITE","LHS"]
        self.examDataFrame = {"ETN": None,"HOV": None,"ITE": None,"LHS": None}
        self.updateExamDataFrame()

    def updateHTMLSource(self):
        self.hhAvailableExamsSourceHTML = urllib.request.urlopen('https://www.hh.se/student/innehall-a-o/tentor-att-hamta-ut.html').read()
        self.soup= BeautifulSoup(self.hhAvailableExamsSourceHTML,"html.parser")
        
    def updateExamDataFrame(self):
        self.updateHTMLSource()
        examTableRowsHTML = {"ETN":None,"HOV":None, "ITE": None,"LHS":None}
        for caption in self.soup.find_all('caption'):
            for academy in self.academys:
                
                if (academy in caption.get_text() and academy != "ETN"):
                    print(academy)
                    print(caption.get_text())
                    examTableHTML = caption.find_parent('table', attrs={'class':'sv-responsiveTable sv-responsiveTable--stacked sv-responsiveTable--stackTable c6'})
                    examTableRowsHTML[academy] = examTableHTML.find_all('tr')
                
                elif (academy is "ETN" and examTableRowsHTML["ETN"] == None):
                    print(academy)
                    print(caption.get_text())
                    examTableHTML = self.soup.find('table', attrs={'class':'sv-responsiveTable sv-responsiveTable--stacked sv-responsiveTable--stackTable c6'})
                    examTableRowsHTML[academy] = examTableHTML.find_all('tr')
                
        exams = {"ETN":[],"HOV":[], "ITE": [],"LHS":[]}
        for academy in exams:
            for tableRow in examTableRowsHTML[academy]:
                tableData = tableRow.find_all('td')
                row = [tr.text.strip() for tr in tableData if tr.text.strip()]
                if row:
                    exams[academy].append(row)
            self.examDataFrame[academy] = pd.DataFrame(exams[academy], columns=["Date", "Course_Code", "Title", "Examinator"])

        for academy in self.academys:
            print("Academy {} \n {}".format(academy, self.examDataFrame.get(academy)))

    def getExamDataFrame(self):
        return self.examDataFrame