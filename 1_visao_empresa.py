#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go  # Corrigido
import pandas as pd
import re
import streamlit as st
import datetime  # ✅ Importe o módulo datetime
from PIL import Image


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
st.header('Marketplace - Visão Cliente')

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática','Visão Geografica' ] )

with tab1:
    with st.container():
       st.markdown('# Orders by day')
       cols = ['ID', 'Order_Date']
    
       # Criando df_aux corretamente
       df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()
       df_aux.rename(columns={'Order_Date': 'order_date', 'ID': 'qtde_entregas'}, inplace=True)

       # Print para depuração
       print(df_aux.columns)  # Isso mostrará os nomes reais das colunas

       # Criando o gráfico
       fig = px.bar(df_aux, x='order_date', y='qtde_entregas')
 
       # Exibindo no Streamlit
       st.plotly_chart(fig, use_container_width=True)
    
    
    with st.container():
       col1, col2 = st.columns( 2 )
       with col1:
           st.header('Traffic Order Share')
           columns = ['ID', 'Road_traffic_density']
           df_aux = df.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()
           df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
           # gráfico
           fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
           st.plotly_chart(fig, use_container_width=True)
       
       with col2:
           st.header('Traffic Order City')
           columns = ['ID', 'City', 'Road_traffic_density']
           df_aux = df.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
           df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
             # gráfico
           fig = px.bar( df_aux, x='City', y='ID', color='Road_traffic_density', barmode='group')
           st.plotly_chart(fig, use_container_width=True)
           
with tab2:
  with st.container():  
    st.markdown('# Order by week')
    # Quantidade de pedidos por Semana
    df['week_of_year'] = df['Order_Date'].dt.strftime( "%U" )
    df_aux = df.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    # gráfico
    fig = px.bar( df_aux, x='week_of_year', y='ID' )
    st.plotly_chart(fig, use_container_width=True)
    
  with st.container():
    st.markdown('# Order Share week')
     # Quantidade de pedidos por entregador por Semana
    # Quantas entregas na semana / Quantos entregadores únicos por semana
    df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    st.plotly_chart(fig, use_container_width=True)
    
with tab3:
    st.header('Coutry maps')
     
    # Removendo espaços extras nos nomes das colunas
    df.columns = df.columns.str.strip()

    columns = [
       'City',
       'Road_traffic_density',
        'Delivery_location_latitude',  # Removido o espaço extra
        'Delivery_location_longitude'
          ]
    columns_groupby = ['City', 'Road_traffic_density']

    # Agrupar e calcular a mediana
    data_plot = df.loc[:, columns].groupby(columns_groupby).median().reset_index()

    # Filtrar valores NaN corretamente
    data_plot = data_plot.dropna(subset=['City', 'Road_traffic_density'])

    # Criar o mapa
    import folium

    map_ = folium.Map(zoom_start=11)
    for index, location_info in data_plot.iterrows():
        folium.Marker(
        [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
        popup=f"{location_info['City']} - {location_info['Road_traffic_density']}"
        ).add_to(map_)

    map_

    
    
    

    
    
#print('Estou aqui!')

