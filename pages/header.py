# Dash
import dash_bootstrap_components as dbc

# Barre de navigation/menu
def Navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Quizz", href="/page_1")),
            dbc.NavItem(dbc.NavLink("Map Quizz", href="/page_2")),
            dbc.NavItem(dbc.NavLink("Map Click", href="/page_3")),
            dbc.NavItem(dbc.NavLink("page 4", href="/page_4")),
        ],
        brand="Homepage",
        brand_href="/homepage",
        color="primary",
        dark=True,
    )
    return navbar