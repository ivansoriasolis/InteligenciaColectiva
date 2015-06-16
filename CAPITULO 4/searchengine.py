import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite

# Crea una lista de palabras a ignorar
ignorewords=set(['the','of','to','and','a','in','is','it'])

class crawler:
  # Inicializa el crawler con el nombre de la base de datos
  def __init__(self,dbname):
    pass
  def __del__(self):
    pass
  def dbcommit(self):
    pass
  # Función auxiliar para obtener un ID de entrada y adiciona
  # este si no está presente
  def getentryid(self,table,field,value,createnew=True):
    return None
  # Indexa una página individual
  def addtoindex(self,url,soup):
    print 'Indexing %s' % url
  # Extrae el texto a partir de una pagina HTML (sin etiquetas)
  def gettextonly(self,soup):
    return None
  # Separa las palabras por un caracter que no sea espacio en blanco
  def separatewords(self,text):
    return None
  # Devuelve True si este URL ya esta indexado
  def isindexed(self,url):
    return False
  # Agrega un link entre dos paginas
  def addlinkref(self,urlFrom,urlTo,linkText):
    pass
  # Iniciando con una lista de páginas, hace una busqueda
  # primero en anchura hasta la profundidad dada
  # indexando las paginas que lleguen
  def crawl(self,pages,depth=2):
    pass
  # Crea las tablas de la base de datos
  def createindextables(self):
    pass

  def crawl(self,pages,depth=2):
    for i in range(depth):
      newpages=set( )
      for page in pages:
        try:
          c=urllib2.urlopen(page)
        except:
          print "Could not open %s" % page
          continue
        soup=BeautifulSoup(c.read( ))
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

	
