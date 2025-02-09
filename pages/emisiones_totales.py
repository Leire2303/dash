import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import pandas as pd
from dash_iconify import DashIconify

# Cargar datos
file_path = "CO2.xlsx"
xls = pd.ExcelFile(file_path)

data_totals = pd.read_excel(file_path, sheet_name="fossil_CO2_totals_by_country", header=0)
data_per_capita = pd.read_excel(file_path, sheet_name="fossil_CO2_per_capita_by_countr", header=0)

data_totals.columns = [int(col) if isinstance(col, float) else col for col in data_totals.columns]
data_per_capita.columns = [int(col) if isinstance(col, float) else col for col in data_per_capita.columns]

data_h1 = data_totals.melt(id_vars=['ISOcode', 'Country'], var_name='Year', value_name='CO2 Emissions')
data_h2 = data_per_capita.melt(id_vars=['ISOcode', 'Country'], var_name='Year', value_name='CO2 Emissions per Capita')

for df in [data_h1, data_h2]:
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df.dropna(subset=['Year'], inplace=True)
    df['Year'] = df['Year'].astype(int)

countries = sorted(data_h1['Country'].dropna().unique())
latest_year = data_h2['Year'].max()

ranking_per_capita = data_h2[data_h2['Year'] == latest_year].sort_values(by='CO2 Emissions per Capita', ascending=False).reset_index()
ranking_per_capita['Rank'] = ranking_per_capita.index + 1

data_sectors = pd.read_excel(file_path, sheet_name="fossil_CO2_by_sector_and_countr", header=0)
data_sectors.columns = [int(col) if isinstance(col, float) else col for col in data_sectors.columns]

data_sectors_melted = data_sectors.melt(id_vars=['Sector', 'ISOcode', 'Country'], var_name='Year', value_name='CO2 Emissions')

data_sectors_melted['Year'] = pd.to_numeric(data_sectors_melted['Year'], errors='coerce')
data_sectors_melted.dropna(subset=['Year'], inplace=True)
data_sectors_melted['Year'] = data_sectors_melted['Year'].astype(int)

excluded_sectors = ["Buildings", "Other industrial combustion", "Other sectors", "Power Industry", "Transport", "All Sectors"]
sector_options = [{'label': sector, 'value': sector} for sector in sorted(data_sectors_melted['Sector'].unique()) if sector not in excluded_sectors]

dash.register_page(__name__, path="/emisiones-totales", name="Emisiones Totales")

layout = dbc.Container(fluid=True, style={'padding-left': '0px', 'padding-right': '0px'}, children=[  
    html.H2("🌍 CO₂ Emissions by Country", className="text-center mt-4"),
    html.Div(style={'margin-bottom': '30px'}),
dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Select a country", className='card-title text-center'),
                    dcc.Dropdown(
                        id='country-selector', 
                        options=[{'label': c, 'value': c} for c in countries], 
                        value=countries[0], 
                        placeholder='Select a country',
                        style={'width': '90%', 'margin': 'auto'}
                    )
                ])
            ], className='mb-2'),  
            
            dbc.Card([
                dbc.CardBody([
                    html.H5("Percentage change in emissions since 2015", className='card-title text-center'),
                    html.Div([
                        html.Span(id='percentage-icon', style={'margin-right': '10px'}),
                        html.Span(id='percentage-change', style={'font-size': '24px', 'font-weight': 'bold', 'text-align': 'center'})
                    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})
                ])
            ], className='mb-2'),
            
            dbc.Card([
                dbc.CardBody([
                    html.H5("Per capita emissions ranking", className='card-title text-center'),
                    html.Div(id='ranking-position', style={'font-size': '24px', 'font-weight': 'bold', 'text-align': 'center'})
                ])
            ])
        ], width=2),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='emissions-line-chart')
                        ])
                    ])
                ], width=6),  

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Checklist(
                                id='checklist-sectors',
                                options=sector_options,
                                value=[],
                                labelStyle={'display': 'block'}
                            ),
                            dcc.Graph(id='sector-line-chart')  
                        ])
                    ])
                ], width=6)  
            ])
        ], width=10)  
    ])
])


@dash.callback(
    [Output('emissions-line-chart', 'figure'),
     Output('sector-line-chart', 'figure'),
     Output('percentage-change', 'children'),
     Output('percentage-icon', 'children'),
     Output('ranking-position', 'children')],
    [Input('country-selector', 'value'),
     Input('checklist-sectors', 'value')]
)
def update_graphs(selected_country, selected_sectors):
    if selected_country is None:
        return {}, {}, "Sin datos", "", "Sin datos"

    df_country = data_h1[data_h1['Country'] == selected_country]
    emissions_2015 = df_country[df_country['Year'] == 2015]['CO2 Emissions'].values
    emissions_latest = df_country.iloc[-1]['CO2 Emissions'] if not df_country.empty else None
    
    percentage_text = "Insufficient data"
    icon = ""
    if emissions_2015.size > 0 and emissions_latest is not None:
        percentage_change = ((emissions_latest - emissions_2015[0]) / emissions_2015[0]) * 100
        percentage_text = f"{percentage_change:.2f}%"
        icon = DashIconify(icon="mdi:arrow-up-bold", width=40, color="green") if percentage_change > 0 else DashIconify(icon="mdi:arrow-down-bold", width=40, color="red")

    ranking = ranking_per_capita[ranking_per_capita['Country'] == selected_country]
    rank_text = f"Rank nº{ranking.iloc[0]['Rank']}" if not ranking.empty else "No data"

    fig_country = px.line(df_country, x='Year', y='CO2 Emissions', title=f'Yearly CO₂ Emissions in {selected_country}')
    
    df_sectors_filtered = data_sectors_melted[data_sectors_melted['Country'] == selected_country]
    if selected_sectors:
        df_sectors_filtered = df_sectors_filtered[df_sectors_filtered['Sector'].isin(selected_sectors)]

    fig_sectors = px.line(df_sectors_filtered, x='Year', y='CO2 Emissions', color='Sector', title=f'CO₂ Emissions by Sector')

    return fig_country, fig_sectors, percentage_text, icon, rank_text

