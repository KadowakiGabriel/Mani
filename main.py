import streamlit as st
from streamlit import session_state as state
import pandas as pd
import gspread
import matplotlib.pyplot as plt
from gspread_dataframe import get_as_dataframe
from streamlit_option_menu import option_menu 
from datetime import datetime
import seaborn as sns


# Ler várias planilhas do Google Sheets e concatenar os dados sem autenticação
import pandas as pd

sheet_id = '15EkENz-7Qvyr0-R_GRb-msa0GGMhTr6RNHLaoru-Xok'
gids = ['1985436030', '2109471434', '1025635223', '768884832', '594542402']  # Substitua pelos GIDs reais das abas '04', '05', '06', '07', '08'

# 


dfs = []
dfs2 = []
for gid in gids:
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    df = pd.read_csv(url)
    # fazer uma cópia do DataFrame usar para a parte de INSIGHTS de produtos
    df2 = df.copy()
    # excluir as colunas que não são necessárias
    df = df.drop(df.columns[[1, 2, 4, 5,6,7,8,9,10,11,12]], axis=1)
    # excluir a primeira linha de cada aba
    df = df.iloc[1:]
    # excluir a linha de index
    df.reset_index(drop=True, inplace=True)
    dfs.append(df)
    dfs2.append(df2)
# criar uma tabela com os dados dos clientes
clientes = dfs

# Parte de limpeza e transformação dos dados para NÚMERO DE PEDIDOS
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



# Parte de visualização dos dados com Streamlit
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



# Dados para INSIGHTS de produtos
# concatenar todos os DataFrames em um único DataFrame
df_final2 = pd.concat(dfs2, ignore_index=True)
# excluir a coluna as colunas 2, 4, 5, 6, 7, 8, 9, 10, 11, 12
df_final2 = df_final2.drop(df_final2.columns[[1, 5, 7, 8, 10, 11, 12, 13]], axis=1)
# excluir a primeira linha
df_final2 = df_final2.iloc[1:]
# excluir a linha de index
df_final2.reset_index(drop=True, inplace=True)
# setar o nome das coluna
df_final2.columns = ['Data', 'Produto', 'Cliente', 'Valor', 'Metodo de Entrega', 'Taxa de Entrega']
# excluir as linhas que tem o valor 'nan' na coluna 'Cliente'
df_final2 = df_final2[df_final2['Cliente'].notna()]
# remover espaços extras no início e no final dos nomes dos clientes
df_final2['Cliente'] = df_final2['Cliente'].str.strip()
# transformar em lower case a coluna 'Cliente'
df_final2['Cliente'] = df_final2['Cliente'].str.lower()
# trocar todos os nomes 'fábia' por 'fabia'
df_final2['Cliente'] = df_final2['Cliente'].replace('fábia', 'fabia')
# trocar todos os nomes 'júlia' por 'julia'
df_final2['Cliente'] = df_final2['Cliente'].replace('júlia', 'julia')
# trocar todos os nomes 'marluci' por 'mariluci'
df_final2['Cliente'] = df_final2['Cliente'].replace('marluci', 'mariluci')
# excluir a primeira linha 
df_final2 = df_final2.iloc[1:]
# remover espaços extras no início e no final dos nomes dos produtos
df_final2['Produto'] = df_final2['Produto'].str.strip()
# transformar em lower case a coluna 'Produto'
df_final2['Produto'] = df_final2['Produto'].str.lower()
# trocar por 0 os valores 'nan' na coluna 'Taxa de Entrega'
df_final2['Taxa de Entrega'] = df_final2['Taxa de Entrega'].fillna(0)
# replace 'R$' por '' na coluna 'Valor'
df_final2['Valor'] = df_final2['Valor'].str.replace('R$', '', regex=True)
# replace ',' por '.' na coluna 'Valor'
df_final2['Valor'] = df_final2['Valor'].str.replace(',', '.', regex=True)
# strip os espaços extras no início e no final dos valores da coluna 'Valor'
df_final2['Valor'] = df_final2['Valor'].str.strip()
# replace 'R$' por '' na coluna 'Taxa de Entrega'
df_final2['Taxa de Entrega'] = df_final2['Taxa de Entrega'].str.replace('R$', '', regex=True)
# replace ',' por '.' na coluna 'Taxa de Entrega'
df_final2['Taxa de Entrega'] = df_final2['Taxa de Entrega'].str.replace(',', '.', regex=True)
# strip os espaços extras no início e no final dos valores da coluna 'Taxa de Entrega'
df_final2['Taxa de Entrega'] = df_final2['Taxa de Entrega'].str.strip()
# substituir os valores '-' na coluna 'Taxa de Entrega' e na coluna 'Valor' por 0
df_final2['Taxa de Entrega'] = df_final2['Taxa de Entrega'].replace('-', '0', regex=True)
df_final2['Valor'] = df_final2['Valor'].replace('-', '0', regex=True)
# printar todos os valores da coluna 'Valor' que não são numéricos
df_final2['Valor'] = pd.to_numeric(df_final2['Valor'], errors='coerce')  # converter a coluna 'Valor' para numérico, substituindo erros por NaN
df_final2['Taxa de Entrega'] = pd.to_numeric(df_final2['Taxa de Entrega'], errors='coerce')  # converter a coluna 'Taxa de Entrega' para numérico, substituindo erros por NaN
df_final2['Valor'] = df_final2['Valor'].fillna(0)  # substituir NaN por 0 na coluna 'Valor'
df_final2['Taxa de Entrega'] = df_final2['Taxa de Entrega'].fillna(0)  # substituir NaN por 0 na coluna 'Taxa de Entrega'   
# reiniciar o índice do DataFrame
df_final2.reset_index(drop=True, inplace=True)
# transformar a coluna 'Data' para o formato datetime em 'DD/MM/AAAA'
df_final2['Data'] = pd.to_datetime(df_final2['Data'], format='%d/%m/%Y', errors='coerce')



