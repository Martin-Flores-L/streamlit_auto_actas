import pandas as pd
import streamlit as st
from openpyxl import load_workbook
from datetime import datetime
import pytz
import os

#Variable global para los titulos del archivo csv
#EECC = Proveedor
sheets={'Proyecto':'C7', 'OC':'H10', 'EECC':'C8', 'total_OC':'C9', 'total_certificar':'H9', 'termino_obra':'E18' ,'servicio_obra':'E19','posiciones':'H8'}
sheetslist = [key for key in sheets]

#Tiempo
#d1 = today.strftime("%d/%m").replace('/','.')
ts = datetime.now(pytz.timezone('America/Lima')).strftime('%d.%m')
d1 = ts


class Usuario:

    def __init__(self, nombre, csv):
        self.nombre = nombre        
        # self.csv = pd.read_csv("/content/drive/MyDrive/Proyecto_ActasPangea/CSV/{}".format(csv), sep=';',encoding='latin-1')
        self.csv = csv


    def __str__(self):
        return 'Usuario {}'.format(self.nombre)


    def show_csv(self):
        return self.csv.head()
    
    
class Clean(Usuario):

    #Agregar columnas solo str de un solo dato
    def addcolumn(self):
        new_column = input("Ingresa el nombre de tu columna")
        new_value = input("Ingresa los valores")

        self.csv.loc[:,new_column] = str(new_value)


    #Para observar solo los duplicados por columna
    def get_duplicated(self):

         for n in self.csv.duplicated('OC',keep=False):
            if n == True:
                return True
            else:
                return False

    #Mostrar los valores duplicados segun lo que se esta trabajando
    def show_duplicated(self):
        if self.get_duplicated() == True:
            duplicated = pd.concat(g for _, g in self.csv.groupby(self.csv['OC']) if len(g) > 1 )
            return duplicated
        else:
            return 'No hay duplicados'


    #Escoger una columna a trabajar
    def choose_to_work(self, cabecera=[]):
        self.cabecera = [n for n in self.csv]

    # Create a dictionary to map column names to their indices
        column_dict = {n: i for i, n in enumerate(self.cabecera)}

    # Use st.selectbox to let the user choose a column
        column = st.selectbox('Choose a column to work with', options=self.cabecera)

    # Get the index of the chosen column
        title = column_dict[column]
        return title


    #Remover espacios en blanco
    #Muchas veces los espacios en blancos se dan por diferentes datos, limpiarlos es parte
    #del analisis en esta ocasión unos espacios en blanco se conviertieron en -> �
    def no_spaces(self, simbol=''):

        self.simbol = simbol
        x = self.choose_to_work()
        #Dependiendo donde esta el dato, sera left o right strip
        self.csv.iloc[:,x] = self.csv.iloc[:,x].str.lstrip(self.simbol)


    #Cuando los valores numericos mayores a 1000 tengan una coma
    def no_comma(self, title=''):
        #df['colname'] = df['colname'].str.replace(',', '').astype(float)
        #c[c.iloc[:, 0] == 1]
        x = title
        self.csv[self.cabecera[x]] = self.csv[self.cabecera[x]].str.replace(',', '').astype(float)
        

    #Cambiar el titulo para similar los parametros establecidos
    def title_change(self):
    # Use st.selectbox to let the user choose a column
        old_title = st.selectbox('Choose a column to rename', options=self.cabecera)

    # Use st.text_input to let the user enter a new title
        new_title = st.text_input("Enter the new title")

    # Create a confirmation button
        if st.button('Confirm'):
            # Rename the column
            self.csv.rename(columns={old_title: new_title}, inplace=True)
            st.write("Cambio exitoso")
            st.write(self.csv.columns)


    #Convert OC to int    
    def convert_oc_int(self):
        self.csv['OC'] = self.csv['OC'].astype(int)


    #Drop rows by index
    def drop_rows(self, row_1,row_2):
        self.csv.drop(self.csv.index[row_1:row_2], inplace=True)  


    #Show types of data
    def show_types(self):
        return self.csv.dtypes 


    #Moneda a certificar con dos decimales round 2
    def value_rounded_2(self,title=''):
        x = title
        self.csv[self.cabecera[x]] = self.csv[self.cabecera[x]].round(2)


    #Clean the NaN values in column posiciones
    def clean_nan(self):
        self.csv['posiciones'].fillna('0', inplace=True)


    #Replace simbols for letter
    def replace_simbols(self, simbol, letter):
        self.csv.iloc[:,1] = self.csv.iloc[:,1].str.replace(simbol,letter)


    #Remove column from DataFrame
    def remove_columns(self, column_titles=[]):     
        self.csv = self.csv.drop(columns=column_titles)


    def download_excel_files():
        # Specify the directory
        directory = r'C:\Users\kher-\Proyectos\streamlit\Actas'

        # List all the Excel files in the directory
        files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]

        # Create a download button for each file
        for file in files:
            with open(os.path.join(directory, file), 'rb') as f:
                st.download_button(
                    label=f"Download {file}",
                    data=f,
                    file_name=file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
                                

class Printed(Clean):

    # def printed_to_excel(self,certified=''):
    def printed_to_excel(self):

        # self.certified = certified
        text1 = 'ACTA ACEPTACION FINAL'
        text2 = 'ACTA ACEPTACION PARCIAL'
        count = 0
        #Trabajando con los documentos
        workbook = load_workbook(filename=r"plantilla/Plantilla_ActaPangeaco.xlsx") 
        sheet = workbook.active

        for i in range( len(self.csv) ):

            for n in sheetslist:
                sheet[sheets[n]] = self.csv.loc[i,n]

                #Para autoguardar
                if 'OC' == n:
                    a = self.csv.loc[i,n]
                elif 'EECC' == n:
                    b = self.csv.loc[i,n]
                elif 'Proyecto' == n:
                    c = self.csv.loc[i,n]
                #Para comprobar total_OC y total_Certificar
                elif 'total_OC' == n:
                    t_oc = self.csv.loc[i,n]
                elif 'total_certificar' == n:
                    t_oc_c = self.csv.loc[i,n]

            #Conditions to difference Actas Final or Actas Parcial
            if t_oc == t_oc_c:
                #Final
                sheet['D4'] = "ACTA DE ACEPTACIÓN FINAL - PANGEA"
                workbook.save('Actas/{} - {} - {} - {} - {}.xlsx'.format(text1,b,a,c,d1))
            elif t_oc != t_oc_c:
                #Parcial                        
                sheet['D4'] = "ACTA DE ACEPTACIÓN PARCIAL - PANGEA"
                workbook.save('Actas/{} - {} - {} - {} - {}.xlsx'.format(text2,b,a,c,d1))

            count += 1

        return st.write('Se crearon {} archivos en total'.format(count))
            # if certified == 'final':
            #     workbook.save('Actas{}/{} - {} - {} - {} - {}.xlsx'.format(d1,text1,b,a,c,d1))
            # elif certified == 'parcial':
            #     workbook.save('Actas{}/{} - {} - {} - {} - {}.xlsx'.format(d1,text2,b,a,c,d1))    
