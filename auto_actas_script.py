
import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from class_actas import Printed
from st_aggrid import GridOptionsBuilder, AgGrid

#Set the page layout to wide
st.set_page_config(layout="wide", initial_sidebar_state="auto")

# Tittle
st.title('Automatic Actas Pangea')

# UPLOAD FILE
uploaded_file = st.file_uploader("Sube tu archivo")


if uploaded_file is not None:

    #Clear cache
    st.cache_data.clear()
    st.session_state.clear()

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file, sep=';',encoding='latin-1')

    #Streamlit_grid config
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_default_column(editable=True)
    gb.configure_column('total_OC', type=['numericColumn','numberColumnFilter','customNumericFormat'], precision=2, valueFormatter="data.total_OC.toLocaleString('en-US');")
    gb.configure_column('total_certificar', type=['numericColumn','numberColumnFilter','customNumericFormat'], precision=2, valueFormatter="data.total_certificar.toLocaleString('en-US');")
    gb.configure_grid_options(
    groupDefaultExpanded=-1,
    suppressColumnVirtualisation=False,
    groupDisplayType="groupRows",
    autoGroupColumnDef=dict(
        minWidth=250,
        pinned="left",
        cellRendererParams=dict(suppressCount=True),
    ),
)

    vgo = gb.build()


    #Star connecto to my class Usuario
    user = Printed('Usuario', dataframe)

    #Variable global para los titulos del archivo csv
    if 'csv' not in st.session_state:
        st.session_state.csv = user.csv

    # Create a sidebar for actions
    st.sidebar.title("Actions")
    action = st.sidebar.selectbox("Choose an action", ["Show dataframe", "Clean dataframe", "Print dataframe", "Show data"])


    #Show dataframe
    if action == "Show dataframe":
        AgGrid(st.session_state.csv, gridOptions=vgo, height=550, columns_auto_size_mode=True,fit_columns_on_grid_load=True,enable_sidebar=True) 
        show_data_types = st.checkbox("Show data types")
        if show_data_types:
            st.write(dataframe.dtypes)

    #Clean dataframe
    elif action == "Clean dataframe":
        cleaning_function = st.sidebar.selectbox("Choose a cleaning function", ["Eliminar comas en columnas", "Borrar columnas","Redondear valores"])

        if cleaning_function == "Eliminar comas en columnas":
            user_input = user.choose_to_work()
            if st.button('Confirm'):
                user.no_comma(user_input)
                AgGrid(st.session_state.csv, gridOptions=vgo, height=550, columns_auto_size_mode=True,fit_columns_on_grid_load=True,enable_sidebar=True)

        elif cleaning_function == "Borrar columnas":
            user_input = user.choose_to_work()
            if st.button('Confirm'):
                user.remove_columns(user_input)
                AgGrid(st.session_state.csv, gridOptions=vgo, height=550, columns_auto_size_mode=True,fit_columns_on_grid_load=True,enable_sidebar=True)

        elif cleaning_function == "Redondear valores":
            user_input = user.choose_to_work()
            if st.button('Confirm'):
                user.value_rounded_2(user_input)
                AgGrid(st.session_state.csv, gridOptions=vgo, height=550, columns_auto_size_mode=True,fit_columns_on_grid_load=True,enable_sidebar=True)

        
    #Doownload excel file    
    elif action == "Print dataframe":
        if st.button('Create xlsx files'):
            user.printed_to_excel()
            st.session_state['confirmed'] = True  # Remember that the 'Confirm' button has been clicked

        if 'confirmed' in st.session_state:
            user.download_excel_files()

        if st.button('Save to SQLite'):
            #Create a column with the date in my user.csv
            user.csv['Download_date'] = datetime.now(pytz.timezone('America/Bogota')).strftime("%d/%m/%Y %H:%M:%S")

  


    #Show SQLite data
    elif action == "Show data":
        pass