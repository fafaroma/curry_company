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
from geopy.distance import geodesic
import matplotlib.pyplot as plt

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
st.header('Marketplace - Visão Restaurantes')

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
         st.title('Over Metrics')
         
         col1, col2, col3, col4, col5, col6 = st.columns (6)
         with col1:
              st.title('seila')
              # Remover valores nulos na coluna de ID dos entregadores
         df = df.dropna(subset=['Delivery_person_ID'])

# Contar entregadores únicos
         num_entregadores = df['Delivery_person_ID'].nunique()
         col1.metric('Entregadores Unicos', num_entregadores)
         
         with col2:
              st.title('seila')
              df = df.rename(columns={
             'delivery_location_latitude': 'Delivery_location_latitude',
             'delivery_location_longitude': 'Delivery_location_longitude',
             'restaurant_latitude': 'Restaurant_latitude',
             'restaurant_longitude': 'Restaurant_longitude'
             })

# Remover valores nulos nas colunas necessárias
              df = df.dropna(subset=['Delivery_location_latitude', 'Delivery_location_longitude',
                        'Restaurant_latitude', 'Restaurant_longitude'])

# Calcular a distância entre restaurante e local de entrega usando a fórmula de Haversine
              df['Distance_km'] = df.apply(lambda row: geodesic(
              (row['Restaurant_latitude'], row['Restaurant_longitude']),
              (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
              ).km, axis=1)

# Calcular a distância média
              distancia_media = df['Distance_km'].mean()
              col2.metric(label="Distância Média (km)", value=f"{distancia_media:.2f}")

         with col3:
              st.title('seila')
              # Garantir que a coluna 'Time_taken(min)' seja numérica
              df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')

# Remover valores nulos nas colunas necessárias
              df = df.dropna(subset=['Time_taken(min)', 'Festival'])

# Filtrar para considerar apenas os dados dos festivais
              df_festival = df[df['Festival'] == True]

# Verificar se o DataFrame não está vazio antes de calcular o tempo médio
              if not df_festival.empty:
                  tempo_medio_festival = df_festival['Time_taken(min)'].mean()
              else:
                 tempo_medio_festival = 0  # Valor padrão caso o DataFrame esteja vazio

# Exibir o tempo médio de entrega durante os festivais
              col3.metric('Tempo Médio de Entrega Durante os Festivais', f"{tempo_medio_festival:.2f}")
 
          
              
         with col4:
              st.title('seila')
              # Garantir que a coluna 'Time_taken(min)' seja numérica
              df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')

# Remover valores nulos nas colunas necessárias
              df = df.dropna(subset=['Time_taken(min)', 'Festival'])

# Filtrar para considerar apenas os dados dos festivais
              df_festival = df[df['Festival'] == True]

# Verificar se o DataFrame não está vazio antes de calcular o desvio padrão
              if not df_festival.empty:
                 desvio_padrao_festival = df_festival['Time_taken(min)'].std()
              else:
                 desvio_padrao_festival = 0  # Valor padrão caso o DataFrame esteja vazio

# Exibir o desvio padrão de entrega durante os festivais
              col4.metric('Desvio Padrão de Entrega Durante os Festivais', f"{desvio_padrao_festival:.2f}")


         with col5:
              st.title('seila')
              # Garantir que a coluna 'Time_taken(min)' seja numérica
              df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')

# Remover valores nulos nas colunas necessárias
              df = df.dropna(subset=['Time_taken(min)', 'Festival'])

# Filtrar para considerar os dados fora dos festivais
              df_sem_festival = df[df['Festival'] == False]

# Verificar se o DataFrame não está vazio antes de calcular o tempo médio
              if not df_sem_festival.empty:
                   tempo_medio_sem_festival = df_sem_festival['Time_taken(min)'].mean()
              else:
                   tempo_medio_sem_festival = 0  # Valor padrão caso o DataFrame esteja vazio

# Exibir o tempo médio de entrega sem festivais
              col5.metric('Tempo Médio de Entrega Sem Festival', f"{tempo_medio_sem_festival:.2f}")

         with col6:
              st.title('seila')
              # Garantir que a coluna 'Time_taken(min)' seja numérica
              df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')

# Remover valores nulos nas colunas necessárias
              df = df.dropna(subset=['Time_taken(min)', 'Festival'])

# Filtrar para considerar os dados fora dos festivais
              df_sem_festival = df[df['Festival'] == False]

# Verificar se o DataFrame não está vazio antes de calcular o desvio padrão
              if not df_sem_festival.empty:
                       desvio_padrao_sem_festival = df_sem_festival['Time_taken(min)'].std()
              else:
                       desvio_padrao_sem_festival = 0  # Valor padrão caso o DataFrame esteja vazio

# Exibir o desvio padrão de entrega sem festivais
              col6.metric('Desvio Padrão de Entrega Sem Festival', f"{desvio_padrao_sem_festival:.2f}")


         
     with st.container():
        st.title('Tempo Medio de entregas por cidade')
        
        
        
        
        df_aux = df.groupby('City').agg(avg_time=('Time_taken(min)', 'mean'), std_time=('Time_taken(min)', 'std')).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))

