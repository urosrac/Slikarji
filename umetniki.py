import zipfile
import csv
import os
import sys
import urllib.request
import requests

def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)

def zapisi_tabelo(slovarji, imena_polj, ime_datoteke):
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w',encoding='utf-8') as csv_dat:
        writer = csv.DictWriter(csv_dat, fieldnames=imena_polj,delimiter=';')
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)
            
def shrani_sliko(url, ime_slike, vsili_prenos=False):
    try:
        print('Shranjujem {}...'.format(url), end='')
        sys.stdout.flush()
        if os.path.isfile(ime_slike) and not vsili_prenos:
            print('shranjeno že od prej!')
            return
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
    pripravi_imenik(ime_slike)
    urllib.request.urlretrieve(url,ime_slike)
        
def prenesi_katalog():
    print('Shranjujem katalog...')
    pripravi_imenik('podatki/katalog/data_txt.zip')
    urllib.request.urlretrieve('http://www.wga.hu/database/download/data_txt.zip', 'podatki/katalog/data_txt.zip')
    with zipfile.ZipFile('podatki/katalog/data_txt.zip') as zf:
        zf.extractall('podatki/katalog/')
    os.remove('podatki/katalog/data_txt.zip')

def preberi_katalog(ime_datoteke):
    print('Berem katalog...')
    slovar_slikarjev={}
    slovar_slik={}
    slovar_linkov={}
    imena=[]
    i=0
    j=0
    with open(ime_datoteke,'r',newline='') as csv_dat:
        csv_dat.readline()        
        reader = csv.reader(csv_dat,delimiter=';')
        for row in reader:
            Ime,Narodnost,Obdobje,Id_slikarja = row[0],row[9],row[10],str(i)
            if Ime not in imena:
                imena.append(Ime)
                slovar_slikarjev[str(i)] = {'Id_slikarja':Id_slikarja,'Ime':Ime,'Narodnost':Narodnost,'Obdobje':Obdobje}
                i+=1
            slovar_slik[str(j)] = {'Id_slike':str(j),'Id_slikarja':str(i-1),'Naslov':row[2],'Tehnika':row[4],'Lokacija':row[5],'Oblika':row[7],'Tip':row[8]}
            slovar_linkov[str(j)]={'Id_slike':str(j),'Id_slikarja':str(i-1),'Linki':row[6]}
            j+=1
    
    zapisi_tabelo(slovar_slikarjev.values(), ['Id_slikarja','Ime','Narodnost','Obdobje'],
                         'csv-datoteke/seznam_slikarji.csv')
    zapisi_tabelo(slovar_slik.values(), ['Id_slike','Id_slikarja','Naslov','Tehnika','Lokacija','Oblika','Tip'],
                         'csv-datoteke/seznam_slik.csv')
    zapisi_tabelo(slovar_linkov.values(),['Id_slike','Id_slikarja','Linki'],'csv-datoteke/seznam_linkov.csv')
    print('Končano')
def prenesi_slike(ime_csv):    
    link=[]
    with open(ime_csv,'r') as csv_dat:
        csv_dat.readline()        
        reader = csv.reader(csv_dat,delimiter=';')
        for row in reader:
            if row:
                link=row[2]
                link=link[:18]+'art'+link[22:-4]+'jpg'
                id_slikarja,id_slike = row[1],row[0]
                ime_slike='podatki/seznam_slik/{0}/{1}'.format(id_slikarja,id_slike)
                shrani_sliko(link, ime_slike+'.jpg')

prenesi_katalog()
preberi_katalog('podatki/katalog/catalog.csv')

prenesi_slike('csv-datoteke/seznam_linkov.csv')