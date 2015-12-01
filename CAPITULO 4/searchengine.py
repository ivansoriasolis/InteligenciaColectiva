#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
from bs4 import *
from urlparse import urljoin
import re

import sqlite3 as sqlite

# Crea una lista de palabras a ignorar
ignorewords=set(['the','of','to','and','a','in','is','it'])

class crawler:
  # Inicializa el crawler con el nombre de la base de datos
  def __init__(self,dbname):
    self.con=sqlite.connect(dbname)

  def __del__(self,dbname):
    self.con.close()
	
  def dbcommit(self):
    self.con.commit()
	
  # Funcion auxiliar para obtener un ID de entrada y adiciona
  # este si no estÃ¡ presente
  def getentryid(self,table,field,value,createnew=True):
    cur=self.con.execute(
    "select rowid from %s where %s='%s'" % (table,field,value))
    res=cur.fetchone( )
    if res==None:
      cur=self.con.execute(
      "insert into %s (%s) values ('%s')" % (table,field,value))
      return cur.lastrowid
    else:
      return res[0]
	
  # Indexa una pagina individual
  def addtoindex(self,url,soup):
    if self.isindexed(url): return
    print 'Indexing '+url
    # Get the individual words
    text=self.gettextonly(soup)
    words=self.separatewords(text)
    # Get the URL id
    urlid=self.getentryid('urllist','url',url)
    # Link each word to this url
    for i in range(len(words)):
      word=words[i]
      if word in ignorewords: continue
      wordid=self.getentryid('wordlist','word',word)
      self.con.execute("insert into wordlocation(urlid,wordid,location) \
        values (%d,%d,%d)" % (urlid,wordid,i))
  
  # Extrae el texto a partir de una pagina HTML (sin etiquetas)
  def gettextonly(self,soup):
    v=soup.string
    if v==None:
      c=soup.contents
      resulttext=''
      for t in c:
        subtext=self.gettextonly(t)
        resulttext+=subtext+'\n'
      return resulttext
    else:
      return v.strip( )
	  
  # Separa las palabras por un caracter que no sea espacio en blanco
  def separatewords(self,text):
    splitter=re.compile('\\W*')
    return [s.lower( ) for s in splitter.split(text) if s!='']
	
  # Devuelve True si este URL ya esta indexado
  def isindexed(self,url):
    u=self.con.execute \
      ("select rowid from urllist where url='%s'" % url).fetchone( )
    if u!=None:
      # Check if it has actually been crawled
      v=self.con.execute(
      'select * from wordlocation where urlid=%d' % u[0]).fetchone( )
      if v!=None: return True
    return False
  
  # Agrega un link entre dos paginas
  def addlinkref(self,urlFrom,urlTo,linkText):
    pass
  # Iniciando con una lista de pÃ¡ginas, hace una busqueda
  # primero en anchura hasta la profundidad dada
  # indexando las paginas que lleguen
  def crawl(self,pages,depth=2):
    pass
  # Crea las tablas de la base de datos
  
  def createindextables(self):
    self.con.execute('create table urllist(url)')
    self.con.execute('create table wordlist(word)')
    self.con.execute('create table wordlocation(urlid,wordid,location)')
    self.con.execute('create table link(fromid integer,toid integer)')
    self.con.execute('create table linkwords(wordid,linkid)')
    self.con.execute('create index wordidx on wordlist(word)')
    self.con.execute('create index urlidx on urllist(url)')
    self.con.execute('create index wordurlidx on wordlocation(wordid)')
    self.con.execute('create index urltoidx on link(toid)')
    self.con.execute('create index urlfromidx on link(fromid)')
    self.dbcommit( )
	
  def crawl(self,pages,depth=2):
    for i in range(depth):
      newpages=set( )
      for page in pages:
        try:
          c=urllib2.urlopen(page)
        except:
          print "Could not open %s" % page
          continue
        cad=c.read()
        soup=BeautifulSoup(cad,'html.parser')
        self.addtoindex(page,soup)
        links=soup('a')
        for link in links:
          if ('href' in dict(link.attrs)):
            url=urljoin(page,link['href'])
            if url.find("'")!=-1: continue
            url=url.split('#')[0]  # quitar la porcion de localizacion
            if url[0:4]=='http' and not self.isindexed(url):
              newpages.add(url)
            linkText=self.gettextonly(link)
            self.addlinkref(page,url,linkText)
        self.dbcommit( )
      pages=newpages

  def calculatepagerank(self,iterations=20):
    # limpiamos las tablas pagerank actuales
    self.con.execute(
	 'drop table if exists pagerank')
    self.con.execute(
	 'create table pagerank(urlid primary key,score)')
    # Inicializar cada pagerank de 1
    self.con.execute(
	 'insert into pagerank select rowid, 1.0 from urllist')
    self.dbcommit( )
    for i in range(iterations):
      print "Iteration %d" % (i)
      for (urlid,) in self.con.execute('select rowid from urllist'):
        pr=0.15
        # Iterando en todas las paginas que enlazan a esta
        for (linker,) in self.con.execute(
        'select distinct fromid from link where toid=%d' % urlid):
          # Obtiene el PageRank del enlazador
          linkingpr=self.con.execute(
          'select score from pagerank where urlid=%d'
		  % linker).fetchone( )[0]
          # Obtenermos el numero total de enlaces desde el enlazador
          linkingcount=self.con.execute(
          'select count(*) from link where fromid=%d'
		  % linker).fetchone( )[0]
          pr+=0.85*(linkingpr/linkingcount)
        self.con.execute(
        'update pagerank set score=%f where urlid=%d' % (pr,urlid))
      self.dbcommit( )

