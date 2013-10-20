__author__ = 'rbq2rd'
import os
from flask import Flask, request
import requests

def upload_file(self, url, filename):
    files = {'file': open(filename,'rb')}
    r = requests.post(url,files=files)
def download_file(self,url,filename):
    r = requests.get(url)
    with open(filename, 'wb') as code:
        code.write(r.content)

def main():
    url = '' # wherever our server is
    filename = '' #some file
    #uploads filename to url
    upload_file(url, filename)
    #downloads the filename uploaded to url and names it ;'banana.txt'
    download_file(url, 'banana.txt')


if __name__ == "__main__":
    main()