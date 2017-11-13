""" Modulo con clases de utilidades web
    Autor:Jesus Navajas 
    Fecha:  2017/10
    *Estas utilidades estan basadas en parte en fuentes del libro BOOK_Web Scraping with Python - Richard Lawson  
"""
import urllib
import urllib2
import urlparse
import json
import httplib
import time
from selenium.webdriver.support.ui import Select

#------------------------------------------------------------------------------------
#UTILIDADES PRIMER EJEMPLO
#------------------------------------------------------------------------------------
class navegador1:
    def __init__(self,host=None,):
        self._host=host
    
    def navegar(self,url2,method="POST",headers={},posdata=None):
        conn = httplib.HTTPSConnection(self._host)
        if posdata:
            midata2 = urllib.urlencode(posdata)
            headers["Content-Length"]=str(len(midata2))
        else:
            midata=None
        #headers = {"Content-type": "application/x-www-form-urlencoded"}
        conn.request(method, url2, midata2, headers)
        response = conn.getresponse()
        midata = response.read()
        conn.close()
        return midata

#------------------------------------------------------------------------------------
#LIBRERIA AVANZADA
#------------------------------------------------------------------------------------
_timesleep=0.5

#-----------------------------LOCALIZADOR-----------------------------------

class localizador:
    #Metodos a implementar
    def localizaInterna(self):
        raise NotImplementedError
    
    #Metodos publicos
    def __init__(self,navegador,maxespera=3):
        self._nav=navegador
        self._maxespera=maxespera
    
    def localiza(self):
        i=0
        aux=None
        try:
            aux=self.localizaInterna()
        except:
            pass
        while ((aux is None) and (i<self._maxespera) ):
            time.sleep(_timesleep)
            i+=1
            try:
                aux=self.localizaInterna()
            except:
                pass
        
        return aux

class localizadorID(localizador):
    #Metodos a implementar
    def localizaInterna(self):
        return self._nav.find_element_by_id(self._ID)
    
    #Metodos publicos
    def __init__(self,navegador,ID,maxespera=1):
        localizador.__init__(self,navegador,maxespera)
        self._ID=ID
        
class localizadorCSS(localizador):
    #Metodos a implementar
    def localizaInterna(self):
        return self._nav.find_elements_by_css_selector(self._ID)
    
    #Metodos publicos
    def __init__(self,navegador,ID,maxespera=1):
        localizador.__init__(self,navegador,maxespera)
        self._ID=ID


#-----------------------------ACCION-----------------------------------

class accion:
    #Metodos a implementar
    def ejecutarInterna(self):
        raise NotImplementedError
    
    #Metodos publicos
    def __init__(self,navegador,espera=True):
        self._nav=navegador
        self._espera=espera

    def ejecutar(self):
        self.ejecutarInterna()
        if self._espera:
            time.sleep(_timesleep)

class accionLoc(accion):
    def __init__(self,navegador,loc,espera=True):
        accion.__init__(self,navegador,espera)
        self._loc=loc

class accionNavegar(accion):
    def __init__(self,navegador,url):
        accion.__init__(self,navegador,True)
        self._url=url
    def ejecutarInterna(self):
        self._nav.get(self._url)
    
       
class accionClick(accionLoc):
    def ejecutarInterna(self):
        self._loc.localiza().click()
        

class accionMultiple(accion):
    def __init__(self,navegador,acciones,espera=True):
        accion.__init__(self,navegador,espera)
        self._acciones=acciones
    
    def ejecutarInterna(self):
        for acc in self._acciones:
            acc.ejecutarInterna()
    

#-----------------------------ACCION ITERADOR-----------------------------------

class excepcionFinSinVolver(Exception):
    pass

class excepcionVolverSinFin(Exception):
    pass

class accionJerarquica(accion):
   

    def __init__(self,navegador,accionHija,accPrimera,espera=True):
        accion.__init__(self,navegador,espera)
        self._accionHija=accionHija
        self._accionPrimera=accPrimera
        

class estado():
    def __init__(self):
        self._estado=""

    def setEstado(self,estado):
        self._estado=estado
    
    def getEstado(self):
        return self._estado
    


class accionIteradorSelect(accionJerarquica):
    def __init__(self,navegador,accionHija,loc,miestado,accPrimera=None):
        accionJerarquica.__init__(self,navegador,accionHija,accPrimera)
        self._loc=loc
        self._estado=miestado
        self._limitesup=10000
        self._limiteinf=0
    
    def limitar(self,limiteinf=0,limitesup=10000):
        self._limitesup=limitesup
        self._limiteinf=limiteinf

    def ejecutarInterna(self):
        
        if self._accionPrimera:
            self._accionPrimera.ejecutar()

        miselect=Select(self._loc.localiza())
        opciones =miselect.options[self._limiteinf:self._limitesup]
        #Avanzar sihay estado
        opcion=opciones[0]
        if self._estado.getEstado()!="":
            while (opcion.text!=self._estado.getEstado()):
                opcion=self._avanzaSeguro(opciones)

        #Ejecutar todas las demas    
        while opcion:
            #miselect.select_by_value('BARCELONA')
            opcion.click()
            self._estado.setEstado(opcion.text)
            try:
                next_text=self._textSigSeguro(opciones)
                self._accionHija.ejecutar()
                opcion=self._avanzaSeguro(opciones)
            except excepcionFinSinVolver:
                opcion=self._avanzaSeguro(opciones)
                if opcion:
                    self._estado.setEstado(next_text)
                    if self._accionPrimera:
                        self.ejecutarInterna()
                        return
                    else:
                        raise excepcionVolverSinFin()
                else:
                    self._estado.setEstado("")
                    if self._accionPrimera:
                        return
                    else:
                        raise 
            except  excepcionVolverSinFin:
                if self._accionPrimera:
                    self.ejecutarInterna()
                    return
                else:
                    raise

        #Borrarestado
        self._estado.setEstado("")

    def _avanzaSeguro(self,opciones):
        del opciones[0]
        if len(opciones)>0:
            return opciones[0]
        else:
            return None
    
    def _textSigSeguro(self,opciones):
        if len(opciones)>1:
            return opciones[1].text
        else:
            return None
    
    
