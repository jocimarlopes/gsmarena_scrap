from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint
import subprocess
import os


URL = 'https://www.gsmarena.com/'

dataframe = []

def init():
    get_links()

def get_links():
    try:
        switch_vpn()
        page = requests.get(URL + 'makers.php3')
        soup = BeautifulSoup(page.text, 'html.parser')
        for span_tag in soup.findAll('span'):
            span_tag.replace_with('')
        table = soup.find('table')
        brands_list = table.find_all('a')
        for a in brands_list:
            brand = a.text.strip()
            link = a.get('href')
            print('Pegando marca: ' + brand)
            get_models_from_brand(brand, link)
        return
    except Exception as e:
        print(e)
        get_links()

def get_models_from_brand(brand, link):
    try:
        switch_vpn()
        page = requests.get(URL + link)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find("div", {"class": "makers"})
        model_list = table.find_all('a')
        for a in model_list:
            print('Acessando modelos da marca: ' + brand)
            model_title = a.text.strip()
            model_link = a.get('href')
            image = a.find('img')
            image_link = image.get('src')
            get_model_infos(brand, model_title, model_link, image_link)
        get_models_from_pagelist(brand, link)
        save_to_excel(brand)
        return
    except Exception as e:
        switch_vpn()
        save_to_excel('backup_error' + str(brand + '_-_' + datetime.now()))
        get_models_from_brand(brand, link)
        print(e)

def get_model_infos(brand, model, link, image):
    try:
        sleep(0.08)
        print('Pegando modelo: ' + model)
        print('=' * 20)
        page = requests.get(URL + link)
        soup = BeautifulSoup(page.text, 'html.parser')

        td_dimension = soup.find("td", {"data-spec": "dimensions"})
        dimension = td_dimension.text.strip()

        td_displaysize = soup.find("td", {"data-spec": "displaysize"})
        displaysize = td_displaysize.text.strip()

        released_at = soup.find("td", {"data-spec": "status"})
        status_release = released_at.text.strip()
        
        data = [
            brand,
            model,
            dimension,
            displaysize,
            image,
            status_release
        ]
        print('------------')
        print(data)
        print('------------')
        print('Salvando modelo [' + str(brand) + ' - ' + str(model) + ']')
        print('Numero: ' + str(len(dataframe)))
        print('=' * 20)
        dataframe.append(data)
    except Exception as e:
        switch_vpn()
        save_to_excel('backup_error' + str(brand + '_-_' + datetime.now()))
        get_model_infos(brand, model, link, image)
        print(e)

def save_to_excel(brand):
    print('brand: ' + brand)
    print('dataframe: ', dataframe)
    df1 = pd.DataFrame(dataframe,
                   columns=['Marca', 'Modelo', 'Dimensão', 'Polegada', 'Foto', 'Lançamento'])
    df1.to_excel(str(brand) + ".xlsx")
    return

def switch_vpn():
    print('Trocando IP..')
    command = "protonvpn-cli c -r"
    proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sleep(8)
    print('IP Trocado..')
    
def disconnect_vpn():
    print('Desconectando VPN..')
    command = "protonvpn-cli d"
    proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sleep(8)
    print('VPN Desconectada..')

def get_models_from_pagelist(brand, brand_link):
    page = requests.get(URL + brand_link)
    soup = BeautifulSoup(page.text, 'html.parser')
    try:
        navPages = soup.find("div", {"class": "nav-pages"})
        a = navPages.find_all('a')
        for item in a:
            switch_vpn()
            page = requests.get(URL + item.get('href'))
            soup = BeautifulSoup(page.text, 'html.parser')
            table = soup.find("div", {"class": "makers"})
            model_list = table.find_all('a')
            for a in model_list:
                print('Acessando modelos da marca: ' + brand)
                model_title = a.text.strip()
                model_link = a.get('href')
                image = a.find('img')
                image_link = image.get('src')
                get_model_infos(brand, model_title, model_link, image_link)
    except Exception as e:
        print(e)
        print('Apenas uma página')


if __name__ == '__main__':
    init()
