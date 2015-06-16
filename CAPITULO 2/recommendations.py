# -*- coding: cp1252 -*-

# un diccionario de criticas de cine y sus puntajes
# de un pequeno conjunto de peliculas
critics={
        'Lisa Rose': {
            'Lady in the Water': 2.5,
            'Snakes on a Plane': 3.5,
            'Just My Luck': 3.0,
            'Superman Returns': 3.5,
            'You, Me and Dupree': 2.5,
            'The Night Listener': 3.0
            },
        'Gene Seymour': {
            'Lady in the Water': 3.0,
            'Snakes on a Plane': 3.5,
            'Just My Luck': 1.5,
            'Superman Returns': 5.0,
            'The Night Listener': 3.0,
            'You, Me and Dupree': 3.5
            },
        'Michael Phillips': {
            'Lady in the Water': 2.5,
            'Snakes on a Plane': 3.0,
            'Superman Returns': 3.5,
            'The Night Listener': 4.0
            },
        'Claudia Puig': {
            'Snakes on a Plane': 3.5,
            'Just My Luck': 3.0,
            'The Night Listener': 4.5,
            'Superman Returns': 4.0,
            'You, Me and Dupree': 2.5
            },
        'Mick LaSalle': {
            'Lady in the Water': 3.0,
            'Snakes on a Plane': 4.0,
            'Just My Luck': 2.0,
            'Superman Returns': 3.0,
            'The Night Listener': 3.0,
            'You, Me and Dupree': 2.0
            },
        'Jack Matthews': {
            'Lady in the Water': 3.0,
            'Snakes on a Plane': 4.0,
            'The Night Listener': 3.0,
            'Superman Returns': 5.0,
            'You, Me and Dupree': 3.5
            },
        'Toby': {
            'Snakes on a Plane':4.5,
            'You, Me and Dupree':1.0,
            'Superman Returns':4.0
            }
        }

from math import sqrt

# Retorna un puntaje de similardiad basado en distancia
# para persona1 y persona2
def sim_distance(prefs,person1,person2):
    # Obtiene la lista de los items similares
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
           si[item]=1
    # si no tienen cosas en comun retorna 0
    if len(si)==0: return 0
    # susma los cuadrados de las diferencias
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                        for item in prefs[person1]
                        if item in prefs[person2]])
    if sum_of_squares == 0: return 1
    return 1.0/(sqrt(sum_of_squares))

def sim_tanimoto(prefs, person1, person2):
    # Obtiene la lista de los items similares
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
           si[item]=1
    # si no tienen cosas en comun retorna 0
    if len(si)==0: return 0
    tani = float(len(si))/(len(prefs[person1])+len(prefs[person2])-len(si))
    if tani == 0: return 1
    return tani

# Devuelve el coeficiente de correlacion de Pearson
def sim_pearson(prefs,p1,p2):
    # Obtiene la lista de items en comun
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item]=1
    # Encontrar el numero de elementos
    n=len(si)
    # Si no hay items en comun retorna 0
    if n==0: return 0
    # Suma todas las preferencias de cada persona
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])
    # Suma de los cuadrados
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
    # Suma de los productos
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
    # Calcula el coeficiente de pearson
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0
    r=num/den
    return r

def sim_pearson2(prefs, p1, p2):
    # Obtiene la lista de items en comun
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
    # Encontrar el numero de elementos
    n=float(len(si)) #float es necesario para que la division sea real
    # Si no hay items en comun retorna 0
    if n==0: return 0
    mediaP1 = sum([prefs[p1][it] for it in si])/n
    mediaP2 = sum([prefs[p2][it] for it in si])/n
    devP1 = sqrt(sum([pow(prefs[p1][it]-mediaP1,2) for it in si])/(n-1))
    devP2 = sqrt(sum([pow(prefs[p2][it]-mediaP2,2) for it in si])/(n-1))
    covP1P2 = sum([(prefs[p1][it]-mediaP1)*(prefs[p2][it]-mediaP2)
                   for it in si])/(n-1)
    r = covP1P2/(devP1*devP2)
    return r

# Devuelve el mejor par para una persona desde el diccionario
# Numero de resultados y funcion de similaridad son parametros opcionales
def topMatches(prefs,person,n=5,similarity=sim_pearson):
    scores=[(similarity(prefs,person,other),other)
            for other in prefs if other!=person]
    # Ordena la lista de forma que el puntaje mas alto aparece primero
    scores.sort( )
    scores.reverse( )
    return scores[0:n]

# Obteniendo recomendaciones para una persona usando un promedio 
# con pesos de cada un de los rankings de los usuarios
def getRecommendations(prefs,person,n=5,similarity=sim_pearson):
    totals={}
    simSums={}
    mejores = [item[1]
               for item in topMatches(prefs,person,n,similarity)]
    for other in mejores:
        # evita que me compare a mi mismo
        if other==person: continue
        sim=similarity(prefs,person,other)
        # ignora puntajes menores que cero
        if sim<=0: continue
        for item in prefs[other]:
            # solamente putua películas que no he visto
            if item not in prefs[person] or prefs[person][item]==0:
                # Similitud * Score
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                # Sum de similitudes
                simSums.setdefault(item,0)
                simSums[item]+=sim
    # Crea la lista normalizada
    rankings=[(total/simSums[item],item)
              for item,total in totals.items( )]
    # Retorna la lista ordenada
    rankings.sort( )
    rankings.reverse( )
    return rankings

# Invierte el diccionario de forma que los items tendrán ahora una
# lista de criticos
def transformPrefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            # Intercambia items y personas
            result[item][person]=prefs[person][item]
    return result

#construye el conjunto de datos para items similares
def calculateSimilarItems(prefs,n=10):
    # Crea un diccionario de itemas mostrando que otros items 
    # son similares a ellos
    result={}
    # Invirte la matriz de preferencias para que se centre en los items
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        # Actualizaciones de estado para grandes conjuntos de datos
        c+=1
        if c%100==0: print "%d / %d" % (c,len(itemPrefs))
        # Encuentra los items mas similares a uno
        scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
        result[item]=scores
    return result

def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}
    # Itera sobre los itemas calificados por el usuario
    for (item,rating) in userRatings.items( ):
        # Itera sobre los items similares a estos
        for (similarity,item2) in itemMatch[item]:
            # Ignorar si el usuario ha calificado ya este item
            if item2 in userRatings: continue
            # Suma ponderada de calificaciones de similitud
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating
            # Suma de todas las similitudes
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity
    # Divide cada puntaje total por el total ponderado
    rankings=[(score/totalSim[item],item)
              for item,score in scores.items( )]
    # Devuelve el ranking del más alto al más bajo
    rankings.sort( )
    rankings.reverse( )
    return rankings

def loadMovieLens(path='./data/movielens'):
    # Obteniendo los titulos de las peliculas
    movies={}
    for line in open(path+'/u.item'):
        (id,title)=line.split('|')[0:2]
        movies[id]=title
    # cargando los datos
    prefs={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts)=line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]]=float(rating)
    return prefs
