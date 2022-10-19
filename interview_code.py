import re
import urllib
from zipfile import ZipFile
import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from bs4 import BeautifulSoup
from PyPDF2 import *
import requests
import threading
import concurrent.futures
from urllib.request import urlretrieve
import PyPDF2
import imageio
from poppler import *


def download_file(url):
    file_name = str(url).split("/")[-1].split(".")[0]
    req = requests.get(url)

    with open("data/" + file_name + ".zip", "wb") as file:
        for chunk in req.iter_content(chunk_size=65535):
            file.write(chunk)
            print("Chunk Written for: " + file_name)


def threaded_file_downloader(urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_file, urls)


def get_urls():
    with open("irs990.xml", 'r') as file:
        data = file.read()

    xml_bs_data = BeautifulSoup(data, "xml").find("ListBucketResult")
    irs_bs_request = requests.get(xml_bs_data["xmlns"])
    irs_soup = BeautifulSoup(irs_bs_request.content, "html.parser")

    url_2d = []

    # Get parent 'div' of month (shortcut to get to IRS990 by month)
    for month in irs_soup.findAll("p"):
        if month.find("strong") is not None:
            parent = month.parent

    # Creates 2D array of URLs to be downloaded
    for month_breakdown in parent.findAll("ul"):
        url_1d = []
        for sub_section in month_breakdown.findAll("li"):
            url_1d.append(sub_section.find("a")["href"])

        url_2d.append(url_1d)

    return url_2d


def download_files():
    url_2d = get_urls()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(threaded_file_downloader, url_2d)


def unzip_files(rel_dir_name):
    file_extension = ".zip"
    abs_dir_name = os.path.abspath(rel_dir_name)

    for zip_file in os.listdir(abs_dir_name):
        if zip_file.endswith(file_extension):
            abs_file_path = abs_dir_name + "\\" + zip_file.__str__()

            zip_ref = ZipFile(abs_file_path)
            zip_ref.extractall(abs_dir_name)
            zip_ref.close()
            os.remove(abs_file_path)


def pdf_to_image():
    print("none")


def find_revenue():
    pdf_pages = convert_from_path("010211483_201906_990_2021012717663616.pdf", 500)

    for page_enumeration, page in enumerate(pdf_pages):
        filename = f"page_{page_enumeration}.jpg"

        page.save(filename, "JPEG")


    '''with open("010211483_201906_990_2021012717663616.pdf", "rb") as file:
        image = imageio.imread(file.read())

        image_str = pytesseract.image_to_string(image)

        print(image_str)'''


    '''page = convert_from_path(
        "C:\\Users\\adibh\PycharmProjects\\MarketSmartCodeInterview\\data\\010211483_201906_990_2021012717663616.pdf",
        500)

    for pageNum, imgBlob in enumerate(page):
        text = pytesseract.image_to_string(imgBlob, lang="eng")

        with open("010211483_201906_990_2021012717663616.txt", "a") as file:
            file.write(text)'''


def run():
    run_downloader = input("Do you want to download all files? Note:" +
                           "This downloads all IRS990 files and takes significant time and memory resources (Y/N): ")

    run_downloader_bool = False

    if run_downloader == "Y" or run_downloader == "y":
        run_downloader_bool = True
        download_files()

    run_unzipper = input("Do you want to unzip all tiles in the 'data' folder? "
                         "Remove all non-'zip' folders (Y/N): ")

    run_unzipper_bool = False

    if run_unzipper == "Y" or run_unzipper == "y":
        run_unzipper_bool = True
        unzip_files("data")

    run_find_revenue = input("Do you want to find all revenue in IRS990 forms (Y/N): ")

    if run_find_revenue == "Y" or run_find_revenue == "y":
        find_revenue()
