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

def mean_time_by_city( df1 ):
    df_aux = df1[['city', 'time_taken(min)', 'road_traffic_density']].groupby(['city', 'road_traffic_density']).agg({'time_taken(min)': ['mean', 'std']} )

    df_aux.columns = ['mean_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = ( px.sunburst( data_frame= df_aux, 
                        path= ['city', 'road_traffic_density'], 
                        values= 'mean_time', color = 'std_time', 
                        color_continuous_scale= 'RdBu' ) )
    return fig


def mean_distance_city( df1 ):
    cols = ['restaurant_latitude', 'restaurant_longitude', 
            'delivery_location_latitude', 'delivery_location_longitude']

    df1['distance'] = ( df1.loc[: , cols].apply( lambda x: 
                    haversine( ( x['restaurant_latitude'], x['restaurant_longitude'] ),
                    ( x['delivery_location_latitude'], x['delivery_location_longitude'] )), axis=1 ))

    avg_distance = df1[['city' , 'distance']].groupby('city').mean().reset_index()

    fig = px.pie( data_frame = avg_distance, names= 'city', values= 'distance')
    return fig


def mean_delivered_time_by_city_traffic( df1 ):
    df_aux = ( df1[['city', 'time_taken(min)', 'type_of_order']]
            .groupby(['city', 'type_of_order']).agg({'time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['mean_time', 'std_time']
    df_aux = df_aux.reset_index()
    return df_aux


def mean_delivered_time_by_city( df1 ):
    df_aux = ( df1[['city', 'time_taken(min)']]
                  .groupby('city').agg( {'time_taken(min)': ['mean', 'std'] } ) )

    df_aux.columns = ['mean_time', 'std_time' ]
    df_aux = df_aux.reset_index()
    fig = px.bar( df_aux, x='city', y='mean_time', width= 600 )
    return fig

def mean_time_std_festival( df1, festival, operation ):
    """
    Essa funcão calcula a média e desvio padrão do tempo de entrega, seja com ou sem festival.
    
    Input = Dataframe, festival, operation:
        - df: dataframe com os dados a serem calculados
        - festival - 'Yes' se houver festival e 'No' se não houver
        - operation: Tipo de operação a ser calculada
            'mean_time': Calcula o tempo médio
            'std_time': Calcula o desvio padrão do tempo
    
    Output: Dataframe
    """
    df_aux = df1[['festival', 'time_taken(min)']].groupby('festival').agg( ['mean', 'std'] )
    df_aux.columns = ['mean_time', 'std_time' ]
    df_aux = df_aux.reset_index()
    
    df_aux = df_aux.loc[ df_aux['festival'] == festival , operation ]
    return df_aux


def mean_distance( df1 ):
    cols = ['restaurant_latitude', 'restaurant_longitude', 
            'delivery_location_latitude', 'delivery_location_longitude']

    df1['distance'] = ( df1.loc[: , cols]
                       .apply( lambda x: haversine( ( x['restaurant_latitude'],
                        x['restaurant_longitude'] ), ( x['delivery_location_latitude'], 
                        x['delivery_location_longitude'] )), axis=1 ) )

    mean_distance = round( df1['distance'].mean(), 2)
    return mean_distance


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

st.set_page_config(
    page_title= 'Visao Entregadores',
    layout= 'wide' )


# IMPORT DATASET
df1 = pd.read_csv('dataset/train.csv')
print( df1.head() )


df1 = clean_code( df1 )

df1 = feature_engineering( df1 )


# ---------------------------------
# 1. SIDEBAR
# ---------------------------------
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


# ---------------------------------
# 2. VISÃO RESTAURANTES
# ---------------------------------

st.markdown( '## Overall Metrics' )

with st.container():
    col1, col2, col3, col4, col5, col6 = st.columns( 6, gap= 'large' )
   
    # Entregadores únicos
    with col1:
        delivery_unique = len( df1.loc[:, 'delivery_person_id'].unique() )
        st.metric( 'Unique deliverers', delivery_unique )

    # Distancia média
    with col2:
        mean_distance = mean_distance( df1 )
        st.metric( 'Mean distance', mean_distance )
        
    # Tempo médio de entrega com festival
    with col3:
        df_aux = mean_time_std_festival( df1, festival= 'Yes', operation= 'mean_time' )
        st.metric( 'Mean time with festival', round(df_aux, 2) )
        
    # Desvio padrao de entrega com festival
    with col4:
        df_aux = mean_time_std_festival( df1, festival= 'Yes', operation= 'std_time')
        st.metric( 'Std with festival', round(df_aux, 2) )
        
    # Tempo médio de entrega sem festival    
    with col5:
        df_aux = mean_time_std_festival( df1, festival= 'No', operation= 'mean_time')
        st.metric( 'Mean time without festival', round(df_aux, 2) )
        
    # Desvio padrao de entrega sem festival    
    with col6:
        df_aux = mean_time_std_festival( df1, festival= 'No', operation= 'std_time')
        st.metric( 'Std without festival', round(df_aux, 2) )

# -----------------------------------------------------------------------      
        
st.markdown( '''___''' )       

with st.container():
    col1, col2 = st.columns( 2 )
    
    with col1:
        st.markdown( '### Mean delivered time by city')
        fig = mean_delivered_time_by_city( df1 )
        st.plotly_chart( fig )
        
    with col2:
        st.markdown( '### Mean time by city and traffic')
        df_aux = mean_delivered_time_by_city_traffic( df1 )
        st.dataframe( df_aux )
    
# ------------------------------------------------------------------------
    
st.markdown( '''___''' )   
    
with st.container():
    col1, col2 = st.columns( 2 )
    
    with col1:
        st.markdown( '### Mean distance by city')
        fig = mean_distance_city( df1 )
        st.plotly_chart( fig, use_container_width= True )
    
    with col2:
        st.markdown( '### Mean time by city')
        fig = mean_time_by_city( df1 )
        st.plotly_chart( fig )