# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 17:02:13 2016

@author: Uporabnik
"""

for i in filter(lambda s: s.endswith('csv'),datoteke('podatki/slikarji/')):
    print(i)