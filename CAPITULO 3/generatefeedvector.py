
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import feedparser
import re
import codecs
charset = "utf-8"

# Devuelve el titulo y un diccionario de conteo de palabras de un feed RSS
def getwordcounts(url):
  # Analiza lexicamente el feed
  d=feedparser.parse(url)
  wc={}

  # itera sobre todas las entradas
  for e in d.entries:
    
    if 'summary' in e: summary=e.summary
    else: summary=e.description

    # extrae una lista de palabras
    words=getwords(e.title+' '+summary)
    for word in words:
      wc.setdefault(word,0)
      wc[word]+=1
  return d.feed.title,wc      

def getwords(html):
  # quita todas las etiquetas HTML
  txt=re.compile(r'<[^>]+>').sub('',html)

  # Divide las palabras con caracteres no alfabeticos
  # se utiliza ur' para incluir caracateres con tilde unicode
  words=re.compile(ur'[^A-Z^a-z^á-ü]+').split(txt) #### <===== OJO
  # Convierte a minusculas
  low = [word.lower() for word in words if word!='']
  return low

def parsefeeds(filefeeds='feedlist.txt'):
  apcount={}
  wordcounts={}
  file=open(filefeeds)
  feedlist=[line for line in file]
  for feedurl in feedlist:
    try:
      print(feedurl)
      title,wc=getwordcounts(feedurl)
      print('Leido')
      wordcounts[title]=wc
      for word,count in wc.items():
        apcount.setdefault(word,0)
        if count>1:
          apcount[word]+=1
    except:
      print ('Failed to parse feed %s' % feedurl)
  return feedlist, apcount, wordcounts

def generatedataset(filefeeds='feedlist.txt', filedataset='blogdata.txt'):
  feedlist, apcount, wordcounts = parsefeeds(filefeeds)
  #Elimina palabras cortas y muy frecuentes
  wordlist=[]
  for w,bc in apcount.items():
    frac=float(bc)/len(feedlist)
    if frac>0.1 and frac<0.5:
      wordlist.append(w)
  #Crea un archivo con todas las palabrac contadas
  out=codecs.open(filedataset,'w',charset)
  out.write('Blog')
  for word in wordlist: out.write('\t%s' % word)
  out.write('\n')
  for blog,wc in wordcounts.items():
    print (blog)
    out.write(blog)
    for word in wordlist:
      if word in wc: out.write('\t%d' % wc[word])
      else: out.write('\t0')
    out.write('\n')
  out.close()  
