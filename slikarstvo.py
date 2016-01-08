import csv
import re
from utils import *


shrani('http://www.wga.hu/art/index.html', 'podatki/index.html')

regex_url_abeceda = re.compile(
    r'/cgi-bin/artist.cgi\?letter=(?P<crka>[a-z])'
)

regex_stevilo_strani=re.compile(
    r'<DIV CLASS="LIST">Page\s\d\sof\s(?P<konec>\d{1,2})</DIV>'
)

for ujemanje in re.finditer(regex_url_abeceda, vsebina_datoteke('podatki/index.html')):
    url = 'http://www.wga.hu/cgi-bin/artist.cgi?letter={}'.format(ujemanje.group('crka'))
    ime_datoteke = 'podatki/slikarji/{}.html'.format(ujemanje.group('crka'))
    shrani(url, ime_datoteke)
    
    for ujemanje_strani in re.finditer(regex_stevilo_strani, vsebina_datoteke('podatki/slikarji/{}.html'.format(ujemanje.group('crka')))):
        strani=int(ujemanje_strani.group('konec'))
    
    regex_abeceda=re.compile(
        r'<a\shref="(?P<naslovi_crke>/cgi-bin/artist.cgi\?Profession=any&School=any&Period=any&Time-line=any&from=([^0]\d+)&max=50&Sort=Name&letter=(\w))">\d+</a>'
    )
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

regex_slikarja=re.compile(
    r'<B>(?P<Ime>.*)</B>'
    r'</A></TD><TD CLASS="ARTISTLIST">(?P<Leto>.*)</TD>'
    r'<TD CLASS="ARTISTLIST">(?P<Obdobje>.*)</TD>'
    r'<TD CLASS="ARTISTLIST">(?P<Narodnost>\w+)\s+(?P<Smer>\w+)\s+(?P<Kraj>.*)</TD>'   
)

for html_datoteka in datoteke('podatki/slikarji/'):
    if html_datoteka[-4:] == '.csv':
        continue
    csv_datoteka = html_datoteka.replace('.html','.csv')
    imena_polj = ['Ime','Leto','Obdobje','Narodnost','Smer','Kraj']
    with open(csv_datoteka, 'w',encoding='utf-8') as csv_dat:
        writer = csv.DictWriter(csv_dat, fieldnames=imena_polj)
        writer.writeheader()
        for ujemanje in re.finditer(regex_slikarja,vsebina_datoteke(html_datoteka)):
            writer.writerow(ujemanje.groupdict())

regex_slikarja=re.compile(
    r'<A HREF="http://www.wga.hu/html/(?P<crka>\w)/'
    r'(?P<Stran>.*)">'
    r'<B>(?P<Ime>.*)</B>'
)

for html_datoteka in datoteke('podatki/slikarji/'):
    if html_datoteka[-4:] == '.csv':
        continue
    for ujemanje in re.finditer(regex_slikarja,vsebina_datoteke(html_datoteka)):
        url_3='http://www.wga.hu/html/{0}/{1}'.format(html_datoteka[17],ujemanje.group('Stran'))
        ime_datoteke='podatki/slikarji/seznam/{}.html'.format(ujemanje.group('Ime'))
        shrani(url_3,ime_datoteke)

with open('podatki/vse.csv','a',encoding='utf-8') as fout:
    with open('podatki/slikarji/a.csv',encoding='utf-8') as prva:
        for line in prva:
            next(prva)
            fout.write(line)
    prva.close()
    for stran in filtriraj('podatki/slikarji/','.csv')[1:]:
        with open(stran,encoding='utf-8') as f:
            first_line = f.readline()
            first_line = f.readline()
            for line in f:
                next(f)
                fout.write(line)
        f.close()
fout.close()