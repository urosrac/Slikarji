import re
import zipfile
from utils import *
import csv

import urllib.request

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
            
def prenesi_katalog():
    
    pripravi_imenik('podatki/katalog/data_txt.zip')
    urllib.request.urlretrieve('http://www.wga.hu/database/download/data_txt.zip', 'podatki/katalog/data_txt.zip')
    with zipfile.ZipFile('podatki/katalog/data_txt.zip') as zf:
        zf.extractall('podatki/katalog/')

def preberi_katalog(ime_datoteke):
    with open(ime_datoteke,'r') as csv_dat:
        reader = csv.reader(csv_dat,delimiter=';')
        i=0
        for row in reader:
            print(row)
            if i==6:
                break
            i+=1
    csv_dat.close()
    

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
            if i==7:
                break
            slovar=slikar.groupdict()
            slovar['id']=i
            #slovar=slikar.groupdict().update({'id':i})
            #slovar=slikar.groupdict()['id']=i
            print(slovar)
            #podatki = slikar.groupdict()
            #slikarji[podatki['Ime']] = podatki
            i+=1
            
    zapisi_tabelo(slikarji.values(), ['Ime','Obdobje','Narodnost','Smer','Kraj'],
                         'csv-datoteke/slikarji.csv')
#prenesi_podatke()
#prenesi_katalog()
vpisi_podatke()
preberi_katalog('podatki/katalog/catalog.csv')
