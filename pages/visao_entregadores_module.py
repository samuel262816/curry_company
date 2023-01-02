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

def top_deliverers( df1, top_asc ):
    df_aux = ( df1.loc[:, ['delivery_person_id', 'city', 'time_taken(min)']]
                          .groupby( ['city', 'delivery_person_id']).mean()
                          .sort_values(['city','time_taken(min)'], ascending= top_asc).reset_index() )

    df_aux01 = df_aux.loc[ df_aux['city'] == 'Metropolitian', :].head(10)
    df_aux02 = df_aux.loc[ df_aux['city'] == 'Urban', :].head(10)
    df_aux03 = df_aux.loc[ df_aux['city'] == 'Semi-Urban', :].head(10)

    df_aux04 = pd.concat( [df_aux01, df_aux02, df_aux03] )
    return df_aux04



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
# 2. VISÃO ENTREGADORES
# ---------------------------------

st.markdown( '# Overall Metrics' )

with st.container():
    col1, col2, col3, col4 = st.columns(4, gap= 'large')
      
    with col1:
        maior_idade = df1.loc[ :, "delivery_person_age"].max()
        st.metric( 'Biggest age', maior_idade )

    with col2:
        menor_idade = df1.loc[ :, "delivery_person_age" ].min() 
        st.metric( 'Lowest age', menor_idade )

    with col3:
        melhor_cond = df1.loc[ :, "vehicle_condition" ].max() 
        st.metric( 'Better condition', menor_idade )

    with col4:
        pior_cond = df1.loc[ :, "vehicle_condition" ].min() 
        st.metric( 'Worst condition', menor_idade )


# -----------------------------------------------------------------------      
        
st.markdown( '''___''' )       
st.markdown( '## Deliverers Ratings' )


with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown( '### Mean rating by deliverer')
        df_aux = ( df1[['delivery_person_id', 'delivery_person_ratings']]
                    .groupby('delivery_person_id').mean()
                    .sort_values('delivery_person_id', ascending= False).reset_index() )
    
        st.dataframe( df_aux )
        
        
    with col2:
        # 1st table
        st.markdown( '### Mean rating by traffic')
        df_aux= ( df1[['delivery_person_ratings', 'road_traffic_density']]
                     .groupby('road_traffic_density').agg( {'delivery_person_ratings': ['mean', 'std']} ) )

        df_aux.columns = ['delivery_mean', 'delivery_std']
        df_aux.reset_index()
        st.dataframe( df_aux )
        
        
        # 2nd table
        st.markdown( '### Mean rating by weather conditions')
        df_aux = ( df1[['delivery_person_ratings', 'weatherconditions']]
                        .groupby('weatherconditions').agg( {'delivery_person_ratings': ['mean', 'std'] } ) )

        df_aux.columns = ['delivery_mean', 'delivery_std']
        df_aux.reset_index()
        st.dataframe( df_aux )
    
    
# -----------------------------------------------------------------------      

st.markdown( '''___''' )       
st.markdown( '## Top Deliverers' )

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown( '### Top fastest deliverers')
        df_aux04 = top_deliverers( df1, top_asc= True)
        st.dataframe( df_aux04 )
    
    
    with col2:        
        st.markdown( '### Top lowest deliverers')
        df_aux04 = top_deliverers( df1, top_asc= False)
        st.dataframe( df_aux04 )

    
    