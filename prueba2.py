""" PRUEBA CONCEPTO OBTENER CIGNA SALUD - NAVEGACION NWEB
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import UtilWeb
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium
#import csv
import unicodecsv as csv
from sets import Set
import re
import argparse
import datetime


class midict(dict):
    def __setitem__(self,key, value):
        value1=value.strip()
        value2=value1.replace("\t"," ")
        value2=value2.replace("\n"," ")
        value2=re.sub("[\s+]"," ",value2)
        dict.__setitem__(self,key,value2)

print('Prueba1\n')

class tratarListadoAccion(UtilWeb.accion):

    def __init__(self,navegador,estados,elementos,claves):
        UtilWeb.accion.__init__(self,navegador)
        self._elementos=elementos
        self._keys=claves
        self._estados=estados

    def procesaIndividual(self,elem):
        valores=midict()
        hijos=elem.find_elements_by_css_selector("DIV")
        for hijo in hijos:
            clase=hijo.get_attribute("class")
            if clase=="Pack01":
                valores["NOMBRETOT"]=hijo.get_property('innerText')
                try:
                    hijos2=hijo.find_elements_by_css_selector("A")
                    z=1
                    for hijo2 in hijos2:
                        valores["NOMBRE"+str(z)]=hijo.get_property('innerText')
                        z+=1
                except:
                    pass
            elif clase=="Pack02":
                saux=hijo.get_property('innerText')
                valores["DIR_COMPLETA"]=saux
                try:
                    saux1=saux.split(',')
                    valores["DIR_CALLE"]=",".join(saux1[0:(len(saux1)-1)])
                    saux2=saux1[len(saux1)-1].split('-')
                    valores["DIR_CP"]=saux2[0]
                    valores["DIR_LOCALIDAD"]=saux2[1]
                    valores["DIR_PROVINCIA"]=saux2[2]
                except:
                    pass
                    
            elif clase=="Pack03":
                for hijo2 in hijo.find_elements_by_css_selector("LI"):
                    try:
                        saux=hijo2.get_property('innerText').split(':')
                        valores["AUX_"+saux[0]]=saux[1]
                    except:
                        pass
            else:
                pass
                #valores["OTROS"]=hijo.text
        return valores
    
    def ejecutarInterna(self):
        #CLICK
        boton=self._nav.find_element_by_id('directorio-medico-page-form-1')
        boton.click()
        ##ELEMENTOS DEL LISTADO
        elementos=self._nav.find_elements_by_css_selector("li[class^='liresults'] ")
        j=0
        for elem in elementos:
            aux=self.procesaIndividual(elem)
            i=1
            aux['TIEMPO']= datetime.datetime.now().isoformat() 
            for estado in self._estados:
                aux["ESTADO_"+str(i)]=estado.getEstado()
                i+=1
            self._elementos.append(aux)
            self._keys.update(aux.keys())
            # j+=1
            # if j==5:
            #     break
        raise UtilWeb.excepcionFinSinVolver()

class accionInicial(UtilWeb.accion):
    def ejecutarInterna(self):
        self._nav.get('http://www.cignasalud.es/directorio_medico/es')
        selCliente=Select(self._nav.find_element_by_id('select-client'))
        selCliente.select_by_value('2')
    

def main():
    
    print 'INICIO : '+ datetime.datetime.now().isoformat()
    #totales
    elementos=[]
    claves=Set()
    #Tratamiento parametros en linea ---------------------------------------------
    parser = argparse.ArgumentParser(description='Descarga cuadro medico')
    parser.add_argument('ficheroSalida',nargs='?',
                        default='output.csv',
                    help='nombre fihero salida')
    parser.add_argument('prI',nargs='?',
                    type=int, default=1,
                    help='provincia inicio 1... (default: 1)')

    parser.add_argument('prF', nargs='?',
                    type=int, default=100,
                    help='provincia fin ... (default: 100)')

    
    args = parser.parse_args()
    print "SALIDA"+ args.ficheroSalida
    print "PROVINCIAS ["+ str(args.prI)+".."+str(args.prF)+"]"

    
    #Creación de clases estados, localizadores y acciones de navegacion--------------------------- 
    #Creamos estados
    estadoEsp=UtilWeb.estado()
    estadoProv=UtilWeb.estado()
    #Creamos objetos de navegacion

    nav = webdriver.Chrome("C:\\desa\\chromedriver.exe")
    
    accionNav=accionInicial(nav)
    accionElemetos=tratarListadoAccion(nav,[estadoProv,estadoEsp],elementos,claves)

    locProvincia=UtilWeb.localizadorID(nav,'edit-provincia--2')
    locEspecialidad=UtilWeb.localizadorID(nav,'edit-especialidad-2')

    accionIterEspecialidad=UtilWeb.accionIteradorSelect(nav,accionElemetos,locEspecialidad,estadoEsp)

    accionIterProvincia=UtilWeb.accionIteradorSelect(nav,accionIterEspecialidad,locProvincia,estadoProv,accionNav)
    
    
    accionIterProvincia.limitar(args.prI,args.prF)
    accionIterEspecialidad.limitar(1)
    
    #bucle de peticiones --------------------------- 

    ierrores=0
    bError=True
    while(bError):
        try:
            bError=False
            accionIterProvincia.ejecutar()
        except :
            print 'ERROR[' +estadoProv.getEstado() + ',' + estadoEsp.getEstado() + '] : '+ datetime.datetime.now().isoformat()
            ierrores+=1
            
            #REINICIAR
            try:
                nav.close()
            except:
                    pass
            
            nav = webdriver.Chrome("C:\\desa\\chromedriver.exe")
            accionNav=accionInicial(nav)
            accionElemetos=tratarListadoAccion(nav,[estadoProv,estadoEsp],elementos,claves)

            locProvincia=UtilWeb.localizadorID(nav,'edit-provincia--2')
            locEspecialidad=UtilWeb.localizadorID(nav,'edit-especialidad-2')
            accionIterEspecialidad=UtilWeb.accionIteradorSelect(nav,accionElemetos,locEspecialidad,estadoEsp)
            accionIterProvincia=UtilWeb.accionIteradorSelect(nav,accionIterEspecialidad,locProvincia,estadoProv,accionNav)
            accionIterProvincia.saltarPrimero()
            accionIterEspecialidad.saltarPrimero()
            accionIterProvincia.limitar(args.prI,args.prF)
            accionIterEspecialidad.limitar(1)
            #CONTROL ERRORES FINAL
            if ierrores<500:
                bError=True
            
    print 'FIN NAVEGACION : '+ datetime.datetime.now().isoformat() 

    #Escritura a fichero --------------------------- 
    if not(bError):
        print 'ESCRITURA FICHERO'
        toCSV=elementos
        keys = list(claves)
        with open(args.ficheroSalida, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(toCSV) 
    
    print 'FIN : '+ datetime.datetime.now().isoformat()

    nav.close()


main()
