import pandas as pd
from dash import dcc, html, callback, Output, Input, register_page
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import plotly.express as px

# Cargar datos
archivo_excel = pd.ExcelFile('CO2.xlsx')
data_hoja1 = pd.read_excel('CO2.xlsx', sheet_name='fossil_CO2_totals_by_country')

# Reestructurar los datos para facilitar la visualización por año
data_h1 = data_hoja1.melt(
    id_vars=['ISOcode', 'Country'],
    var_name='Year',
    value_name='CO2 Emissions'
)

data_h1['Year'] = data_h1['Year'].astype(int)
years = sorted(data_h1['Year'].unique(), reverse=True)

# Datos de sectores
data_hoja3 = pd.read_excel('CO2.xlsx', sheet_name='fossil_CO2_by_sector_and_countr')

data_3 = data_hoja3.melt(
    id_vars=['Sector', 'ISOcode', 'Country'],
    var_name='Year',
    value_name='CO2 Emissions'
)
grouped_data_sectors = data_3.groupby(['Sector', 'Year'])['CO2 Emissions'].sum().reset_index()

register_page(__name__, path="/emisiones-year")

layout = dbc.Container([
    html.H2("🌍 CO₂ Emissions by Year", className="text-center mt-4"),
    
    dbc.Row([
        dbc.Col([
            html.Label("Select a year:", className="fw-bold"),
            dcc.Dropdown(
                id='dropdown-year3',
                options=[{'label': str(year), 'value': year} for year in years],
                value=years[0],
                clearable=False
            ),

            html.Br(),  

            dcc.Graph(id='donut-chart', style={"height": "400px"})  # Ajustado el tamaño del gráfico de sectores

        ], width=4, style={"margin-bottom": "20px"}),  

        dbc.Col([
            html.Br(),
            dcc.Graph(id='graph-world-map3', style={"height": "600px"})  # Ajustado el tamaño del gráfico del globo
        ], width=8),
    ], className="mt-3"),
], fluid=True)

@callback(
    Output('graph-world-map3', 'figure'),
    [Input('dropdown-year3', 'value')]
)
def update_world_map(selected_year):
    df_year = data_h1[data_h1['Year'] == selected_year]
    df_year['CO2 Emissions Scaled'] = df_year['CO2 Emissions'] ** (1/3)
    
    fig = go.Figure(data=go.Choropleth(
        locations=df_year['ISOcode'],
        locationmode='ISO-3',
        z=df_year['CO2 Emissions Scaled'],
        text=df_year['Country'] + ": " + df_year['CO2 Emissions'].astype(str) + " Mt",
        colorscale=list(reversed(px.colors.sequential.Inferno)),
        colorbar=dict(title="CO₂ Emissions (Mt)"),
        zmin=df_year['CO2 Emissions Scaled'].min(),
        zmax=df_year['CO2 Emissions Scaled'].max()
    ))

    fig.update_geos(
        projection_type="orthographic",
        showland=True, landcolor="rgb(240, 240, 240)",
        showocean=True, oceancolor="rgb(200, 220, 250)",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="rgb(50, 50, 50)"
    )

    fig.update_layout(
        title=f'CO₂ Emissions by Country in {selected_year}',
        title_x=0.5,
        title_y=0.95,
        height=600,  # Ajustado de 650 a 600
        margin={"r":0, "t":80, "l":0, "b":0}
    )

    return fig

@callback(
    Output('donut-chart', 'figure'),
    [Input('dropdown-year3', 'value')]
)
def update_donut_chart(selected_year):
    filtered_data = grouped_data_sectors[grouped_data_sectors['Year'] == selected_year]
    fig = go.Figure(data=[go.Pie(labels=filtered_data['Sector'], values=filtered_data['CO2 Emissions'], hole=0.4)])
    fig.update_layout(
        title_text=f"CO2 Emissions Distribution by Sector in {selected_year}",
        title_x=0.5,
        title_y=0.95,
        height=400  # Ajustado de 450 a 400
    )
    return fig
