import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc

# Crear la app con soporte multipágina
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH], use_pages=True)

# Estilos personalizados para navbar
NAVBAR_STYLE = {
    "position": "sticky",
    "top": "0",
    "width": "100%",
    "zIndex": "1000",
    "background": "rgba(37, 93, 184, 0.8)",  # Azul con transparencia
    "backdropFilter": "blur(10px)",  # Efecto glassmorphism
    "boxShadow": "0px 4px 10px rgba(0, 0, 0, 0.2)",  # Sombra suave
    "padding": "10px 20px",
}

NAV_LINK_STYLE = {
    "color": "white",
    "padding": "10px 15px",
    "borderRadius": "8px",
    "transition": "0.3s",
    "fontSize": "18px",
    "fontWeight": "bold",
    "textDecoration": "none",
}

ACTIVE_NAV_LINK_STYLE = {
    **NAV_LINK_STYLE,
    "backgroundColor": "white",
    "color": "#255DB8",
}

# Navbar dinámico
navbar = html.Div([
    dcc.Location(id="url", refresh=False),  # Componente para obtener la URL actual
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H3("🏭 CO₂ emissions around the world", style={"color": "white"}), width="auto"),
            dbc.Col(
                dbc.Nav([
                    dcc.Link("Home", href="/", id="home-link", style=NAV_LINK_STYLE, className="nav-item"),
                    dcc.Link("Country Emissions", href="/emisiones-totales", id="country-link", style=NAV_LINK_STYLE, className="nav-item"),
                    dcc.Link("Year Emissions", href="/emisiones-year", id="year-link", style=NAV_LINK_STYLE, className="nav-item"),
                ], className="d-flex gap-3 justify-content-end"),
                width=True
            )
        ], align="center")
    ], fluid=True)
], style=NAVBAR_STYLE)

# Callback para actualizar los estilos de los enlaces de navegación según la URL actual
@callback(
    [Output("home-link", "style"),
     Output("country-link", "style"),
     Output("year-link", "style")],
    [Input("url", "pathname")]
)
def update_nav_style(pathname):
    return (
        ACTIVE_NAV_LINK_STYLE if pathname == "/" else NAV_LINK_STYLE,
        ACTIVE_NAV_LINK_STYLE if pathname == "/emisiones-totales" else NAV_LINK_STYLE,
        ACTIVE_NAV_LINK_STYLE if pathname == "/emisiones-year" else NAV_LINK_STYLE,
    )

# Layout principal
app.layout = dbc.Container([
    navbar,
    html.Br(),
    dash.page_container  # Renderiza las páginas
], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True)
