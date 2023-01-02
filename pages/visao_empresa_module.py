# LIBRARIES
import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px

from haversine import haversine
from streamlit_folium import folium_static
from PIL import Image


#----------------------------------
# FUNCTIONS
#----------------------------------

def country_maps( df1 ):
    df_aux = ( df1.loc[:, ['city', 'road_traffic_density', 'delivery_location_latitude', 
                           'delivery_location_longitude']]
                            .groupby(['city', 'road_traffic_density']).median().reset_index() )

    map = folium.Map()

    for i, loc_info in df_aux.iterrows():
        folium.Marker( [loc_info['delivery_location_latitude'], 
                        loc_info['delivery_location_longitude']],
                        popup= loc_info[['city', 'road_traffic_density']]).add_to( map )

    folium_static( map, width=1400 ,height=680 )
    return None


def order_delivered_by_week( df1 ):
    # quantidade de pedidos por semana
    df_aux = df1.loc[:, ['id', 'week_of_year']].groupby('week_of_year').count().reset_index()

    # quantidade de entregadores unicos por semana
    df_aux2 = (df1.loc[:, ['delivery_person_id', 'week_of_year']]
               .groupby('week_of_year').nunique().reset_index() )

    # merge df_aux + df_aux2
    df_aux = pd.merge( df_aux, df_aux2, how= 'inner' )
    df_aux['order_by_delivery'] = df_aux['id'] / df_aux['delivery_person_id']   
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery')
    return fig


def order_by_week( df1 ):
    df_aux = df1[['id', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line( df_aux, x='week_of_year', y='id')
    return fig
            
def traffic_order_share( df1 ):
    df_aux = ( df1[['id','road_traffic_density','city']]
                    .groupby(['city','road_traffic_density']).count().reset_index() )
    fig = px.scatter( df_aux, x='city', y='road_traffic_density', size='id')
    return fig
        
            
def order_by_traffic( df1 ):
    df_aux = df1[['id', 'road_traffic_density']].groupby('road_traffic_density').count().reset_index()
    df_aux['percent'] = df_aux['id'] / df_aux['id'].sum()
    fig = px.pie( df_aux, names='road_traffic_density', values='percent' )
    return fig


def order_by_day( df1 ):
    df_aux = df1[['id', 'order_date']].groupby('order_date').count().reset_index()
    fig = px.bar( data_frame= df_aux, x='order_date', y='id')
    return fig


def clean_code( df1 ):
    # rename
    old_col = ['ID', 'Delivery_person_ID', 'Delivery_person_Age', 'Delivery_person_Ratings', 'Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude', 'Order_Date', 'Time_Orderd', 'Time_Order_picked', 'Weatherconditions', 'Road_traffic_density', 'Vehicle_condition', 'Type_of_order', 'Type_of_vehicle', 'multiple_deliveries', 'Festival', 'City', 'Time_taken(min)']

    snakecase = lambda x: x.lower()

    new_cols = list( map( snakecase, old_col ))

    df1.columns = new_cols

    # remove spaces in the strings
    df1 = df1.applymap( lambda x: x.strip() if isinstance(x, str) else x )

    # convertendo a coluna age para int
    df1 = df1[ df1['delivery_person_age'] != 'NaN' ]
    df1['delivery_person_age'] = df1['delivery_person_age'].astype('int64')

    # convertendo a coluna ratings para float
    df1['delivery_person_ratings'] = df1['delivery_person_ratings'].astype(float)

    # convertendo a coluna order_datew para data
    df1['order_date'] = pd.to_datetime( df1['order_date'], format= '%d-%m-%Y')

    # convertendo a coluna multiples deliveries para int
    df1 = df1[ df1['multiple_deliveries'] != 'NaN' ]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype('int64')

    # limpando e convertendo para int a coluna time_taken
    df1['time_taken(min)'] = df1['time_taken(min)'].apply( lambda x: x.split('(min) ')[1] )
    df1['time_taken(min)'] = df1['time_taken(min)'].astype( 'int64' )

    # filtrando NA road_traffic_density
    df1 = df1[ df1['road_traffic_density'] != 'NaN']

    # filtrando NA city
    df1 = df1[ df1['city'] != 'NaN']

    # filtrando NA festival
    df1 = df1[ df1['festival'] != 'NaN']
    
    return df1


def feature_engineering( df1 ):
    # criando semana do ano
    df1['week_of_year'] = df1['order_date'].dt.strftime( '%U' )
    
    return df1


#----------------------------------
# ESTRUTURA LÓGICA DO CÓDIGO
#----------------------------------

# IMPORT DATASET
df1 = pd.read_csv( 'dataset/train.csv' )

df1 = clean_code( df1 )

df1 = feature_engineering( df1 )


#----------------------------------
# DASHBOARD STREAMLIT
#----------------------------------

st.set_page_config(
    page_title= 'Visao Empresa',
    layout= 'wide' )


# 1. SIDEBAR

image = Image.open( 'logo.png' )
st.sidebar.image( image, width= 150 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '### Fastest delivery in Town' )
st.sidebar.markdown( '''___''' )

st.sidebar.markdown( '## Selecione uma data limite' )

data_slider = st.sidebar.slider( 'Data limite', 
                                  value= pd.datetime( 2022, 3, 1 ),
                                  min_value= pd.datetime( 2022, 2, 11) ,
                                  max_value= pd.datetime( 2022, 4, 6),
                                  format = 'DD-MM-YYYY')

st.sidebar.markdown( '''___''' )

# st.sidebar.markdown( '## Quais as condições de trânsito? ' )
# st.sidebar.checkbox( 'Low' , value= True)
# st.sidebar.checkbox( 'Medium' )
# st.sidebar.checkbox( 'High' )
# st.sidebar.checkbox( 'Jam' )


traffic_options = st.sidebar.multiselect( 'Quais as condições de trânsito? ',
                                          ['Low', 'Medium', 'High', 'Jam'],
                                          default= ['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( '''___''' )
st.sidebar.markdown( '# Powered by ComunidadeDS')

# Filtros
df1 = df1.loc[ df1['order_date'] < data_slider, : ]

df1 = df1.loc[ df1['road_traffic_density'].isin( traffic_options ), :]



# Separando em páginas
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica '])

# ---------------------------------
# 2. VISÃO EMPRESA
# ---------------------------------

with tab1:
    # Order day
    with st.container():
        st.markdown( '#### Order by day' )
        fig = order_by_day( df1 )
        st.plotly_chart( fig, use_container_width= True )
                          
    
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '### Order by traffic' )
            fig = order_by_traffic( df1 )
            st.plotly_chart( fig, use_container_width= True )
            
        with col2:
            st.markdown( '### Traffic Order Share' )
            fig = traffic_order_share( df1 )
            st.plotly_chart( fig, use_container_width= True )

# ---------------------------------------------------------------------------------------------------            
            
with tab2:
    with st.container():
        st.markdown( '### Order by week' )
        fig = order_by_week( df1 )
        st.plotly_chart( fig, use_container_width= True )

        
    with st.container():
        st.markdown( '### Order delivered by week' )
        fig = order_delivered_by_week( df1 )
        st.plotly_chart( fig, use_container_width= True )
            
# ---------------------------------------------------------------------------------------------------               
with tab3:
    st.markdown( '### Country Maps' )
    country_maps( df1 )