class searcher:
  def __init__(self, dbname):
    self.con = sqlite.connect(dbname)
	
  def __del__(self):
    self.con.close()
	
  def getmatchrows(self,q):
    # Cadenas para construir la consulta
    fieldlist='w0.urlid'
    tablelist=''
    clauselist=''
    wordids=[]
    # Dividir las palabras por los espacios
    words=q.split(' ')
    tablenumber=0
    for word in words:
        # Obtener el ID de la palabra
        wordrow=self.con.execute(
          "select rowid from wordlist where word='%s'" % word).fetchone( )
        if wordrow!=None:
          wordid=wordrow[0]
          wordids.append(wordid)
          if tablenumber>0:
            tablelist+=','
            clauselist+=' and '
            clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
          fieldlist+=',w%d.location' % tablenumber
          tablelist+='wordlocation w%d' % tablenumber
          clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
          tablenumber+=1
	# Crear la consulta a partir de las partes separadas
    fullquery='select %s from %s where %s' % (fieldlist,tablelist,clauselist)
    print fullquery
    try:
      cur=self.con.execute(fullquery)
      rows=[row for row in cur]
    except sqlite.OperationalError:
      print "Error"
      return None
    return rows,wordids

  def getscoredlist(self,rows,wordids):
    totalscores=dict([(row[0],0) for row in rows])
    # aqui es donde pondrás después las funciones de score
    weights=[]
    #weights=[(1.0,self.frecuencyscore(rows))]
    #weights=[(1.0,self.locationscore(rows))]
	
    for (weight,scores) in weights:
      for url in totalscores:
        totalscores[url]+=weight*scores[url]
    return totalscores

  def geturlname(self,id):
    return self.con.execute(
    "select url from urllist where rowid=%d" % id).fetchone( )[0]

  def query(self,q):
    rows,wordids=self.getmatchrows(q)
    scores=self.getscoredlist(rows,wordids)
    rankedscores=sorted([(score,url) for (url,score)
                         in scores.items( )],reverse=1)
    for (score,urlid) in rankedscores[0:10]:
      print '%f\t%s' % (score,self.geturlname(urlid))

  def normalizescores(self,scores,smallIsBetter=0):
    vsmall=0.00001 # Evita la división por cero errores
    if smallIsBetter:
      minscore=min(scores.values( ))
      return dict([(u,float(minscore)/max(vsmall,l)) for (u,l) \
        in scores.items( )])
    else:
      maxscore=max(scores.values( ))
      if maxscore==0: maxscore=vsmall
      return dict([(u,float(c)/maxscore) for (u,c) in scores.items( )])

  def frequencyscore(self,rows):
    counts=dict([(row[0],0) for row in rows])
    for row in rows: counts[row[0]]+=1
    return self.normalizescores(counts)
	
  def locationscore(self,rows):
    locations=dict([(row[0],1000000) for row in rows])
    for row in rows:
      loc=sum(row[1:])
      if loc<locations[row[0]]: locations[row[0]]=loc
    return self.normalizescores(locations,smallIsBetter=1)
	
  def inboundlinkscore(self,rows):
    uniqueurls=set([row[0] for row in rows])
    inboundcount=dict([(u,self.con.execute( \
      'select count(*) from link where toid=%d' % u).fetchone( )[0]) \
        for u in uniqueurls])
    return self.normalizescores(inboundcount)
	
  def pagerankscore(self,rows):
    pageranks=dict([(row[0],self.con.execute(
	'select score from pagerank where urlid=%d' 
	% row[0]).fetchone( )[0]) for row in rows])
    maxrank=max(pageranks.values( ))
    normalizedscores=dict([(u,float(l)/maxrank) 
	for (u,l) in pageranks.items( )])
    return normalizedscores
	
	
