#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go  # Corrigido
import pandas as pd
import re
import streamlit as st
import datetime  # ✅ Importe o módulo datetime
from PIL import Image
import folium

#biblioteca
import pandas as pd

#import dataset 
df = pd.read_csv( 'train.crdownload')


# Remover espaços das colunas específicas
df['ID'] = df['ID'].astype(str).str.strip()
df['Delivery_person_ID'] = df['Delivery_person_ID'].astype(str).str.strip()

# Garantir que 'Delivery_person_Age' é string antes de usar .str.strip()
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(str).str.strip()

# Substituir valores inválidos por NaN e converter para número
df['Delivery_person_Age'] = pd.to_numeric(df['Delivery_person_Age'], errors='coerce')

# Remover linhas onde 'Delivery_person_Age' está vazio
df = df.dropna(subset=['Delivery_person_Age'])

# Converter idade para inteiro
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

# Converter avaliações para float
df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')

# Converter datas para o formato correto
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y', errors='coerce')

# Excluir linhas onde 'multiple_deliveries' está vazio ou inválido
df['multiple_deliveries'] = pd.to_numeric(df['multiple_deliveries'], errors='coerce')
df = df.dropna(subset=['multiple_deliveries'])
df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

# Extrair números de 'Time_taken(min)'
df['Time_taken(min)'] = df['Time_taken(min)'].astype(str).apply(lambda x: ''.join(re.findall(r'\d+', x)))
df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')

# Resetar o índice
df = df.reset_index(drop=True)

##################################
################################# Barra lateral 
st.header('Marketplace - Visão Entregadores')

#image_path = 'logo.png'
image = Image.open('Logo.png')
st.sidebar.image(image, width=120)


st.sidebar.markdown('#Cury Company')
st.sidebar.markdown('## Fatest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.date(2022, 4, 13),  # Usando datetime.date
    min_value=datetime.date(2022, 2, 11),  # Usando datetime.date
    max_value=datetime.date(2022, 4, 6),  # Usando datetime.date
    format='DD-MM-YYYY'
)

st.sidebar.markdown("""___""")

# Supondo que date_slider seja a data selecionada pelo usuário no Streamlit
# Garantir que date_slider seja do tipo datetime
date_slider = pd.to_datetime(date_slider)

# Exibe a data selecionada de forma formatada
st.header(f"Data Selecionada: {date_slider.strftime('%d/%m/%Y')}")

# Opções de condições de tráfego
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

# Filtra as linhas com base nas opções de tráfego selecionadas
# Certifique-se de que não haja espaços extras e que as maiúsculas/minúsculas sejam tratadas corretamente
df['Road_traffic_density'] = df['Road_traffic_density'].str.strip().str.lower()

# Garantir que os valores de 'traffic_options' também sejam minúsculos e sem espaços extras
traffic_options = [option.lower() for option in traffic_options]

# Filtra o DataFrame com base nas condições de tráfego selecionadas
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)

# Aplica o filtro
df = df.loc[linhas_selecionadas, :]

# Exibe o DataFrame filtrado
st.dataframe(df)

##################################
#################################  Layout

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns (4, gap='large')
        
        with col1:
             
           
            maior_idade = df['Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)
        with col2:
           
            menor_idade = df['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            
            melhor_condicao =  df[ 'Vehicle_condition'].max()
            col3.metric('Melhor condicao', melhor_condicao)
        with col4:
            
            pior_condicao = df[ 'Vehicle_condition'].min()
            col4.metric('pior condicao', pior_condicao)
   
    with st.container():
         st.sidebar.markdown("""___""")
         st.title('Avaliações')
       
         
        
         
         col1, col2 = st.columns (2)
         with col1:
             st.subheader('Avaliacao medias por entregador')
             
         # Garantir que a coluna de avaliação é numérica
             df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')

# Remover valores nulos
             df = df.dropna(subset=['Delivery_person_Ratings'])

# Calcular a média de avaliação por entregador
             avaliacao_media = df.groupby('Delivery_person_ID')['Delivery_person_Ratings'].mean().reset_index()
             st.dataframe(avaliacao_media)
         
         
             
        
         with col2:
             st.subheader('Avaliacao media por transito')
             # Garantir que a coluna de avaliação seja numérica
             df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')

# Remover valores nulos
             df = df.dropna(subset=['Delivery_person_Ratings', 'Road_traffic_density'])

# Calcular média e desvio padrão por tipo de tráfego
             traffic_ratings = df.groupby('Road_traffic_density')['Delivery_person_Ratings'].agg(['mean', 'std']).reset_index()

# Renomear as colunas para facilitar a leitura
             traffic_ratings.rename(columns={'mean': 'Average_Rating', 'std': 'Std_Deviation'}, inplace=True)

# Exibir os resultados
             st.dataframe(traffic_ratings)
             
             st.subheader('Avaliacao media por clima')
             # Garantir que a coluna de avaliação seja numérica
             df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')

# Remover valores nulos
             df = df.dropna(subset=['Delivery_person_Ratings', 'Weatherconditions'])

# Calcular média e desvio padrão por condição climática
             weather_ratings = df.groupby('Weatherconditions')['Delivery_person_Ratings'].agg(['mean', 'std']).reset_index()

# Renomear as colunas para facilitar a leitura
             weather_ratings.rename(columns={'mean': 'Average_Rating', 'std': 'Std_Deviation'}, inplace=True)

# Exibir os resultados
             st.dataframe(weather_ratings)
             
    with st.container():
        st.sidebar.markdown("""___""")
        st.title('Velocidade de Entrega')
        
        
        col1, col2 = st.columns (2)
        with col1:
             st.subheader('Top Entregadores mais rapidos')
             # Garantir que a coluna de tempo de entrega seja numérica
             df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')
 
# Remover valores nulos
             df = df.dropna(subset=['Time_taken(min)', 'City', 'Delivery_person_ID'])

# Ordenar do menor para o maior tempo de entrega
             df_sorted = df.sort_values(by=['City', 'Time_taken(min)'], ascending=[True, True])

# Selecionar os 10 entregadores mais rápidos por cidade
             top_10_fastest = df_sorted.groupby('City').head(10)

# Exibir os resultados
             st.dataframe(top_10_fastest)
        
        with col2:
             st.subheader('Top Entregadores mais lentos')
             # Garantir que a coluna de tempo de entrega seja numérica
             df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')

# Remover valores nulos
             df = df.dropna(subset=['Time_taken(min)', 'City', 'Delivery_person_ID'])

# Ordenar do maior para o menor tempo de entrega (os mais lentos primeiro)
             df_sorted = df.sort_values(by=['City', 'Time_taken(min)'], ascending=[True, False])

# Selecionar os 10 entregadores mais lentos por cidade
             top_10_slowest = df_sorted.groupby('City').head(10)
 
# Exibir os resultados no Streamlit
             st.dataframe(top_10_slowest)