__author__ = 'rbq2rd'

import requests
import constants

#Uploads directory as specified in server.py::upload_file() must exist



def main():
    url = constants.SERVER_ADDRESS # wherever our server is
    filename = 'server.py' # some file
    # uploads filename to url
    upload_file(url, filename)
    # downloads the filename uploaded to url and names it ;'banana.txt'
    download_file(url, 'banana.txt')


if __name__ == "__main__":
    main()
