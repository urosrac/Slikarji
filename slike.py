import urllib.request
import re
from utils import *

#d=urllib.request.urlretrieve('http://www.wga.hu/art/a/aagaard/deerlake.jpg', 'deerlake.jpg')

regex_slike=re.compile(
    r'<a href="/art/(?P<Crka>[a-z])/(?P<Slikar_link>.*)/(?P<Slika>.*.jpg)"',
    re.MULTILINE
)

def shrani_sliko(url, ime_slike, vsili_prenos=False): #Popravi!
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
    print('shranjeno!')

for html_datoteka in datoteke('podatki/seznam_slikarjev/'):
    for slika in re.finditer(regex_slike,vsebina_datoteke(html_datoteka)):
        url='http://www.wga.hu/art/{0}/{1}/{2}'.format(slika.group('Crka'),slika.group('Slikar_link'),slika.group('Slika'))
        ime_slike='podatki/seznam_slik/{0}/{1}'.format(slika.group('Slikar_link'),slika.group('Slika'))
        shrani_sliko(url, ime_slike)