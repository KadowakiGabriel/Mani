import streamlit as st
from streamlit import session_state as state
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe
from streamlit_option_menu import option_menu 
from datetime import datetime

# Ler várias planilhas do Google Sheets e concatenar os dados sem autenticação
import pandas as pd

sheet_id = '15EkENz-7Qvyr0-R_GRb-msa0GGMhTr6RNHLaoru-Xok'
gids = ['1985436030', '2109471434', '1025635223', '768884832', '594542402']  # Substitua pelos GIDs reais das abas '04', '05', '06', '07', '08'

# 


dfs = []
for gid in gids:
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    df = pd.read_csv(url)
    # excluir a coluna 3, 4, 6 e 7
    df = df.drop(df.columns[[1, 2, 4, 5,6,7,8,9,10,11,12]], axis=1)
    # excluir a primeira linha de cada aba
    df = df.iloc[1:]
    # excluir a linha de index
    df.reset_index(drop=True, inplace=True)
    dfs.append(df)
# criar uma tabela com os dados dos clientes
clientes = dfs

# Concatenar todos os DataFrames em um único DataFrame
df_final = pd.concat(dfs, ignore_index=True)
# excluir a coluna 'Unnamed: 13'
df_final = df_final.drop(columns=['Unnamed: 13'], errors='ignore')
# setar o nome das colunas
df_final.columns = ['Data', 'Cliente']
# excluir as linhas que tem o valor 'nan' na coluna 'Cliente'
df_final = df_final[df_final['Cliente'].notna()]
# excluir as linhas que tem o valor 'nan' na coluna 'Data'
df_final = df_final[df_final['Data'].notna()]
# excluir a primeira linha
df_final = df_final.iloc[1:]
# transformar em lower case a coluna 'Cliente'
df_final['Cliente'] = df_final['Cliente'].str.lower()
# trocar todos os nomes 'fábia' por 'fabia'
df_final['Cliente'] = df_final['Cliente'].replace('fábia', 'fabia')
# trocar todos os nomes 'júlia' por 'julia'
df_final['Cliente'] = df_final['Cliente'].replace('júlia', 'julia')
# trocar todos os nomes 'marluci' por 'mariluci'
df_final['Cliente'] = df_final['Cliente'].replace('marluci', 'mariluci')

# remover espaços extras no início e no final dos nomes dos clientes
df_final['Cliente'] = df_final['Cliente'].str.strip()
# Contar quantos pedidos cada cliente fez em cada data
pedidos_por_cliente_data = (
    df_final.groupby(['Data', 'Cliente'])
    .size()
    .reset_index(name='Pedidos')
)
# filtrar os pedidos por cliente e data
pedidos_por_cliente_data = pedidos_por_cliente_data[pedidos_por_cliente_data['Pedidos'] > 0]   
# lista de quantos dias diferentes cada cliente fez pedidos, por exemplo, se o cliente 'joão' fez pedidos em 3 dias diferentes, quero que apareça 'joão' e '3'
pedidos_por_cliente = (
    df_final.groupby('Cliente')['Data']
    .nunique()
    .reset_index(name='Dias_de_pedido')
)
#Colocar a primeira letra de cada nome de cliente em maiúscula
pedidos_por_cliente['Cliente'] = pedidos_por_cliente['Cliente'].str.title()
# sortear a tabela de pedidos por cliente por quem mais fez pedidos
pedidos_por_cliente = pedidos_por_cliente.sort_values(by='Dias_de_pedido', ascending=False)
# abrindo o menu cliente
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["Início", "Clientes", "Financeiro", "Pedidos"],
        icons=["house", "person-badge-fill", "cash-coin", "person-raised-hand"],
        menu_icon="cast",
        default_index=1,
    )
if selected == "Início":
    st.title(f"Página {selected}")
if selected == "Clientes":
    st.title(f"Página {selected}")
    st.write("Lista de clientes:")
    st.dataframe(pedidos_por_cliente)
    # criar um filtro para o nome do cliente
    cliente = st.selectbox("Selecione um cliente para saber seu último pedido:", pedidos_por_cliente['Cliente'].unique())
    # mostrar o ultimo pedido do cliente
    ultimo_pedido = df_final[df_final['Cliente'] == cliente.lower()]['Data'].max()
    st.write(f"O último pedido do cliente {cliente} foi em {ultimo_pedido}.")
    # calcular a data de hoje menos o último pedido do cliente usando o formato 'DD/MM/AAAA'
    hoje = datetime.now()
    ultimo_pedido_date = datetime.strptime(ultimo_pedido, '%d/%m/%Y')
    dias_desde_ultimo_pedido = (hoje - ultimo_pedido_date).days
    st.write(f"Já se passaram {dias_desde_ultimo_pedido} dias desde o último pedido do cliente {cliente}.")
    # mostrar o número de pedidos que o cliente fez

    # mostrar o número de dias diferentes que o cliente fez pedidos
    dias_de_pedido = pedidos_por_cliente[pedidos_por_cliente['Cliente'] == cliente]['Dias_de_pedido'].values[0]
if selected == "Redes Sociais":
    st.title(f"Página {selected}")
    st.write("Página de Redes Sociais em construção.")
if selected == "Pedidos":   
    st.title(f"Página {selected}")
    st.write("Página de pedidos em construção.")
    # mostrar a tabela de pedidos por cliente e data
    st.dataframe(pedidos_por_cliente_data)
    # criar um filtro para a data
    data = st.selectbox("Selecione uma data:", pedidos_por_cliente_data['Data'].unique())
    # filtrar os pedidos da data selecionada
    pedidos_data = pedidos_por_cliente_data[pedidos_por_cliente_data['Data'] == data]
    st.write(f"Pedidos na data {data}:")
    st.dataframe(pedidos_data)
