import pandas as pd
import streamlit as st
from openpyxl import load_workbook
from datetime import datetime
import pytz
import os
import zipfile
import sqlite3

#Global variables
#EECC = Proveedor
sheets={'Proyecto':'C7', 'OC':'H10', 'EECC':'C8', 'total_OC':'C9', 'total_certificar':'H9', 'termino_obra':'E18' ,'servicio_obra':'E19','posiciones':'H8'}
sheetslist = [key for key in sheets]

#Time
#d1 = today.strftime("%d/%m").replace('/','.')
ts = datetime.now(pytz.timezone('America/Lima')).strftime('%d.%m')



#Class
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
    def choose_to_work(self):
    # Get the index of the chosen column
        columns_to_remove = st.multiselect('Choose columns', options=self.csv.columns.tolist())
        return columns_to_remove


    #Remover espacios en blanco
    #Muchas veces los espacios en blancos se dan por diferentes datos, limpiarlos es parte
    #del analisis en esta ocasión unos espacios en blanco se conviertieron en -> �
    def no_spaces(self, simbol=''):

        self.simbol = simbol
        x = self.choose_to_work()
        #Dependiendo donde esta el dato, sera left o right strip
        self.csv.iloc[:,x] = self.csv.iloc[:,x].str.lstrip(self.simbol)


    #Cuando los valores numericos mayores a 1000 tengan una coma
    def no_comma(self, columns): 
        for column in columns:
            st.session_state.csv[column] = st.session_state.csv[column].str.replace(',', '').astype(float)
        

    #Cambiar el titulo para similar los parametros establecidos
    
                
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
    def value_rounded_2(self, columns):
        for column in columns:
            self.csv[column] = self.csv[column].round(2)
        


    #Clean the NaN values in column posiciones
    def clean_nan(self):
        self.csv['posiciones'].fillna('0', inplace=True)


    #Replace simbols for letter
    def replace_simbols(self, simbol, letter):
        self.csv.iloc[:,1] = self.csv.iloc[:,1].str.replace(simbol,letter)


    #Remove column from DataFrame
    def remove_columns(self, columns): 
        st.session_state.csv = st.session_state.csv.drop(columns, axis=1)


    def download_excel_files(self):
        # Specify the directory
        directory = r'Actas/'

        # List all the Excel files in the directory
        files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]

        # Create a zip file
        with zipfile.ZipFile('excel_files.zip', 'w') as zipf:
            # Add each Excel file to the zip file
            for file in files:
                zipf.write(os.path.join(directory, file), arcname=file)

        # Create a download button for the zip file
        with open('excel_files.zip', 'rb') as f:
            data = f.read()

        def delete_files(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

        st.download_button(
            label="Download zip file",
            data=data,
            file_name="excel_files.zip",
            mime="application/zip"
        )

        delete_files(directory)


    #Save in sqlite                                  
    def save_sqlite(self):
        conn = st.connection('actas_database.db', type='sql')

        #Create table
        conn.execute('CREATE TABLE IF NOT EXISTS actas (Proyecto TEXT, OC INTEGER, EECC TEXT, total_OC REAL, total_certificar REAL, termino_obra DATE, servicio_obra DATE, posiciones INTEGER);' )
                      
        self.csv.to_sql('actas_database', conn, if_exists='append', index=False)

        conn.close()


    #Show sqlite
    def show_sqlite(self):
        conn = st.connection('actas_database.db')
        query = "SELECT * FROM actas"
        df = pd.read_sql(query, conn)
        st.write(df)
        conn.close()        


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
                workbook.save('Actas/{} - {} - {} - {} - {}.xlsx'.format(text1,b,a,c,ts))
            elif t_oc != t_oc_c:
                #Parcial                        
                sheet['D4'] = "ACTA DE ACEPTACIÓN PARCIAL - PANGEA"
                workbook.save('Actas/{} - {} - {} - {} - {}.xlsx'.format(text2,b,a,c,ts))

            count += 1

        return st.write('Se crearon {} archivos en total'.format(count))
            # if certified == 'final':
            #     workbook.save('Actas{}/{} - {} - {} - {} - {}.xlsx'.format(d1,text1,b,a,c,d1))
            # elif certified == 'parcial':
            #     workbook.save('Actas{}/{} - {} - {} - {} - {}.xlsx'.format(d1,text2,b,a,c,d1))    
