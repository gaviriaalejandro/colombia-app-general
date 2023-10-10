import streamlit as st
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
import plotly.express as px

from scripts.getdata import marketing_leads,marketing_metrics

def main():
    
    st.set_page_config(layout="wide",initial_sidebar_state="collapsed")
    
    formato = {
               'polygonfilter':None,
               'zoom_start':12,
               'latitud':4.652652, 
               'longitud':-74.077899,
               'data_leads':pd.DataFrame(),
               'data_callhistory':pd.DataFrame(),
               'data_clientes':pd.DataFrame(),
               'data_obs':pd.DataFrame(),  
               'data_leads_unicos':pd.DataFrame(), 
               'data_metrics_edad_sexo':pd.DataFrame(), 
               'data_metrics_plataforma':pd.DataFrame(), 
               'secion_filtro':False,
               }
    
    for key,value in formato.items():
        if key not in st.session_state: 
            st.session_state[key] = value
    
    if st.session_state.data_leads.empty:
        marketing_leads()

    if st.session_state.data_metrics_edad_sexo.empty:
        marketing_metrics()
        
    plazo    = datetime.datetime.now() + relativedelta(months=-6)
    minyear  = plazo.year
    minmonth = plazo.month
    minday   = plazo.day

    plazo    = datetime.datetime.now()
    maxyear  = plazo.year
    maxmonth = plazo.month
    maxday   = plazo.day

    col1,col2 = st.columns(2)
    with col1:
        d1 = st.date_input("Desde:", datetime.datetime(minyear, minmonth, minday))
        d1_formatted = d1.strftime('%Y-%m-%d')

    with col2: 
        d2 = st.date_input("Hasta:", datetime.datetime(maxyear, maxmonth, maxday),max_value=datetime.datetime(maxyear, maxmonth, maxday))
        hora_23_59 = datetime.time(23, 59)
        d2 = datetime.datetime.combine(d2, hora_23_59)
        d2_formatted = d2.strftime('%Y-%m-%d %H:%M:%S')

    #-------------------------------------------------------------------------#
    # Analisis de leads de redes sociales
    #-------------------------------------------------------------------------#

    idd               = (st.session_state.data_leads['created_time']>=d1_formatted) & (st.session_state.data_leads['created_time']<=d2_formatted)
    data_leads        = st.session_state.data_leads[idd]
    idd               = (st.session_state.data_leads_unicos['created_time']>=d1_formatted) & (st.session_state.data_leads_unicos['created_time']<=d2_formatted)
    data_leads_unicos = st.session_state.data_leads_unicos[idd]

    idd                = data_leads_unicos['phone_fix'].isin(st.session_state.data_callhistory['phone_fix'])
    data_leads_call    = data_leads_unicos[idd]
    data_leads_notcall = data_leads_unicos[~idd]
    
    total_leads    = len(data_leads)
    leads_unicos   = len(data_leads_unicos)
    leads_llamados = len(data_leads_call)
    
    idd                = st.session_state.data_callhistory['phone_fix'].isin(data_leads_unicos['phone_fix'])
    data_leads_visit   = st.session_state.data_callhistory[idd]
    data_leads_visit   = data_leads_visit[data_leads_visit['date_visit'].notnull()]
    visitas_agendadas  = len(data_leads_visit)
    data_leads_visit   = data_leads_visit[data_leads_visit['visit_check']==1]
    visitas_realizadas = len(data_leads_visit)
    
    try:    pleads_unicos = '('+"{:.1%}".format(leads_unicos/total_leads)+')'
    except: pleads_unicos = '&nbsp;'
    
    try:    pleads_llamados = '('+"{:.1%}".format(leads_llamados/leads_unicos)+')'
    except: pleads_llamados = '&nbsp;'
    
    try:    pvisitas_agendadas = '('+"{:.1%}".format(visitas_agendadas/leads_unicos)+')'
    except: pvisitas_agendadas = '&nbsp;'
    
    try:    pvisitas_realizadas = '('+"{:.1%}".format(visitas_realizadas/leads_unicos)+')'
    except: pvisitas_realizadas = '&nbsp;'    
    
    formato = [
        {'key':'Total leads','value':total_leads,'porcentage':'&nbsp;'},
        {'key':'Leads únicos','value':leads_unicos,'porcentage':pleads_unicos},
        {'key':'Leads llamados','value':leads_llamados,'porcentage':pleads_llamados},
        {'key':'Visitas agendadas','value':visitas_agendadas,'porcentage':pvisitas_agendadas},
        {'key':'Visitas realizadas','value':visitas_realizadas,'porcentage':pvisitas_realizadas},
    ]
    
    html_paso = ''
    for j in formato:
        
        tamanoletra = '1.5rem'

        # Crear el bloque HTML correspondiente a cada iteración
        html_paso += f"""
        <div class="col-xl-2 col-sm-2 mb-xl-0 mb-2">
          <div class="card">
            <div class="card-body p-3">
              <div class="row">
                <div class="numbers">
                  <h3 class="font-weight-bolder mb-0" style="text-align: center;font-size: {tamanoletra};">{j['value']}</h3>
                  <p class="mb-0 text-capitalize" style="font-weight: 300;font-size: 1rem;text-align: center;">{j['key']}</p>
                  <p class="mb-0 text-capitalize" style="font-weight: 300;font-size: 1rem;text-align: center;">{j['porcentage']}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
            
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet" />
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet" />
      <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet" />
    </head>
    <body>
    <div class="container-fluid py-1">
    <div class="row">
    <div class="row" style="margin-bottom: 30px;">
      <div class="card-body p-3">
        <div class="row">
          <div class="numbers">
            <h3 class="font-weight-bolder mb-0" style="text-align: center; font-size: 1.5rem;border-bottom: 0.5px solid #ccc; padding-bottom: 8px;">Funnel de leads</h3>
          </div>
        </div>
      </div>
    </div>
    {html_paso}
    </div>
    </div>
    </body>
    </html>        
    """
    
    texto = BeautifulSoup(html, 'html.parser')
    st.markdown(texto, unsafe_allow_html=True)
    
    #-------------------------------------------------------------------------#
    # Analisis de costos
    #-------------------------------------------------------------------------#

    idd          = (st.session_state.data_metrics_edad_sexo['dia']>=d1_formatted) & (st.session_state.data_metrics_edad_sexo['dia']<=d2_formatted)
    data_metrics_edad_sexo = st.session_state.data_metrics_edad_sexo[idd]
    data_metrics_edad_sexo = data_metrics_edad_sexo[data_metrics_edad_sexo['resultados']>0]
    
    formato = [
        {'key':'Anuncios activos','value':len(data_metrics_edad_sexo[(data_metrics_edad_sexo['estado_de_la_entrega']=='active') | (data_metrics_edad_sexo['resultados']>0)].drop_duplicates(subset='nombre_del_anuncio',keep='first'))},
        {'key':'Total Gasto','value':f"${data_metrics_edad_sexo['importe_gastado_(cop)'].sum():,.0f}"},
        {'key':'Costo por lead','value':f"${data_metrics_edad_sexo['costo_por_resultado'].mean():,.0f}"},
        {'key':'CPC (enlace)','value':f"${data_metrics_edad_sexo['cpc_(costo_por_clic_en_el_enlace)'].mean():,.0f}"},
        {'key':'CTR','value':"{:.1%}".format(data_metrics_edad_sexo['ctr_(todos)'].mean()/100)},
        {'key':'clics enlace','value':"{:.1%}".format(data_metrics_edad_sexo['clics_en_el_enlace'].sum()/data_metrics_edad_sexo['clics_(todos)'].sum())},
    ]
    
    html_paso = ''
    for j in formato:
        
        tamanoletra = '1.5rem'

        # Crear el bloque HTML correspondiente a cada iteración
        html_paso += f"""
        <div class="col-xl-2 col-sm-2 mb-xl-0 mb-2">
          <div class="card">
            <div class="card-body p-3">
              <div class="row">
                <div class="numbers">
                  <h3 class="font-weight-bolder mb-0" style="text-align: center;font-size: {tamanoletra};">{j['value']}</h3>
                  <p class="mb-0 text-capitalize" style="font-weight: 300;font-size: 1rem;text-align: center;">{j['key']}</p>
                  </div>
              </div>
            </div>
          </div>
        </div>
        """
            
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet" />
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet" />
      <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet" />
    </head>
    <body>
    <div class="container-fluid py-1">
    <div class="row">
    <div class="row" style="margin-bottom: 30px;">
      <div class="card-body p-3">
        <div class="row">
          <div class="numbers">
            <h3 class="font-weight-bolder mb-0" style="text-align: center; font-size: 1.5rem;border-bottom: 0.5px solid #ccc; padding-bottom: 8px;">Metricas</h3>
          </div>
        </div>
      </div>
    </div>
    {html_paso}
    </div>
    </div>
    </body>
    </html>        
    """
    
    texto = BeautifulSoup(html, 'html.parser')
    st.markdown(texto, unsafe_allow_html=True)

    #-------------------------------------------------------------------------#
    # Graficas
    #-------------------------------------------------------------------------#
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet">
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet">
      <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet">
    <style>
        .snr-table {
          overflow-x: auto;
          overflow-y: auto; 
          max-width: 100%; 
          max-height: 250px; 
        }    
        .catastro-table {
          max-height: 250px; 
          overflow-y: auto; 
        }
    </style>
    </head>
    <body>
      <div class="container-fluid py-4">
        <div class="row">
        <div class="container-fluid py-4">
          <div class="row" style="margin-bottom: -30px;">
            <div class="card-body p-3">
              <div class="row">
                <div class="numbers">
                  <h3 class="font-weight-bolder mb-0" style="text-align: center; font-size: 1.5rem;border-bottom: 0.5px solid #ccc; padding-bottom: 8px;">Estadisticas</h3>
                </div>
              </div>
            </div>
          </div>
        </div>                
        </div>
      </div>
    </body>
    </html>
    """     
    texto = BeautifulSoup(html, 'html.parser')
    st.markdown(texto, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_estadistica = st.selectbox("Tipo de estadísticas:", options=["Leads","Alcance","Impresiones","Clics"])
    with col2:
        tipo_filtro = st.selectbox("Filtro por:", options=["Total","Red social","Tipo de publicacion","Edad","Sexo","Anuncio"]) # ,"Formulario"
    with col3:
        frecuencia  = st.selectbox("Frecuencia:", options=["Semanal","Mensual"])
    
    filtros_r = {
        "Red social":"plataforma",
        "Tipo de publicacion":"ubicacion",
        "Edad":"edad",
        "Sexo":"sexo",
        "Anuncio":"nombre_del_conjunto_de_anuncios"
               }
    
    estadistica_r = {
        "Leads":"resultados",
        "Alcance":"alcance" ,
        "Impresiones":"impresiones",
        "Clics":"clics_(todos)", 
               }
    
    if any([w for w in ["Total","Edad","Sexo"] if tipo_filtro in w]):
        idd   = (st.session_state.data_metrics_edad_sexo['dia']>=d1_formatted) & (st.session_state.data_metrics_edad_sexo['dia']<=d2_formatted)
        df    = st.session_state.data_metrics_edad_sexo[idd]
        df    = df.set_index(['dia'])        
        
    elif any([w for w in ["Red social","Anuncio","Tipo de publicacion"] if tipo_filtro in w]):
        idd   = (st.session_state.data_metrics_plataforma['dia']>=d1_formatted) & (st.session_state.data_metrics_plataforma['dia']<=d2_formatted)
        df    = st.session_state.data_metrics_plataforma[idd]
        df    = df.set_index(['dia'])
 
    if frecuencia=='Mensual':
        if tipo_filtro=="Total":
            df = df.groupby(pd.Grouper(freq='M'))
        else:
            df = df.groupby([pd.Grouper(freq='M'),filtros_r[tipo_filtro]])

    if frecuencia=='Semanal':
        if tipo_filtro=="Total":
            df = df.groupby(pd.Grouper(freq='W'))
        else:
            df = df.groupby([pd.Grouper(freq='W'),filtros_r[tipo_filtro]])
    
    if tipo_filtro=="Total":
        df          = df[estadistica_r[tipo_estadistica]].sum().reset_index()
        df.columns  = ['Fecha','column']
        df['Fecha'] = df['Fecha'].astype(str)
        
        fig = go.Figure(data=[go.Bar(x=df['Fecha'], y=df['column'])])
        fig.update_traces(text=df['column'], textposition='outside')
    
        fig.update_layout(
            title=f'Total de {tipo_estadistica}',
            xaxis_title='Fecha',
            yaxis_title=tipo_estadistica,
            title_x=0.5,
        )
        
        fig.update_xaxes(
            tickformat='%b %Y',
            tickmode='auto',
        )
        st.plotly_chart(fig,use_container_width=True)
        
    else:
        df         = df[estadistica_r[tipo_estadistica]].sum().reset_index()
        df.columns = ['Fecha',tipo_filtro,tipo_estadistica]
        color      = tipo_filtro
        
        df['Fecha'] = df['Fecha'].astype(str)
        
        fig = px.bar(
            df, 
            x='Fecha', 
            y=tipo_estadistica, 
            color=color,
            title=f'Total de {tipo_estadistica}',
            #color_continuous_scale="reds",
        )
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        fig.update_layout(
            title_x=0.5,
        )
            
        st.plotly_chart(fig,use_container_width=True)
        

    #-------------------------------------------------------------------------#
    # Por anuncio
    #-------------------------------------------------------------------------#
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet">
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet">
      <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet">
    <style>
        .snr-table {
          overflow-x: auto;
          overflow-y: auto; 
          max-width: 100%; 
          max-height: 250px; 
        }    
        .catastro-table {
          max-height: 250px; 
          overflow-y: auto; 
        }
    </style>
    </head>
    <body>
      <div class="container-fluid py-4">
        <div class="row">
        <div class="container-fluid py-4">
          <div class="row" style="margin-bottom: -30px;">
            <div class="card-body p-3">
              <div class="row">
                <div class="numbers">
                  <h3 class="font-weight-bolder mb-0" style="text-align: center; font-size: 1.5rem;border-bottom: 0.5px solid #ccc; padding-bottom: 8px;">Estadisticas por anuncio</h3>
                </div>
              </div>
            </div>
          </div>
        </div>                
        </div>
      </div>
    </body>
    </html>
    """     
    texto = BeautifulSoup(html, 'html.parser')
    st.markdown(texto, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_estadistica_anuncio = st.selectbox("Tipo de estadísticas por anuncio:", options=["Leads","Alcance","Impresiones","Gasto total", "Gasto por lead", "Clics enlace", "Total clics", "CPC enlace", "CPC", "CPM", "CTR"])
          
    formato_filtro = {
        "Leads":'resultados',
        "Alcance":'alcance',
        "Impresiones":'impresiones',
        "Gasto total":'importe_gastado_(cop)',
        "Gasto por lead":'costo_por_resultado',
        "Clics enlace":'clics_en_el_enlace',
        "Total clics":'clics_(todos)',
        "CPC enlace":'cpc_(costo_por_clic_en_el_enlace)',
        "CPC":'cpc_(todos)',
        "CPM":'cpm_(costo_por_mil_impresiones)',
        "CTR":'ctr_(todos)',
        }
    
    if any([w for w in ["Total","Edad","Sexo"] if tipo_filtro in w]):
        idd   = (st.session_state.data_metrics_edad_sexo['dia']>=d1_formatted) & (st.session_state.data_metrics_edad_sexo['dia']<=d2_formatted)
        df    = st.session_state.data_metrics_edad_sexo[idd]    
        
    elif any([w for w in ["Red social","Anuncio","Tipo de publicacion"] if tipo_filtro in w]):
        idd   = (st.session_state.data_metrics_plataforma['dia']>=d1_formatted) & (st.session_state.data_metrics_plataforma['dia']<=d2_formatted)
        df    = st.session_state.data_metrics_plataforma[idd]


    df  = df.groupby(['nombre_del_conjunto_de_anuncios'])[formato_filtro[tipo_estadistica_anuncio]].sum().reset_index()
    df  = df.sort_values(by=formato_filtro[tipo_estadistica_anuncio],ascending=False)
    
    
    fig = go.Figure(data=[go.Bar(x=df['nombre_del_conjunto_de_anuncios'], y=df[formato_filtro[tipo_estadistica_anuncio]])])
    fig.update_traces(text=df[formato_filtro[tipo_estadistica_anuncio]], textposition='outside')

    fig.update_layout(
        title=f'Total de {tipo_estadistica_anuncio}',
        yaxis_title=tipo_estadistica_anuncio,
        title_x=0.5,
        height=600,
    )
    
    fig.update_xaxes(
        tickformat='%b %Y',
        tickmode='auto',
    )
    st.plotly_chart(fig,use_container_width=True)    
    
    
    #-------------------------------------------------------------------------#
    # Comentarios de las personas
    
    #-------------------------------------------------------------------------#
    # Falta por llamar 
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet">
      <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet">
      <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet">
    <style>
        .snr-table {
          overflow-x: auto;
          overflow-y: auto; 
          max-width: 100%; 
          max-height: 250px; 
        }    
        .catastro-table {
          max-height: 250px; 
          overflow-y: auto; 
        }
    </style>
    </head>
    <body>
      <div class="container-fluid py-4">
        <div class="row">
        <div class="container-fluid py-4">
          <div class="row" style="margin-bottom: -30px;">
            <div class="card-body p-3">
              <div class="row">
                <div class="numbers">
                  <h3 class="font-weight-bolder mb-0" style="text-align: center; font-size: 1.5rem;border-bottom: 0.5px solid #ccc; padding-bottom: 8px;">Leads por llamar</h3>
                </div>
              </div>
            </div>
          </div>
        </div>                
        </div>
      </div>
    </body>
    </html>
    """     
    texto = BeautifulSoup(html, 'html.parser')
    st.markdown(texto, unsafe_allow_html=True)
    
    data_leads_notcall = data_leads_notcall[['created_time', 'ad_name', 'form_name', 'platform', 'full_name', 'email', 'phone', 'phone_fix']]
    data_leads_notcall = data_leads_notcall.sort_values(by='created_time',ascending=False)
    data_leads_notcall.index = range(len(data_leads_notcall))
    st.dataframe(data_leads_notcall)
    
    csv = convert_df(data_leads_notcall)     
    st.download_button(
       "Descargar leads por llamar",
       csv,
       "leads_por_llamar.csv",
       "text/csv",
       key='leads_por_llamar'
    )      

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')