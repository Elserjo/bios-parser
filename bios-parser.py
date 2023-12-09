from html.parser import HTMLParser

import requests
import re
import time
import sys

# https://stackoverflow.com/questions/3276040/how-can-i-use-the-python-htmlparser-library-to-extract-data-from-a-specific-div

# linkExample = "https://bios-fix.com/index.php?forums/dell-bios-password-remove.236"
regularExpression = r'(?i)(Unlock bios password for )(?P<notebookName>[\s\S]+)'

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.__rec = False
        #self.__count = 0
        self.__dataArray = []
        self.__totalPages = 0

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, val in attrs:
                #print(attr, val)
                if attr == "data-previewurl":
                    self.__rec = True
                    # print(self.__rec)
                else:
                    self.__rec = False

        if tag == "div":
            for attr, val in attrs:
                if attr == "data-last":
                    self.__totalPages = int(val)
                    #print(self__totalPages)

    def handle_endtag(self, tag):
        # print(tag)
        if tag != "a" or tag != "h3":
            self.__rec = False

    def handle_data(self, data):
        if self.__rec:
            match = re.match(regularExpression, data)
            if match:
                notebookName = match.group("notebookName")
                self.__dataArray.append(notebookName)
            else:
                pass
                #self.__dataArray.append("Not Matching value!")

    def get_page_count(self):
        return self.__totalPages

    def get_data(self):
        return self.__dataArray

def main():

    if (len(sys.argv)) < 2:
        print("No args specified")
        return -1

    link = sys.argv[1]

    parser = MyHTMLParser()
    pageCount = 0

    response = requests.get(link) #first init launch for getting page count
    if response:
        content = response.text
        parser.feed(content)
        pageCount = parser.get_page_count()
        if not pageCount:
            print("Page count is null")
            parser.close()
            return -1
    else:
        print("Can not get response", response.status_code)
        parser.close()
        return -1

    parser.close()

    for i in range (pageCount):
        page = "/page-" + str(i + 1)
        response = requests.get(link + page)
        print("Processing page: ", link + page, "of", pageCount)

        if response:
            content = response.text
        else:
            print("Can not get response", response.status_code)
            return -1

        parser.feed(content)
        parser.close()
        time.sleep(1)

    uniqueModels = set(parser.get_data()) #clear same values in list

    print("All values: ", len(parser.get_data()), "Unique Values: ", len(uniqueModels))

    print(parser.get_data())

    with open("note.txt", 'w') as file:
        for line in uniqueModels:
            file.write(line + "\n")
    file.close()

main()
