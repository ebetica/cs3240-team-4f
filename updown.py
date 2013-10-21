__author__ = 'rbq2rd'

import requests


def upload_file(url, filename):
    url = url + '/post/' + filename
    files = {'file': open(filename,'rb')}
    r = requests.post(url,files=files)


def download_file(url,filename):
    url = url + '/uploads/' + filename
    r = requests.get(url)
    with open(filename, 'wb') as code:
        code.write(r.content)


def main():
    url = 'http://127.0.0.1:5000' # wherever our server is
    filename = 'server.py' # some file
    # uploads filename to url
    upload_file(url, filename)
    # downloads the filename uploaded to url and names it ;'banana.txt'
    download_file(url, 'banana.txt')


if __name__ == "__main__":
    main()