# criar kpi's para a parte de INSIGHTS de produtos
# kpi de total de vendas
total_vendas = df_final2['Valor'].sum()
# kpi de total de taxa de entrega
total_taxa_entrega = df_final2['Taxa de Entrega'].sum()
# kpi de total de pedidos
total_pedidos = df_final2.shape[0]
# kpi de total de produtos vendidos
total_produtos_vendidos = df_final2['Produto'].nunique()   
# kpi de total de clientes
total_clientes = df_final2['Cliente'].nunique()
# kpi de total de produtos vendidos por cliente
produtos_por_cliente = df_final2.groupby('Cliente')['Produto'].nunique().reset_index(name='Produtos Vendidos')
produtos_por_cliente = produtos_por_cliente.sort_values(by='Produtos Vendidos', ascending=False)
# kpi de total de produtos vendidos por dia
produtos_por_dia = df_final2.groupby('Data')['Produto'].nunique().reset_index(name='Produtos Vendidos')
produtos_por_dia = produtos_por_dia.sort_values(by='Produtos Vendidos', ascending=False)   
# kpi de total de vendas por produto
vendas_por_produto = df_final2.groupby('Produto')['Valor'].sum().reset_index(name='Total de Vendas')
vendas_por_produto = vendas_por_produto.sort_values(by='Total de Vendas', ascending=False)
# kpi de total de taxa de entrega por produto
taxa_entrega_por_produto = df_final2.groupby('Produto')['Taxa de Entrega'].sum().reset_index(name='Total de Taxa de Entrega')
taxa_entrega_por_produto = taxa_entrega_por_produto.sort_values(by='Total de Taxa de Entrega', ascending=False)    
# kpi de total de vendas por cliente
vendas_por_cliente = df_final2.groupby('Cliente')['Valor'].sum().reset_index(name='Total de Vendas')
vendas_por_cliente = vendas_por_cliente.sort_values(by='Total de Vendas', ascending=False)
# kpi de total de taxa de entrega por cliente
taxa_entrega_por_cliente = df_final2.groupby('Cliente')['Taxa de Entrega'].sum().reset_index(name='Total de Taxa de Entrega')
taxa_entrega_por_cliente = taxa_entrega_por_cliente.sort_values(by='Total de Taxa de Entrega', ascending=False) 
# kpi de total de vendas por dia
vendas_por_dia = df_final2.groupby('Data')['Valor'].sum().reset_index(name='Total de Vendas')
vendas_por_dia = vendas_por_dia.sort_values(by='Total de Vendas', ascending=False)
# kpi de total de taxa de entrega por dia
taxa_entrega_por_dia = df_final2.groupby('Data')['Taxa de Entrega'].sum().reset_index(name='Total de Taxa de Entrega')
taxa_entrega_por_dia = taxa_entrega_por_dia.sort_values(by='Total de Taxa de Entrega', ascending=False)
# kpi de total de pedidos por produto
pedidos_por_produto = df_final2.groupby('Produto')['Cliente'].count().reset_index(name='Total de Pedidos')
pedidos_por_produto = pedidos_por_produto.sort_values(by='Total de Pedidos', ascending=False)
# kpi de total de pedidos por cliente
pedidos_por_cliente = df_final2.groupby('Cliente')['Produto'].count().reset_index(name='Total de Pedidos')
pedidos_por_cliente = pedidos_por_cliente.sort_values(by='Total de Pedidos', ascending=False)
# kpi de total de pedidos por dia
pedidos_por_dia = df_final2.groupby('Data')['Produto'].count().reset_index(name='Total de Pedidos')
pedidos_por_dia = pedidos_por_dia.sort_values(by='Total de Pedidos', ascending=False)   
# kpi de total de produtos vendidos por método de entrega
produtos_por_metodo_entrega = df_final2.groupby('Metodo de Entrega')['Produto'].nunique().reset_index(name='Produtos Vendidos')
produtos_por_metodo_entrega = produtos_por_metodo_entrega.sort_values(by='Produtos Vendidos', ascending=False)
# kpi de total de vendas por método de entrega
vendas_por_metodo_entrega = df_final2.groupby('Metodo de Entrega')['Valor'].sum().reset_index(name='Total de Vendas')
vendas_por_metodo_entrega = vendas_por_metodo_entrega.sort_values(by='Total de Vendas', ascending=False)

