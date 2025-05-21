import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# --- CARREGAMENTO E UNIFICAÇÃO DOS DADOS ---
# Carregar bases de vendas
df_vendas_2020 = pd.read_csv('./data/Base Vendas - 2020.csv', sep=";")
df_vendas_2021 = pd.read_csv('./data/Base Vendas - 2021.csv', sep=";")
df_vendas_2022 = pd.read_csv('./data/Base Vendas - 2022.csv', sep=";")

# Carregar bases de cadastro
df_produtos = pd.read_csv('./data/Cadastro Produtos.csv', sep=";")
df_lojas = pd.read_csv('./data/Cadastro Lojas.csv', sep=";")
df_clientes = pd.read_csv('./data/Cadastro Clientes.csv', sep=";")

# Unificar tabelas de vendas
df_vendas_unificado = pd.concat([df_vendas_2020, df_vendas_2021, df_vendas_2022], ignore_index=True)

# Renomear colunas para padronização
df_vendas_unificado = df_vendas_unificado.rename(columns={
    'Data da Venda': 'Data Venda',
    'SKU': 'ID Produto',
    'Qtd Vendida': 'Quantidade'
})

df_produtos = df_produtos.rename(columns={
    'SKU': 'ID Produto',
    'Tipo do Produto': 'Tipo de Produto',
    'Preço Unitario': 'Preco Unitario Produto',
    'Produto': 'Nome Produto'
})

df_lojas = df_lojas.rename(columns={
    'Nome da Loja': 'Nome Loja'
})

# Unificar colunas de nome do cliente
df_clientes['Nome Cliente'] = df_clientes['Primeiro Nome'] + ' ' + df_clientes['Sobrenome']

# Converter 'Data Venda' para datetime e extrair ano
df_vendas_unificado['Data Venda'] = pd.to_datetime(df_vendas_unificado['Data Venda'], dayfirst=True)
df_vendas_unificado['Ano Venda'] = df_vendas_unificado['Data Venda'].dt.year

# Realizar merges para criar o DataFrame principal
df_merged = pd.merge(df_vendas_unificado, df_produtos, on='ID Produto', how='left')
df_merged = pd.merge(df_merged, df_lojas, on='ID Loja', how='left')
df_merged = pd.merge(df_merged, df_clientes, on='ID Cliente', how='left')

# Calcular 'Valor Total'
df_merged['Valor Total'] = df_merged['Quantidade'] * df_merged['Preco Unitario Produto']

# Remover colunas duplicadas
df_merged = df_merged.loc[:,~df_merged.columns.duplicated()]

