""" PRUEBA CONCEPTO OBTENER AEGON - PETICIONJSON
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import sys
import urllib
import urllib2
import urlparse
import json
import httplib
import UtilWeb
from sets import Set
import unicodecsv as csv
from selenium.webdriver.support.ui import Select
from selenium import webdriver
import datetime
import argparse

#PROCESO DE LISTA
def _procesaElem2(elem,resul,prefijo):
    if type(elem) is dict:
        for a in elem.keys():
            if prefijo=="":
                aux=str(a)
            else:
                aux=prefijo + "_" + str(a)
            _procesaElem2(elem[a],resul,aux )

    elif type(elem) is str:
        resul[prefijo]=elem
    else:
        resul[prefijo]=str(elem)

def procesaElem(vocal,espe,elem,claves):
    """Procesa elementoindividual reduciendolo a diccionario simple"""
    resul={}
    resul['ESTADO1']=espe
    resul['ESTADO2']=vocal
    _procesaElem2(elem,resul,'')
    claves.update(resul.keys())
    return resul


#CARGA ESPECIALIDADES
def listaEspecialidades():
    nav = webdriver.Chrome("C:\\desa\\chromedriver.exe")
    lista=[]
    nav.get('https://www.aegon.es/cuadro-medico')
    aux1=nav.find_element_by_id('searchTerms')
    aux1.send_keys('u')
    aux1.submit()
    #aux2=nav.find_element_by_css_selector("SPAN[class='icomoon-lupa']")
    #aux2.click()
    selEspe=Select(nav.find_element_by_id('especialidad'))
    for option in selEspe.options:
        lista.append(option.get_attribute('value'))
    nav.close()
    del lista[0]
    return lista

def main():
    print 'INICIO : '+ datetime.datetime.now().isoformat()

    #PARAMETROD----------------------------------------------------------
   
    parser = argparse.ArgumentParser(description='Descarga cuadro medico')
    parser.add_argument('ficheroSalida',nargs='?',
                        default='e:\\output.csv',
                    help='nombre fihero salida')
    args = parser.parse_args()
    print "SALIDA"+ args.ficheroSalida
   
    #VALORES INICIALES----------------------------------------------------------
    headers={}
    params={}
    url='https://www.aegon.es/cuadro-medico?p_p_id=aegonmedicalsearch_WAR_aegonmedicalsearchportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1'
    host='www.aegon.es'
    url2='/cuadro-medico?p_p_id=aegonmedicalsearch_WAR_aegonmedicalsearchportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1'
    
    url2="/cuadro-medico?p_p_id=aegonmedicalsearch_WAR_aegonmedicalsearchportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1"
    headers["Accept"]="application/json, text/javascript, */*; q=0.01"
    headers["Accept-Encoding"]= "gzip, deflate, br"
    headers["Accept-Language"]= "es,en-US;q=0.8,en;q=0.6"
    headers["Content-Type"]= "application/x-www-form-urlencoded; charset=UTF-8"
    headers["Host"]= "www.aegon.es"
    headers["Origin"]= "https://www.aegon.es"
    headers["Referer"]= "https://www.aegon.es/cuadro-medico?p_auth=WSPsCI8E&p_p_id=aegonmedicalsearch_WAR_aegonmedicalsearchportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_javax.portlet.action=actionEnlaceMedicalSearch"
    headers["User-Agent"]= "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    headers["X-Requested-With"]= "XMLHttpRequest"
    headers["Connection"]= "keep-alive"
    params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_action"]= "search"    
    params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_searchTerms"]= "gar"
    params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_latitude"]= ""
    params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_longitude"]= ""
    params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_increase"]= "true"
    params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_poblacion"]= ""
    params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_especialidad"] = ""           
    #params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_searchTerms"] = busq
    params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_pageIndex"] = "0"
    
    #ElementosIteracion
    listaVocales=['a','e','i','o','u']
    #listaVocales=['u']
    max_pag=20
    listaEspe=['']
    #listaEspe=listaEspecialidades()
    resul={}
    
    
    #BUCLE----------------------------------------------------------
    for espe in listaEspe:
        params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_especialidad"] = espe
        if not resul.has_key(espe):
            resul[espe]={}
        for vocal in listaVocales:
            if not resul[espe].has_key(vocal):
                resul[espe][vocal]=[]
        
            params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_searchTerms"] = vocal
            nav=UtilWeb.navegador1(host)
            for pag in range(0, max_pag):
                params["_aegonmedicalsearch_WAR_aegonmedicalsearchportlet_pageIndex"]= str(pag * 100)
                bError=True
                ierrores=0
                while(bError and ierrores<5):
                    try:
                        print 'LANZADO ESPECIALIDAD:[' + espe + ']  VOCAL:[' + vocal +']  PAG:[' + str(pag) +']' + datetime.datetime.now().isoformat()
                        midata = nav.navegar(url2,headers=headers,posdata=params)
                        aux2=json.loads(midata)
                        resul[espe][vocal].extend(aux2['RES']['R'])
                        bError=False
                        print 'PROCESADA ESPECIALIDAD:[' + espe + ']  VOCAL:[' + vocal +']  PAG:[' + str(pag) +']'  + datetime.datetime.now().isoformat()
                    except:
                        print 'ERROR ESPECIALIDAD:[' + espe + ']  VOCAL:[' + vocal +']  PAG:[' + str(pag) +']' + datetime.datetime.now().isoformat()
                        ierrores+=1
                if bError:
                    break

    #ESCRITURA SALIDA----------------------------------------------------------
    listaFinal=[]
    claves=Set()
    for espe in listaEspe:
        for vocal in listaVocales:
            for elem in resul[espe][vocal]:
                listaFinal.append(procesaElem(vocal,espe,elem,claves))
    print 'ESCRITURA FICHERO'
    toCSV=listaFinal
    keys = list(claves)
    with open(args.ficheroSalida, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV) 
                 
    print 'FIN : '+ datetime.datetime.now().isoformat()


main()
