import streamlit as st
import re
import pandas as pd
from sqlalchemy import create_engine

#-----------------------------------------------------------------------------#
# LEADS + MARKETING
st.cache_data
def marketing_leads():
    user     = st.secrets["user_colombia"]
    password = st.secrets["password_colombia"]
    host     = st.secrets["host_colombia"]
    schema   = st.secrets["schema_colombia"]
    engine   = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')    
   
    data_leads       = pd.read_sql_query("""SELECT * FROM colombia.marketing_leads """ , engine)
    data_callhistory = pd.read_sql_query("""SELECT * FROM colombia.app_callcenter_callhistory_inbound; """ , engine)
    data_clientes    = pd.read_sql_query("""SELECT * FROM colombia.app_callcenter_inbound_clientes; """ , engine)
    data_obs         = pd.read_sql_query(""" SELECT * FROM colombia.app_callcenter_inbound_obs; """ , engine)

    if data_leads.empty is False:
        if 'created_time' in data_leads:
            data_leads['created_time'] = pd.to_datetime(data_leads['created_time'],errors='coerce')
            
    if data_callhistory.empty is False:
        data_callhistory['phone_fix'] =  data_callhistory['contact_number'].apply(lambda x: fix_phone(x))
    
    if data_clientes.empty is False:
        data_clientes['phone_fix']    =  data_clientes['celular'].apply(lambda x: fix_phone(x))

    st.session_state.data_leads              = data_leads.copy()
    st.session_state.data_leads.index        = range(len(data_leads))
    st.session_state.data_leads_unicos       = data_leads.sort_values(by='created_time',ascending=True).drop_duplicates(subset=['phone_fix'],keep='first')
    st.session_state.data_leads_unicos.index = range(len(st.session_state.data_leads_unicos))
    st.session_state.data_callhistory        = data_callhistory.copy()
    st.session_state.data_callhistory.index  = range(len(data_callhistory))
    st.session_state.data_clientes           = data_clientes.copy()
    st.session_state.data_clientes.index     = range(len(data_clientes))
    st.session_state.data_obs                = data_obs.copy()
    st.session_state.data_obs.index          = range(len(data_obs))
    st.session_state.zoom_start    = 16
    st.session_state.secion_filtro = True
    #st.rerun()
    
    
def fix_phone(x):
    try: return re.sub('[^0-9]','',x.replace('+57',''))
    except: return None
        
    
st.cache_data
def marketing_metrics():
    user     = st.secrets["user_colombia"]
    password = st.secrets["password_colombia"]
    host     = st.secrets["host_colombia"]
    schema   = st.secrets["schema_colombia"]
    
    engine                  = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')    
    data_metrics_edad_sexo  = pd.read_sql_query("""SELECT * FROM colombia.marketing_metrics_edad_sexo """ , engine)
    data_metrics_plataforma = pd.read_sql_query("""SELECT * FROM colombia.marketing_metrics_plataforma """ , engine)
    
    st.session_state.data_metrics_edad_sexo       = data_metrics_edad_sexo.copy()
    st.session_state.data_metrics_edad_sexo.index = range(len(data_metrics_edad_sexo))
    
    st.session_state.data_metrics_plataforma       = data_metrics_plataforma.copy()
    st.session_state.data_metrics_plataforma.index = range(len(data_metrics_plataforma))