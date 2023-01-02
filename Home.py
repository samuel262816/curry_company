import streamlit as st
from PIL import Image

st.set_page_config( 
    page_title = 'Home',
)

image = Image.open( 'logo.png' )
st.sidebar.image( image, width= 150 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '### Fastest delivery in Town' )
st.sidebar.markdown( '''___''' )

st.markdown( '# Curry Company Growth Dashboard')

st.markdown( """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento da Empresa, dos Entregadores e dos Restaurantes.
    
    ### Como Utilizar esse Growth Dashboard?
    
    - #### Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Métricas gerais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
        
    - #### Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
        
    - #### Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
        
    ### Ask for Help:
        @Samuel
""")