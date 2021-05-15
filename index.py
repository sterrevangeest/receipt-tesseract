import pandas as pd
from string import digits
import re
import cv2
import pytesseract
from pytesseract import Output
import csv
import numpy as np


# get grayscale image


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# thresholding


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# dilation


def getData(thresh, url):
    d = pytesseract.image_to_data(thresh, output_type=Output.DICT)

    parse_text = []
    word_list = []
    last_word = ''
    for word in d['text']:
        if word != '':
            word_list.append(word)
            last_word = word
        if (last_word != '' and word == '') or (word == d['text'][-1]):
            parse_text.append(word_list)
            word_list = []

    with open(url + '.txt', 'w', newline='') as csvfile:
        csv.writer(csvfile, delimiter=" ").writerows(parse_text)


for i in range(1, 6):
    url = 'Bob/bon' + str(i) + ".jpg"
    image = cv2.imread(url)
    gray = get_grayscale(image)
    thresh = thresholding(gray)
    data = getData(thresh, url)

#####


df = pd.DataFrame()


def getProducts(url):
    mylines = []
    products = []
    data = []
    time = getTime(url)
    date = getDate(url)
    location = getLocation(url)

    with open(url, "rt") as myfile:
        for myline in myfile:
            if not myline.startswith("Lidl Plus korting"):
                mylines.append(myline.rstrip('\n'))

        # get products
        start = mylines.index("OMSCHRIJVING EUR") + 1
        stop = [mylines.index(l)
                for l in mylines if l.startswith('Te betalen')][0]

        for x in range(start, stop):

            res = re.sub('[0-9]', '', mylines[x])
            res = re.sub('[^\w\s]+', '', res)
            res = re.sub(r' x ', '', res)
            res = re.sub(r' X ', '', res)
            res = re.sub(r'kg', '', res)
            res = re.sub(r'EUR', '', res)
            res = re.sub(r'st', '', res)
            res = re.sub(r'L', '', res)

            if len(res) != 0:
                products.append(res)
                data.append({'Product': res, 'Date': date,
                             "Time": time, "Location": location})
                print(res, date, time, location)
    return data


def getLocation(url):
    mylines = []
    location = []
    with open(url, "rt") as myfile:
        for myline in myfile:
            if not myline.startswith("Lidl Plus korting"):
                mylines.append(myline.rstrip('\n'))

        # get products
        start = mylines.index("Aankoop gedaan bij") + 4

        stop = [mylines.index(l)
                for l in mylines if l.startswith('Ma.')][0]

        for x in range(start, stop):
            if len(mylines[x]) != 0:
                location.append(mylines[x])
                return mylines[x]


def getTime(url):
    mylines = []
    time = []
    with open(url, "rt") as myfile:
        for myline in myfile:
            mylines.append(myline.rstrip('\n'))

        # get products
        start = mylines.index("BETALING") + 1
        stop = start + 1

        for x in range(start, stop):
            if len(mylines[x]) != 0:
                time = mylines[x][11:16]
                return time


def getDate(url):
    mylines = []
    time = []
    with open(url, "rt") as myfile:
        for myline in myfile:
            mylines.append(myline.rstrip('\n'))

        # get products
        start = mylines.index("BETALING") + 1
        stop = start + 1

        for x in range(start, stop):
            if len(mylines[x]) != 0:
                date = mylines[x][:10]
                return date


for i in range(1, 6):
    url = 'Bob/bon' + str(i) + ".jpg.txt"
    data = getProducts(url)
    for row in data:
        if len(row['Product']) > 2:
            df = df.append(row, ignore_index=True)
        df.to_csv('receipt_df.csv')


cv2.waitKey(0)