# Plotando o gráfico de intervalo
        ax.errorbar(x=df_aux['City'], y=df_aux['avg_time'], yerr=df_aux['std_time'], fmt='o', capsize=5, capthick=2, color='b', ecolor='r')

# Configurações do gráfico
        ax.set_xlabel('Cidade')
        ax.set_ylabel('Tempo Médio de Entrega (min)')
        ax.set_title('Tempo Médio e Desvio Padrão de Entrega por Cidade')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
             # Rotaciona os rótulos do eixo X para evitar sobreposição
        plt.xticks(rotation=45)
        st.pyplot(fig)
         



        
         
     with st.container():
         st.title('Distribuição do Tempo')
         
         col1,col2 = st.columns (2)
         with col1:
             df.rename(columns={
               'delivery_location_latitude': 'Delivery_location_latitude',
               'delivery_location_longitude': 'Delivery_location_longitude',
               'restaurant_latitude': 'Restaurant_latitude',
               'restaurant_longitude': 'Restaurant_longitude'
        }, inplace=True)

# Garantir que a coluna 'Time_taken(min)' seja numérica
             df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')

# Remover valores nulos nas colunas relevantes
             df = df.dropna(subset=['Time_taken(min)', 'City'])

# Calcular o tempo médio de entrega por cidade
             tempo_medio = df.groupby('City')['Time_taken(min)'].mean()

# Criar o gráfico de pizza para o tempo médio de entrega por cidade
             fig, ax = plt.subplots(figsize=(8, 8))

# Gráfico de pizza
             ax.pie(tempo_medio, labels=tempo_medio.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
             ax.set_title('Tempo Médio de Entrega por Cidade')

# Exibir o gráfico no Streamlit
             st.pyplot(fig)
             
             

          

         with col2:
             # Criando df_aux com tempo médio de entrega por cidade e tipo de tráfego
            df_aux = df.groupby(['City', 'Road_traffic_density']).agg(avg_time=('Time_taken(min)', 'mean')).reset_index()

# Criando o gráfico Sunburst
            fig = px.sunburst(df_aux, 
                  path=['City', 'Road_traffic_density'], 
                  values='avg_time',
                  color='avg_time',
                  color_continuous_scale='Blues',
                  title='Tempo Médio de Entrega por Cidade e Tipo de Tráfego')

# Exibir no Streamlit
            st.plotly_chart(fig)
            



         
     with st.container():
         st.title('Distribuição da Distancia')
         # Criando df_aux com tempo médio e desvio padrão de entrega por cidade e tipo de pedido
         df_aux = df.groupby(['City', 'Type_of_order']).agg(
         avg_time=('Time_taken(min)', 'mean'),
         std_time=('Time_taken(min)', 'std')
         ).reset_index()

# Exibindo a tabela no Streamlit
         st.dataframe(df_aux)
    
    