# --- INICIALIZAÇÃO DO DASH APP | LAYOUT DO DASHBOARD ---
app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': '#1a1a1a', 'color': '#f0f0f0', 'fontFamily': 'Arial, sans-serif', 'padding': '30px'}, children=[
    
    html.H1("Dashboard de Vendas", style={'textAlign': 'center', 'color': '#ffffff', 'paddingTop': '20px'}),

    html.Div([
        html.Div([
            html.Label("Filtrar por Produto:"),
            dcc.Dropdown(
                id='dropdown-produto',
                options=[{'label': i, 'value': i} for i in df_merged['Nome Produto'].unique()],
                multi=True,
                placeholder="Selecione um Produto",
                style={'backgroundColor': '#333333', 'color': '#f0f0f0', 'marginTop': '2%'},
                className='dark-dropdown'
            )
        ], style={'width': '24%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '1%', 'marginBottom': '1%'}),

        html.Div([
            html.Label("Filtrar por Loja:"),
            dcc.Dropdown(
                id='dropdown-loja',
                options=[{'label': i, 'value': i} for i in df_merged['Nome Loja'].unique()],
                multi=True,
                placeholder="Selecione uma Loja",
                style={'backgroundColor': '#333333', 'color': '#f0f0f0', 'marginTop': '2%'},
                className='dark-dropdown'
            )
        ], style={'width': '24%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '1%', 'marginBottom': '1%'}),

        html.Div([
            html.Label("Filtrar por Cliente:"),
            dcc.Dropdown(
                id='dropdown-cliente',
                options=[{'label': i, 'value': i} for i in df_merged['Nome Cliente'].unique()],
                multi=True,
                placeholder="Selecione um Cliente",
                style={'backgroundColor': '#333333', 'color': '#f0f0f0', 'marginTop': '2%'},
                className='dark-dropdown'
            )
        ], style={'width': '24%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '1%', 'marginBottom': '1%'}),

        html.Div([
            html.Label("Filtrar por Tipo de Produto:"),
            dcc.Dropdown(
                id='dropdown-tipo-produto',
                options=[{'label': i, 'value': i} for i in df_merged['Tipo de Produto'].unique()],
                multi=False,
                placeholder="Selecione um Tipo",
                style={'backgroundColor': '#333333', 'color': '#f0f0f0', 'marginTop': '2%'},
                className='dark-dropdown'
            )
        ], style={'width': '24%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginBottom': '1%'}),

        html.Div([
            html.Label("Filtrar por Marca (dependente do Tipo de Produto):"),
            dcc.Dropdown(
                id='dropdown-marca',
                multi=True,
                placeholder="Selecione uma Marca",
                style={'backgroundColor': '#333333', 'color': '#f0f0f0', 'marginTop': '2%'},
                className='dark-dropdown'
            )
        ], style={'width': '24%', 'display': 'inline-block', 'verticalAlign': 'top'}),


    ], style={'padding': '20px', 'backgroundColor': '#2a2a2a', 'borderRadius': '8px', 'margin': '20px'}),


    html.Div([
        html.Div(dcc.Graph(id='graph-vendas-ano'), className='six columns', style={'display': 'inline-block', 'width': '49%'}),
        html.Div(dcc.Graph(id='graph-vendas-loja'), className='six columns', style={'display': 'inline-block', 'width': '49%'})
    ], style={'padding': '10px'}),

    html.Div([
        html.Div(dcc.Graph(id='graph-vendas-produto'), className='six columns', style={'display': 'inline-block', 'width': '49%'}),
        html.Div(dcc.Graph(id='graph-vendas-tipo-produto'), className='six columns', style={'display': 'inline-block', 'width': '49%'})
    ], style={'padding': '10px'}),

    html.Div([
        html.Div(dcc.Graph(id='graph-vendas-marca'), className='six columns', style={'display': 'inline-block', 'width': '49%'}),
        html.Div(html.Div(id='table-vendas-cliente-container'), className='six columns', style={'display': 'inline-block', 'width': '49%', 'verticalAlign': 'top', 'paddingTop': '20px'})
    ], style={'padding': '10px'})
])

# --- CALLBACKS PARA DINAMISMO ---

# Callback para filtro cascata de Marca
@app.callback(
    Output('dropdown-marca', 'options'),
    Input('dropdown-tipo-produto', 'value')
)
def set_marcas_options(selected_tipo_produto):
    if selected_tipo_produto:
        filtered_df = df_merged[df_merged['Tipo de Produto'] == selected_tipo_produto]
        marcas = sorted(filtered_df['Marca'].unique())
        return [{'label': i, 'value': i} for i in marcas]
    return []

# Callback principal para atualizar todos os gráficos
@app.callback(
    Output('graph-vendas-ano', 'figure'),
    Output('graph-vendas-loja', 'figure'),
    Output('graph-vendas-produto', 'figure'),
    Output('table-vendas-cliente-container', 'children'),
    Output('graph-vendas-tipo-produto', 'figure'),
    Output('graph-vendas-marca', 'figure'),
    Input('dropdown-produto', 'value'),
    Input('dropdown-loja', 'value'),
    Input('dropdown-cliente', 'value'),
    Input('dropdown-tipo-produto', 'value'),
    Input('dropdown-marca', 'value')
)
def update_graphs(selected_produtos, selected_lojas, selected_clientes, selected_tipo_produto, selected_marcas):
    df_filtered = df_merged.copy()

    # Aplica os filtros
    if selected_produtos:
        df_filtered = df_filtered[df_filtered['Nome Produto'].isin(selected_produtos)]
    if selected_lojas:
        df_filtered = df_filtered[df_filtered['Nome Loja'].isin(selected_lojas)]
    if selected_clientes:
        df_filtered = df_filtered[df_filtered['Nome Cliente'].isin(selected_clientes)]
    if selected_tipo_produto:
        df_filtered = df_filtered[df_filtered['Tipo de Produto'] == selected_tipo_produto]
    if selected_marcas:
        df_filtered = df_filtered[df_filtered['Marca'].isin(selected_marcas)]

    # Mensagem de "Sem dados" se o DataFrame filtrado estiver vazio
    if df_filtered.empty:
        empty_figure = go.Figure().update_layout(
            plot_bgcolor='#222222', paper_bgcolor='#1a1a1a', font_color='#f0f0f0',
            title='Sem dados para exibir com os filtros selecionados', title_x=0.5
        )
        empty_table = html.Div(
            html.P("Sem dados de cliente para exibir com os filtros selecionados.",
                   style={'textAlign': 'center', 'color': '#f0f0f0', 'marginTop': '50px', 'fontSize': '1.2em'}),
            style={'backgroundColor': '#222222', 'padding': '20px', 'borderRadius': '8px', 'height': '400px'}
        )
        return empty_figure, empty_figure, empty_figure, empty_table, empty_figure, empty_figure

    # Função para aplicar estilo dark mode aos gráficos
    def create_dark_mode_figure(fig, title_text):
        fig.update_layout(
            title=title_text,
            title_x=0.5,
            plot_bgcolor='#222222',
            paper_bgcolor='#1a1a1a',
            font=dict(color='#f0f0f0'),
            title_font_color='#ffffff',
            xaxis=dict(showgrid=False, zeroline=False, tickangle=45, color='#f0f0f0', linecolor='#444444'),
            yaxis=dict(showgrid=True, gridcolor='#444444', zeroline=False, color='#f0f0f0', linecolor='#444444'),
            margin=dict(l=40, r=40, t=80, b=40),
            hovermode="x unified"
        )
        return fig

    # 1. Gráfico: Venda por Ano (Line Chart)
    # Exibe a tendência das vendas ao longo dos anos.
    vendas_por_ano = df_filtered.groupby('Ano Venda')['Valor Total'].sum().reset_index()
    fig_ano = go.Figure(data=go.Scatter(x=vendas_por_ano['Ano Venda'],
                                         y=vendas_por_ano['Valor Total'],
                                         mode='lines+markers',
                                         marker=dict(color='#00cc96'),
                                         line=dict(color='#636efa', width=3)
                                        ))
    fig_ano = create_dark_mode_figure(fig_ano, 'Vendas Totais por Ano')
    fig_ano.update_xaxes(rangeselector_bgcolor='#333333',
                         rangeselector_font_color='#f0f0f0',
                         rangeslider_visible=True,
                         rangeslider_thickness=0.07,
                         rangeslider_bgcolor='#333333',
                         title_text='Ano')
    fig_ano.update_yaxes(title_text='Valor Total de Vendas (R$)')

    # 2. Gráfico: Venda por Loja (Horizontal Bar Chart)
    # Compara o desempenho de vendas entre as diferentes lojas.
    vendas_por_loja = df_filtered.groupby('Nome Loja')['Valor Total'].sum().reset_index().sort_values(by='Valor Total', ascending=True)
    fig_loja = go.Figure(data=go.Bar(x=vendas_por_loja['Valor Total'],
                                      y=vendas_por_loja['Nome Loja'],
                                      orientation='h',
                                      marker_color='#636efa'
                                     ))
    fig_loja = create_dark_mode_figure(fig_loja, 'Vendas Totais por Loja')
    fig_loja.update_layout(yaxis=dict(showgrid=False, zeroline=False, color='#f0f0f0', linecolor='#444444'))
    fig_loja.update_xaxes(title_text='Valor Total de Vendas (R$)')
    fig_loja.update_yaxes(title_text='Loja')

    # 3. Gráfico: Venda por Produto (Vertical Bar Chart - Top 10 Produtos)
    # Destaca os produtos que geram maior receita.
    vendas_por_produto = df_filtered.groupby('Nome Produto')['Valor Total'].sum().reset_index().sort_values(by='Valor Total', ascending=False).head(10)
    fig_produto = go.Figure(data=go.Bar(x=vendas_por_produto['Nome Produto'],
                                         y=vendas_por_produto['Valor Total'],
                                         marker_color='#00cc96'
                                        ))
    fig_produto = create_dark_mode_figure(fig_produto, 'Top 10 Produtos por Vendas Totais')
    fig_produto.update_layout(xaxis=dict(tickangle=45, automargin=True))
    fig_produto.update_xaxes(title_text='Produto')
    fig_produto.update_yaxes(title_text='Valor Total de Vendas (R$)')

    # 4. Tabela: Venda por Cliente (Top 10 Clientes por Vendas Totais)
    # Lista os clientes que mais contribuíram para as vendas.
    vendas_por_cliente = df_filtered.groupby('Nome Cliente')['Valor Total'].sum().reset_index().sort_values(by='Valor Total', ascending=False).head(10)
    table_cliente = html.Div([
        html.H3("Top 10 Clientes por Vendas Totais", style={'textAlign': 'center', 'color': '#ffffff'}),
        html.Table([
            html.Thead(
                html.Tr([html.Th('Cliente', style={'padding': '8px', 'backgroundColor': '#444444', 'color': '#ffffff', 'textAlign': 'left'}),
                         html.Th('Valor Total (R$)', style={'padding': '8px', 'backgroundColor': '#444444', 'color': '#ffffff', 'textAlign': 'left'})])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(cliente, style={'padding': '8px', 'borderTop': '1px solid #333333', 'textAlign': 'left'}),
                    html.Td(f"{valor:,.2f}", style={'padding': '8px', 'borderTop': '1px solid #333333', 'textAlign': 'left'})
                ]) for cliente, valor in vendas_por_cliente.values
            ])
        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': '#222222', 'color': '#f0f0f0'})
    ], style={'padding': '20px', 'backgroundColor': '#222222', 'borderRadius': '8px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)'})

    # 5. Gráfico: Venda por Tipo de Produto (Pie Chart)
    # Mostra a proporção das vendas por categoria de produto.
    vendas_por_tipo_produto = df_filtered.groupby('Tipo de Produto')['Valor Total'].sum().reset_index()
    fig_tipo_produto = go.Figure(data=[go.Pie(labels=vendas_por_tipo_produto['Tipo de Produto'],
                                              values=vendas_por_tipo_produto['Valor Total'],
                                              hole=.3
                                             )])
    fig_tipo_produto.update_layout(
        title='Vendas Totais por Tipo de Produto',
        title_x=0.5,
        plot_bgcolor='#222222',
        paper_bgcolor='#1a1a1a',
        font=dict(color='#f0f0f0'),
        title_font_color='#ffffff',
        margin=dict(l=40, r=40, t=80, b=40)
    )
    fig_tipo_produto.update_traces(marker=dict(colors=['#636efa', '#EF553B', '#00cc96', '#ab63fa', '#FFA15A', '#19d3f3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']),
                                   hoverinfo='label+percent+value')

    # 6. Gráfico: Venda por Marca (Vertical Bar Chart)
    # Apresenta as marcas com maior volume de vendas.
    vendas_por_marca = df_filtered.groupby('Marca')['Valor Total'].sum().reset_index().sort_values(by='Valor Total', ascending=False).head(10)
    fig_marca = go.Figure(data=go.Bar(x=vendas_por_marca['Marca'],
                                       y=vendas_por_marca['Valor Total'],
                                       marker_color='#FFA15A'
                                      ))
    fig_marca = create_dark_mode_figure(fig_marca, 'Top 10 Marcas por Vendas Totais')
    fig_marca.update_layout(xaxis=dict(tickangle=45, automargin=True))
    fig_marca.update_xaxes(title_text='Marca')
    fig_marca.update_yaxes(title_text='Valor Total de Vendas (R$)')

    return fig_ano, fig_loja, fig_produto, table_cliente, fig_tipo_produto, fig_marca

server = app.server