# ticket médio
ticket_medio = total_vendas / total_pedidos if total_pedidos > 0 else 0
print(f"Ticket médio: {ticket_medio:.2f} R$")
# crescimento de vendas
# plotar o crescimento de vendas
vendas_por_dia['Crescimento'] = vendas_por_dia['Total de Vendas'].pct_change().fillna(0) * 100
vendas_por_dia['Crescimento'] = vendas_por_dia['Crescimento'].round(2)
# plotar o crescimento de pedidos com data em datetime
vendas_por_dia['Data'] = pd.to_datetime(vendas_por_dia['Data'], format='%d/%m/%Y', errors='coerce')
plt.figure(figsize=(10, 5))
sns.lineplot(data=vendas_por_dia, x='Data', y='Crescimento', marker='o')
plt.title('Crescimento de Vendas ao Longo do Tempo')
plt.xlabel('Data')
plt.ylabel('Crescimento (%)')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
st.pyplot(plt.gcf())  # Exibir o gráfico no Streamlit
# printar os kpi's
st.write(f"Total de Vendas: {total_vendas:.2f} R$")
st.write(f"Total de Taxa de Entrega: {total_taxa_entrega:.2f} R$")
st.write(f"Total de Pedidos: {total_pedidos}")
st.write(f"Total de Produtos Vendidos: {total_produtos_vendidos}")
st.write(f"Total de Clientes: {total_clientes}")
st.write(f"Ticket Médio: {ticket_medio:.2f} R$")
# plotar o total de vendas por produto
plt.figure(figsize=(10, 5))
sns.barplot(data=vendas_por_produto, x='Produto', y='Total de Vendas')
plt.title('Total de Vendas por Produto')
plt.xlabel('Produto')
plt.ylabel('Total de Vendas (R$)')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
st.pyplot(plt.gcf())  # Exibir o gráfico no Streamlit
# plotar o total de taxa de entrega por produto
plt.figure(figsize=(10, 5))
sns.barplot(data=taxa_entrega_por_produto, x='Produto', y='Total de Taxa de Entrega')
plt.title('Total de Taxa de Entrega por Produto')
plt.xlabel('Produto')
plt.ylabel('Total de Taxa de Entrega (R$)')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()         
