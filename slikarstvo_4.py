import re
import zipfile
from utils import *
import csv
import os
import urllib.request
#import shutil

#Prvi del.
def prenesi_podatke():
    #Shrani index strani.
    shrani('http://www.wga.hu/art/index.html', 'podatki/index.html')
    #Regularni izraz za črke.
    regex_url_abeceda = re.compile(
        r'/cgi-bin/artist.cgi\?letter=(?P<crka>[a-z])'
    )
    #Regularni izraza za število strani.
    regex_stevilo_strani=re.compile(
        r'<DIV CLASS="LIST">Page\s\d\sof\s(?P<konec>\d{1,2})</DIV>'
    )
    #Prenese vse strani glede na črko s spletne strani.
    for ujemanje in re.finditer(regex_url_abeceda, vsebina_datoteke('podatki/index.html')):
        url = 'http://www.wga.hu/cgi-bin/artist.cgi?letter={}'.format(ujemanje.group('crka'))
        ime_datoteke = 'podatki/slikarji/{}.html'.format(ujemanje.group('crka'))
        shrani(url, ime_datoteke)
        #Preberemo število strani neke črke.
        for ujemanje_strani in re.finditer(regex_stevilo_strani, vsebina_datoteke('podatki/slikarji/{}.html'.format(ujemanje.group('crka')))):
            strani=int(ujemanje_strani.group('konec'))
        #Regularni izraz za preostale strani neke črke (vse razen prve).
        regex_abeceda=re.compile(
            r'<a\shref="(?P<naslovi_crke>/cgi-bin/artist.cgi\?Profession=any&School=any&Period=any&Time-line=any&from=([^0]\d+)&max=50&Sort=Name&letter=(\w))">\d+</a>'
        )
        #Za vsako stran prenesemo preostale strani neke črke.
        strani-=1
        i=2
        for ujemanje_crk in re.finditer(regex_abeceda, vsebina_datoteke('podatki/slikarji/{}.html'.format(ujemanje.group('crka')))):
            if strani==0:
                break        
            url_2='http://www.wga.hu{}'.format(ujemanje_crk.group('naslovi_crke'))
            ime_datoteke_2 = 'podatki/slikarji/{0}_{1}.html'.format(ujemanje.group('crka'),str(i))
            shrani(url_2,ime_datoteke_2)
            i+=1
            strani-=1
    
    #Regularni izraz za stran podatkov slik slikarja.
    regex_slikarja=re.compile(
        r'<A HREF="http://www.wga.hu/html/(?P<Slikar>.*)'
        r'/index.html">'
        r'<B>(?P<Ime>.*)</B>'
    )
    #Prenesemo strani slikarjev.
    for html_datoteka in datoteke('podatki/slikarji/'):
        for ujemanje in re.finditer(regex_slikarja,vsebina_datoteke(html_datoteka)):
            url_3='http://www.wga.hu/html/{}/index.html'.format(ujemanje.group('Slikar'))
            ime_datoteke='podatki/seznam_slikarjev/{}.html'.format(ujemanje.group('Ime'))
            shrani(url_3,ime_datoteke)

def vpisi_podatke():
    #Regularni izraz za podatke o slikarju.
    regex_slikarja=re.compile(
        r'<B>(?P<Ime>.*)</B>'
        r'</A></TD><TD CLASS="ARTISTLIST">.*</TD>'
        r'<TD CLASS="ARTISTLIST">(?P<Obdobje>.*)</TD>'
        r'<TD CLASS="ARTISTLIST">(?P<Narodnost>\w+)\s+(?P<Smer>\w+)\s+(\((?P<Kraj>.*)\))?</TD>'
    )    
    slikarji = {}
    i=0
    for html_datoteka in datoteke('podatki/slikarji/'):
        for slikar in re.finditer(regex_slikarja,vsebina_datoteke(html_datoteka)):
            podatki=slikar.groupdict()
            podatki['Id']=str(i)
            slikarji[podatki['Id']]=podatki
            i+=1
            
    zapisi_tabelo(slikarji.values(), ['Id','Ime','Obdobje','Narodnost','Smer','Kraj'],
                         'csv-datoteke/slikarji_prebrano.csv')
#Drugi del.        
def prenesi_katalog():
    
    pripravi_imenik('podatki/katalog/data_txt.zip')
    urllib.request.urlretrieve('http://www.wga.hu/database/download/data_txt.zip', 'podatki/katalog/data_txt.zip')
    with zipfile.ZipFile('podatki/katalog/data_txt.zip') as zf:
        zf.extractall('podatki/katalog/')
    os.remove('podatki/katalog/data_txt.zip')

def preberi_katalog(ime_datoteke):
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
            slovar_slik[str(j)] = {'Id_slike':str(j),'Id_slikarja':Id_slikarja,'Naslov':row[2],'Tehnika':row[4],'Lokacija':row[5],'Oblika':row[7],'Tip':row[8]}
            slovar_linkov[str(j)]={'Id_slike':str(j),'Id_slikarja':Id_slikarja,'Linki':row[6]}
            j+=1
    
    zapisi_tabelo(slovar_slikarjev.values(), ['Id_slikarja','Ime','Narodnost','Obdobje'],
                         'csv-datoteke/seznam_slikarji.csv')
    zapisi_tabelo(slovar_slik.values(), ['Id_slike','Id_slikarja','Naslov','Tehnika','Lokacija','Oblika','Tip'],
                         'csv-datoteke/seznam_slik.csv')
    zapisi_tabelo(slovar_linkov.values(),['Id_slike','Id_slikarja','Linki'],'csv-datoteke/seznam_linkov.csv')

def prenesi_slike(ime_csv):
    
    #if os.path.exists('podatki/seznam_slik/') and datoteke('podatki/seznam_slik/') != []:
    #    zadnja = datoteke('podatki/seznam_slik/')[-1]
    #    shutil.rmtree(zadnja)
    
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

#prenesi_podatke()
#vpisi_podatke()

prenesi_katalog()
preberi_katalog('podatki/katalog/catalog.csv')

prenesi_slike('csv-datoteke/seznam_linkov.csv')