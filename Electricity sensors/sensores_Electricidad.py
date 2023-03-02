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
        self.button2 = QPushButton("Representacion y envio de la energia consumida")
        #Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.numeroSensor)
        layout.addWidget(self.añoInicio)
        layout.addWidget(self.mesInicio)
        layout.addWidget(self.diaInicio)
        layout.addWidget(self.añoFinal)
        layout.addWidget(self.mesFinal)
        layout.addWidget(self.diaFinal)
        layout.addWidget(self.button2)
        #Set dialog layout
        self.setLayout(layout)
        #Add button signal to greetings slot
        self.button2.clicked.connect(self.representacion)
#-------------------------------------------------------------------------------------------
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
        except ValueError:
            print("El numero de sensor debe de ser 11." + "\n" + "El formato de fechas debe de introducirse correctamente (con numeros enteros).")
            os._exit(1)
        #Sensores
        sensor11 = "UEXCC_TEL_PS1_CUA002_SEN001_INV" #Sensor electricidad
        #Lista de sensores de ayuda.
        lista_Sensores = [sensor11]
        numero_Sensores = [11]    
        def days_between(fechafinal, fechainicio):
            return (fechafinal - fechainicio).days #explicacion de .days: https://stackoverflow.com/questions/8258432/days-between-two-dates
        #Asignacion de las fechas
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
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Conversion de las fechas al formato utilizado. El formato utilizado para poder hacer la llamada al servicio de Zato es el ISO8601.
        fechainicio = datetime.datetime(yearstart, monthstart, daystart, hourstart, 00, 00, 000000) #explicacion datetime: https://python-para-impacientes.blogspot.com/2014/02/operaciones-con-fechas-y-horas.html
        fechafinal = datetime.datetime(yearfinish, monthfinish, dayfinish, hourfinish, 00, 00, 000000)
        fechadesplazada = fechainicio + datetime.timedelta(days=0)  #explicacion timedelta https://docs.python.org/2/library/datetime.html. 
        diasanalizado = (days_between(fechafinal,fechainicio))  #Variable que almacena la diferencia entre la fecha final e inicial, llamando a la funcion previamente definida como days_between
        #Descarga de datos.
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
                print(content)
                json.dump(content, file, indent=4)
        else:
            print("LAS FECHAS DE BUSQUEDA INTRODUCIDAS NO SON CORRECTAS")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if nameofsensor == sensor11:
            #Operaciones con fichero json.
            f = open('prueba.json', 'r')
            content = f.read()
            jsondecoded = json.loads(content)
            #Conversion de la informacion.
            lista = []
            listaCreated = []
            dicc_aux={}
            dicc_created={}
            for entity in jsondecoded:
                dicc_aux = entity.get('data','')
                for key, value in dicc_aux.items():
                    lista.append(value)
            new_list = lista[::9]
            maximoValor = max(new_list)
            for entity in jsondecoded:
                dicc_created = entity.get('created_at', '')
                listaCreated.append(dicc_created)
            tb.send_message('9284473','Energia consumida en Wh maximo captado por el sensor ' + str(nameofsensor) + ' entre los dias ' + str(fechainicio) + ' y ' + str(fechafinal) + ' es: ' + str(maximoValor))
            if maximoValor == 0:
                tb.send_message('9284473','En esta situacion, la energia consumida minima y maxima es la misma.')    
            def devolucion_listas():
                return (new_list, listaCreated)
            #Parametros de devolución.
            listaC1 = []
            listaFechas = []
            listaC1, listaFechas = devolucion_listas()
            return (listaC1, listaFechas)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def representacion(self):
        repre = []
        repre4 = []
        repre, repre4 = self.Numero_Sensores() 
        #Envio de archivo
        mi_path_1 = "C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/file_EnergiaConsumida_Electricidad.txt"
        with open(mi_path_1, 'a+') as j:
            for ind, valor_a in enumerate(repre):
                j.write("Energia consumida en Wh es " + str(valor_a) + " con fecha de recogida exacta: " + repre4[ind] + '\n')
            j.close()
        doc_1 = open('C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/file_EnergiaConsumida_Electricidad.txt')
        tb.send_document('9284473', doc_1)
        #Representacion
        plt.plot(repre)
        plt.title("Energia Consumida")
        plt.xlabel("Muestras")
        plt.ylabel("Wh")
        #Envio
        plt.savefig('imagen_ConsumoElectricidad.png')
        file = open('C:/Users/adrit/AppData/Local/Programs/Python/Python37/Scripts/Ingenieria_Servicios_TIC/imagen_ConsumoElectricidad.png', 'rb')
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

