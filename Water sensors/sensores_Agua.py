import sys
from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication, QVBoxLayout, QDialog, QLabel, QMainWindow)
import os, sys
import json
import datetime
import csv
import pandas as pd
import requests
import telebot
import time
import matplotlib.pyplot as plt
import numpy as np
from os import remove
from os import path

TOKEN = '1484600287:AAGdrHz2gW_spWOgb3PJN-C3_vMvFlMMckk' #Token del bot.
tb = telebot.TeleBot(TOKEN) 

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        #Create widgets
        self.numeroSensor = QLineEdit("Numero de sensor") #Numero de sensor en la interfaz grafica
        self.añoInicio = QLineEdit("Año de Inicio")
        self.mesInicio = QLineEdit("Mes de Inicio")
        self.diaInicio = QLineEdit("Dia de Inicio")
        self.añoFinal = QLineEdit("Año de finalizacion")
        self.mesFinal = QLineEdit("Mes de finalizacion")
        self.diaFinal = QLineEdit("Dia de finalizacion")
        self.umbral = QLineEdit("Umbral de consumo")
        self.button2 = QPushButton("Generación alarma y representacion del consumo")
        self.button3 = QPushButton("Generación de alarma y representacion del consumo con contadores dobles")
        #Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.numeroSensor)
        layout.addWidget(self.añoInicio)
        layout.addWidget(self.mesInicio)
        layout.addWidget(self.diaInicio)
        layout.addWidget(self.añoFinal)
        layout.addWidget(self.mesFinal)
        layout.addWidget(self.diaFinal)
        layout.addWidget(self.umbral)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)       
        #Set dialog layout
        self.setLayout(layout)
        #Add button signal to greetings slot
        self.button2.clicked.connect(self.representacion)
        self.button3.clicked.connect(self.representacion2)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def Numero_Sensores(self):        
        #Recopilacion y asignacion de la informacion recogida por la interfaz
        try:
            #Numero de sensor
            numero = int(self.numeroSensor.text())
            sensor = numero
            #Fechas iniciales
            añoInicio = int(self.añoInicio.text())
            mesInicio = int(self.mesInicio.text())
            diaInicio = int(self.diaInicio.text())
            #Fechas finales
            añoFinal = int(self.añoFinal.text())
            mesFinal = int(self.mesFinal.text())
            diaFinal = int(self.diaFinal.text())
            #Valor de umbral
            umbral_C = int(self.umbral.text())
        except ValueError:
            print("El numero de sensor debe de estar entre 1 y 13." + "\n" + "El formato de fechas debe de introducirse correctamente (con numeros enteros).")
            os._exit(1)
        #Sensores
        sensor1 = "UEXCC_ATE_P00_CUA003_SEN001_AGU"  # #CONTADOR DE AGUA DE ARQUITECTURA TECNICA CONTADOR 1 Y CONTADOR 2 SERVICICIOS COMUNES #Actualizado
        sensor2 = "UEXCC_ATE_P00_LAB023_SEN001_AGU"  #CONTADOR DE AGUA DE ARQUITECTURA TECNICA LABORATORIO 23
        sensor3 = "UEXCC_ATE_P00_LAB018_SEN001_AGU"  #CONTADOR DE AGUA DE ARQUITECTURA TECNICA LABORATORIO 18
        sensor4 = "UEXCC_INF_P00_ASE003_SEN001_AGU"  #CONTADOR DE DE AGUA INFORMATICA ASEO DE MUJERES
        sensor5 = "UEXCC_INF_P00_COM048_SEN003_AGU"  # CONTADOR DE DE AGUA INFORMATICA COMBINACION DE ASEO PB Y P1
        sensor6 = "UEXCC_INF_P00_CUA002_SEN002_AGU"  #CONTADOR DE AGUA, CONTADOR 1 SERVICIOS COMUNES CONTADOR 2 INFORMATICA
        sensor7 = "UEXCC_INV_P00_CUA016_SEN004_AGU"  #CONTADOR DE AGUA TOTAL DE LA EPCC
        sensor8 = "UEXCC_OPU_P00_CUA002_SEN001_AGU"  #CONTADOR DE AGUA, CONTADOR 1 OBRAS PUBLICAS CONTADOR 2 SERVICIOS COMUNES
        sensor9 = "UEXCC_INV_PS1_CUA002_SEN001_AGU"  #CONTADOR DE AGUA DEL EDIFICIO DE INVESTIGACION
        sensor10 = "UEXCC_TEL_P00_CUA027_SEN001_AGU"  #CONTADOR DE AGUA DEL EDIFICIO DE TELECOMUNICACIONES
        sensor11 = "UEXCC_OPU_P00_LAB022_SEN001_AGU"  #CONTADOR DE AGUA DE OBRAS PUBLICAS LABORATORIO 22
        sensor12 = "UEXCC_OPU_P00_LAB016_SEN001_AGU"  #CONTADOR DE AGUA DE OBRAS PUBLICAS LABORATORIO 16
        sensor13 = "UEXCC_SCO_P00_CUA012_SEN001_AGU"  #CONTADOR DE AGUA CAFETERIA
        #Lista auxiliares de sensores.
        lista_Sensores = [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8, sensor9, sensor10, sensor11, sensor12, sensor13]
        numero_Sensores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        #La descargas de los datos se realizara haciendo una llamada a un servicio alojado en Zato. Este servicio nos enlazara con la base de datos en la que estan almacenadas los datos,
        #InfluxDB. El problema que surge para la descarga de datos, es que no es posible descargar todos los datos que ha recogido un sensor de una sola llamada, dado que esto puede
        #provocar que la base de datos colapse y no funcione correctamente. Por ello, se hace necesaria una API que permita la descarga de datos entre las fechas que se solicite, realizando
        #consultas a InfluxDB que nos devuelvan unicamente los datos de consumo relativos a un dia, de forma que se pueda recorrer todos los dias existentes entre las fechas solicitadas.
        def days_between(fechafinal, fechainicio):
            return (fechafinal - fechainicio).days
        #Asignacion de las fechas y el nombre del sensor del que se quieren descargar los datos:
        numeroS = sensor
        numero = numero_Sensores.index(numeroS)
        nameofsensor = lista_Sensores[numero]
        #Fechas de inicio de descarga de datos
        yearstart = añoInicio
        monthstart = mesInicio
        daystart = diaInicio
        hourstart = 0
        #Fechas de final de descarga de datos
        yearfinish = añoFinal
        monthfinish = mesFinal
        dayfinish = diaFinal
        hourfinish = 0
        maximoUmbral = umbral_C
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Conversion de las fechas al formato utilizado. El formato utilizado para poder hacer la llamada al servicio de Zato es el ISO8601
        fechainicio = datetime.datetime(yearstart, monthstart, daystart, hourstart, 00, 00, 000000)
        fechafinal = datetime.datetime(yearfinish, monthfinish, dayfinish, hourfinish, 00, 00, 000000)
        #Desplazamiento de la fecha un numero de dias para poder hacer la busqueda de dia en dia
        fechadesplazada = fechainicio + datetime.timedelta(days=0)  
        #Variable que almacena la diferencia entre la fecha final e inicial, llamando a la funcion previamente definida como days_between
        diasanalizado = (days_between(fechafinal,fechainicio))
        #Ejemplo descarga de datos 
        contador= 0
        ffmod = 0
        content=[]
        if diasanalizado >= 0:
            datossensor = []  #Necesario definir lista previamente dado que si se elige una fecha sin datos al estar sin definir nos da error
            llabarquitectura18 = []  #Lista donde se almacenara toda la coleccion de datos recolectada
            while ffmod != fechafinal:
                fimod = fechainicio + datetime.timedelta(days=contador)  #Esta sera la fechainicial modificada para sacar los datos de un dia
                ffmod = fechainicio + datetime.timedelta(days=contador + 1)
                r = requests.get('http://158.49.112.127:11223/read/influx/json?json={"info": {"api_key": "000000","device": "'+ nameofsensor + '","from":"'+fimod.strftime("%Y-%m-%dT%H:%M:%S")+'", "to":"'+ffmod.strftime("%Y-%m-%dT%H:%M:%S")+'"}}') #url de llamada al servicio
                #print(json.loads(r.content))
                try:
                    content = content+json.loads(r.content)
                    contador += 1
                except:
                    contador+=1
            with open('prueba.json', 'w') as file:
                #print(content)
                json.dump(content, file, indent=4)
        else:
            print("LAS FECHAS DE BUSQUEDA INTRODUCIDAS NO SON CORRECTAS")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Procesamiento exclusivo para sensores con contadores dobles
        if nameofsensor == sensor1 or nameofsensor == sensor8 or nameofsensor == sensor6:
            #Operaciones con fichero json
            f = open('prueba.json', 'r')
            content = f.read()
            jsondecoded = json.loads(content) #Lista jsondecoded
            #Conversion de la informacion
            lista = [] #Lista auxiliar
            listaCreated = []
            dicc_aux = {} #Diccionario
            dicc_created = {}
            for entity in jsondecoded:
                dicc_aux = entity.get('data','')
                for key, value in dicc_aux.items():
                    lista.append(value)
            #Eliminacion de el campo IP de los diferentes sensores
            listaUX=[]
            listaUX2 = []
            for elem in lista:
                try:
                    listaUX.append(float(elem))
                except ValueError:
                    listaUX2.append(elem)
            #Division de listas para representacion grafica
            listaCounter1 = listaUX[::2]
            listaCounter2 = listaUX[1::2]
            #Conversion de la informacion de tiempo de fechas
            for entity in jsondecoded:
                dicc_created = entity.get('created_at', '')
                listaCreated.append(dicc_created)
            #Modificacion para sensores con contadores dobles. Duplicado del tiempo.
            resultado = listaCreated[:]
            for index in range(len(listaCreated)):
                resultado.insert(index * 2, listaCreated[index])
            #Mensajes para Telegram del consumo máximo y mínimo captado por el sensor.
            maximo = max(listaUX)
            tb.send_message('9284473','Consumo maximo en litros captado por el sensor ' + str(nameofsensor) + ' entre los dias ' + str(fechainicio) + ' y ' + str(fechafinal) + ': ' + str(maximo) + ' litros.')
            if maximo == 0:
                tb.send_message('9284473','En esta situacion, el consumo minimo y maximo es el mismo.')
            #Alarma
            for indice, valor_a in enumerate(listaUX):
                if maximoUmbral < listaUX[indice]:
                    tb.send_message('9284473', 'Se ha superado el valor umbral escogido. El valor que ha superado es de ' + str(valor_a) + ' litros ' + ' con fecha exacta: ' + resultado[indice])
                    break
            def devolucion_Listas_SD():
                return(listaCounter1, listaCounter2, resultado, maximoUmbral, listaUX)
            #Parametros de devolucion
            lista_C1 = []
            lista_C2 = []
            lista_Fechas = []
            listaUX_1 = []
            lista_C1, lista_C2, lista_Fechas, numero, lista_UX1 = devolucion_Listas_SD()
            return (lista_C1, lista_C2, lista_Fechas, numero, lista_UX1)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Procesamiento para el resto de sensores    
        else:
            #Operaciones con fichero json.
            f = open('prueba.json', 'r')
            content = f.read()
            jsondecoded = json.loads(content) #Lista jsondecoded
            #Conversion de la informacion
            lista = [] #Lista auxiliar
            listaCreated = []
            dicc_aux = {} #Diccionario
            dicc_created = {}
            for entity in jsondecoded:
                dicc_aux = entity.get('data','')
                for key, value in dicc_aux.items():
                    lista.append(value)
            #Eliminacion de el campo IP de los diferentes sensores
            listaUX=[]
            listaUX2 = []
            for elem in lista:
                try:
                    listaUX.append(float(elem))
                except ValueError:
                    listaUX2.append(elem)
            #Conversion de la informacion de tiempo de fechas
            for entity in jsondecoded:
                dicc_created = entity.get('created_at', '')
                listaCreated.append(dicc_created)
            #Mensajes para Telegram del consumo máximo y mínimo captado por el sensor
            maximo = max(listaUX)
            tb.send_message('9284473','Consumo maximo en litros captado por el sensor ' + str(nameofsensor) + ' entre los dias ' + str(fechainicio) + ' y ' + str(fechafinal) + ': ' + str(maximo) + ' litros.')
            if maximo == 0:
                tb.send_message('9284473','En esta situacion, el consumo minimo y el maximo es el mismo.')
            #Alarma
            for indice, valor_a in enumerate(listaUX):
                if maximoUmbral < listaUX[indice]:
                    tb.send_message('9284473', 'Se ha superado el valor umbral escogido. El valor que ha superado es de ' + str(valor_a) + ' litros ' + ' con fecha exacta: ' + listaCreated[indice])
                    break
            def devolucion_Listas_S1():
                return(listaUX, listaCreated, maximoUmbral)
            #Parametros de devolucion
            listaFechas = []
            listaNueva_Consumo = []
            listaNueva_Consumo, listaFechas, numero = devolucion_Listas_S1()
            return (listaNueva_Consumo, listaFechas, numero)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def representacion(self):
        repre = [] #Lista de Counter de sensores
        repre4 = [] #Lista de fechas de recogida
        repre, repre4, num = self.Numero_Sensores()
        #Envio de archivo
        mi_path_1 = "C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/file_LitrosConsumidos_Agua.txt"
        with open(mi_path_1, 'a+') as j:
            for ind, valor_a in enumerate(repre):
                j.write("Un total de litros consumidos igual a " + str(valor_a) + " con fecha de recogida exacta: " + repre4[ind] + '\n')
            j.close()
        doc_1 = open('C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/file_LitrosConsumidos_Agua.txt', 'rb')
        tb.send_document('9284473', doc_1)
        #Representacion.
        plt.plot(repre)
        plt.title("Consumo de agua")
        plt.xlabel("Muestras")
        plt.ylabel("Litros")
        plt.axhline(num, color = 'r', label = "Umbral")
        plt.legend(loc = "upper left")
        #Envio
        plt.savefig('imagen.png')
        file = open('C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/imagen.png', 'rb')
        tb.send_photo('9284473', file)
        plt.show()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def representacion2(self):
        repre2 = [] #Lista de Counter1 de sensores dobles
        repre3 = [] #Lista de Counter2 de sensores dobles
        repre5 = [] #Lista de fechas de recogida
        repre6 = []
        repre2, repre3, repre5, num, repre6 = self.Numero_Sensores()
        #Envio de archivo
        mi_path_1 = "C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/file_LitrosConsumidos_Agua_SD.txt"
        with open(mi_path_1, 'a+') as j:
            for ind, valor_a in enumerate(repre6):
                j.write("Un total de litros consumidos igual a " + str(valor_a) + " con fecha de recogida exacta: " + repre5[ind] + '\n')
            j.close()
        doc_1 = open('C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/file_LitrosConsumidos_Agua_SD.txt', 'rb')
        tb.send_document('9284473', doc_1)
        #Representacion
        plt.plot(repre2, label = "Counter 1")
        plt.ion
        plt.title("Consumo de agua (Contadores dobles).")
        plt.xlabel("Muestras")
        plt.ylabel("Litros")
        plt.plot(repre3, label = "Counter 2")
        plt.axhline(num, color='r', label = "Umbral")
        plt.legend(loc = "upper left")
        #Envio
        plt.savefig('imagen.png')
        file = open('C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/imagen.png', 'rb')
        tb.send_photo('9284473', file)
        plt.show()
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #Create and show the form
    form = Form()
    form.show()
    #Run the main Qt loop
    sys.exit(app.exec_())  
