# Import necessary libraries
import dash
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import io
import base64
import plotly.io as pio

class DashboardApp:
    def __init__(self):
        self.data = pd.read_csv('intoxication_alimentaire_maroc_mis_a_jour.csv')
        self.city_coordinates = {
            "Al Hoceïma": {"lat": 35.2511, "lon": -3.9315},
            "Larache": {"lat": 35.1932, "lon": -6.1557},
            "Ifrane": {"lat": 33.5333, "lon": -5.1167},
            "Casablanca": {"lat": 33.5731, "lon": -7.5898},
            "Inezgane": {"lat": 30.3657, "lon": -9.5333},
            "Taroudant": {"lat": 30.4725, "lon": -8.8762},
            "Tangier": {"lat": 35.7595, "lon": -5.8339},
            "Mohammedia": {"lat": 33.6861, "lon": -7.3829},
            "Marrakech": {"lat": 31.6295, "lon": -7.9811},
            "Agadir": {"lat": 30.4278, "lon": -9.5981},
            "Tétouan": {"lat": 35.5663, "lon": -5.3724},
            "Safi": {"lat": 32.2994, "lon": -9.2372},
        }
        self.data["Latitude"] = self.data["Ville"].map(lambda ville: self.city_coordinates.get(ville, {}).get("lat"))
        self.data["Longitude"] = self.data["Ville"].map(lambda ville: self.city_coordinates.get(ville, {}).get("lon"))
        self.app = dash.Dash(__name__)
        self.app.title = "Tableau de Bord - Incidents Alimentaires"
        self.set_custom_css()
        self.set_layout()
        self.set_callbacks()

    def set_custom_css(self):
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        background: linear-gradient(135deg, #1a1a1a 0%, #0a192f 100%);
                        color: #ffffff;
                    }
                    .dashboard-container {
                        max-width: 1800px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    .card {
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 15px;
                        padding: 20px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        backdrop-filter: blur(10px);
                        margin-bottom: 20px;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                    }
                    .kpi-card {
                        background: linear-gradient(45deg, #2c3e50, #3498db);
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        transition: transform 0.3s ease;
                        
                    }
                    .kpi-card:hover {
                        transform: translateY(-5px);
                    }
                    .alert-card {
                        background: linear-gradient(45deg, #c0392b, #e74c3c);
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 10px;
                    }
                    .dropdown-container {
                        background: rgba(255, 255, 255, 0.1);
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                    }
                    .dropdown-container .Select--multi .Select-value {
                        background-color: #ffffff !important;
                        color: #000000 !important;
                    }
                    .dropdown-container .Select-menu-outer {
                        background-color: #ffffff !important;
                        color: #000000 !important;
                    }
                    .dashboard-title {
                        text-align: center;
                        padding: 20px 0;
                        font-size: 2.5em;
                        font-weight: 600;
                        color: #3498db;
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
    def set_layout(self):
        self.app.layout = html.Div([
            html.Div([
                html.H1("Intoxications Alimentaires au Maroc : Analyse Régionale et Facteurs de Risque", 
                        className="dashboard-title"),
                html.Div([
                    html.Label("Filtrer par région:", style={'font-weight': '500', 'margin-bottom': '10px'}),
                    dcc.Dropdown(
                        id='region-filter',
                        options=[{'label': region, 'value': region,} for region in sorted(self.data['Région'].unique())],
                        multi=True,
                        placeholder="Sélectionner une ou plusieurs régions",
                        style={'background-color': 'rgba(255, 255, 255, 0.1)', 'border': 'none'}
                    )
                ], className="dropdown-container"),
                html.Div([
                    html.Div(id="kpi-total-incidents", className="kpi-card"),
                    html.Div(id="kpi-fatality-rate", className="kpi-card"),
                    html.Div(id="kpi-hospitalized", className="kpi-card"),
                ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr 1fr', 'gap': '20px', 'margin-bottom': '20px'}),
                html.Div([
                    html.Div([
                        dcc.Graph(id='incident-map', style={'height': '60vh'})
                    ], className="card", style={'flex': '2'}),
                    html.Div([
                        html.H2("Alertes Importantes", style={'margin-top': '0'}),
                        html.Div(id='alerts-section', style={'max-height': '50vh', 'overflow-y': 'auto'})
                    ], className="card", style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
                html.Div([
                    dcc.Graph(id='trend-line-chart')
                ], className="card"),
                html.Div([
                    html.Div([
                        dcc.Graph(id='food-item-bar')
                    ], className="card", style={'flex': '1'}),
                    html.Div([
                        dcc.Graph(id='severity-pie')
                    ], className="card", style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
                html.Div([
                    html.Div([
                        dcc.Graph(id='age-group-bar')
                    ], className="card", style={'flex': '1'}),
                    html.Div([
                        dcc.Graph(id='bacteria-bar')
                    ], className="card", style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
                html.Div([
                    html.Div([
                        dcc.Graph(id='radar-chart')
                    ], className="card", style={'flex': '1'}),
                    html.Div([
                        dcc.Graph(id='actions-pie')
                    ], className="card", style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
                html.Div([
                    html.Button(
                        "📊 Télécharger les données",
                        id="download-csv-button",
                        style={
                            'background': 'linear-gradient(45deg, #2ecc71, #27ae60)',
                            'border': 'none',
                            'padding': '15px 30px',
                            'color': 'white',
                            'border-radius': '8px',
                            'cursor': 'pointer',
                            'font-weight': '500',
                            'transition': 'transform 0.2s ease',
                            'margin': '20px 0'
                        }
                    ),
                    dcc.Download(id="download-csv"),
                ], style={'text-align': 'center'})
            ], className="dashboard-container")
        ])

    def set_callbacks(self):
        @self.app.callback(
            [Output('incident-map', 'figure'),
             Output('food-item-bar', 'figure'),
             Output('severity-pie', 'figure'),
             Output('age-group-bar', 'figure'),
             Output('bacteria-bar', 'figure'),
             Output('trend-line-chart', 'figure'),
             Output('radar-chart', 'figure'),
             Output('actions-pie', 'figure'),
             Output('alerts-section', 'children'),
             Output('kpi-total-incidents', 'children'),
             Output('kpi-fatality-rate', 'children'),
             Output('kpi-hospitalized', 'children')],
            [Input('region-filter', 'value')]
        )
        def update_dashboard(selected_regions):
            filtered_data = self.data.copy()
            if selected_regions and len(selected_regions) > 0:
                filtered_data = filtered_data[filtered_data['Région'].isin(selected_regions)]
            filtered_data['Date d\'incident'] = pd.to_datetime(filtered_data['Date d\'incident'], errors='coerce')
            filtered_data = filtered_data.dropna(subset=['Date d\'incident'])
            total_incidents = len(filtered_data)
            fatality_rate = (filtered_data['Résultat'] == 'Fatal').sum() / total_incidents * 100 if total_incidents > 0 else 0
            hospitalized = filtered_data['Hospitalisé'].sum()
            map_fig = px.scatter_mapbox(
                filtered_data,
                lat="Latitude",
                lon="Longitude",
                color="Gravité",
                size="Nombre affecté",
                hover_name="Ville",
                hover_data=["Aliment suspecté", "Nombre affecté"],
                mapbox_style="carto-positron",
                zoom=5,
                center={"lat": 31.7917, "lon": -7.0926},
                title="Distribution Géographique des Incidents"
            )
            map_fig.update_layout(
                margin={"r":0,"t":30,"l":0,"b":0},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            food_fig = px.bar(
                filtered_data.groupby('Aliment suspecté')['Nombre affecté'].sum().reset_index().sort_values('Nombre affecté', ascending=True),
                y='Aliment suspecté',
                x='Nombre affecté',
                orientation='h',
                title="Incidents par Type d'Aliment",
                color_discrete_sequence=['#3498db']
            )
            food_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(showgrid=False)
            )
            severity_fig = px.pie(
                filtered_data,
                names='Gravité',
                title="Répartition par Gravité",
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            severity_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            age_fig = px.bar(
                filtered_data.groupby('Groupe d\'âge')['Nombre affecté'].sum().reset_index(),
                x='Nombre affecté',
                y='Groupe d\'âge',
                orientation='h',
                title="Distribution par Groupe d'Âge",
                color_discrete_sequence=['#2ecc71']
            )
            age_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(showgrid=False)
            )
            bacteria_fig = px.bar(
                filtered_data.groupby('Bactérie détectée')['Nombre affecté'].sum().reset_index(),
                x='Bactérie détectée',
                y='Nombre affecté',
                title="Types de Bactéries Détectées",
                color_discrete_sequence=['#e74c3c']
            )
            bacteria_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
            )
            trend_data = filtered_data.groupby('Date d\'incident')['Nombre affecté'].sum().reset_index()
            trend_fig = px.line(
                trend_data,
                x='Date d\'incident',
                y='Nombre affecté',
                title="Évolution Temporelle des Incidents",
                line_shape="spline",
                markers=True
            )
            trend_fig.update_traces(line_color="#f1c40f")
            trend_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
            )
            alerts = self.get_alerts(filtered_data)
            alerts_html = [
                html.Div(
                    alert,
                    className="alert-card",
                    style={
                        'margin-bottom': '10px',
                        'padding': '10px',
                        'border-radius': '5px',
                        'background-color': 'rgba(231, 76, 60, 0.2)',
                        'border-left': '4px solid #e74c3c'
                    }
                ) for alert in alerts
            ]
            kpi1_html = html.Div([
                html.H3("Total des Incidents", style={'margin': '0', 'font-size': '1em'}),
                html.H2(f"{total_incidents:,}", style={'margin': '10px 0', 'font-size': '2em'})
            ])
            kpi2_html = html.Div([
                html.H3("Taux de Fatalité", style={'margin': '0', 'font-size': '1em'}),
                html.H2(f"{fatality_rate:.1f}%", style={'margin': '10px 0', 'font-size': '2em'})
            ])
            kpi3_html = html.Div([
                html.H3("Personnes Hospitalisées", style={'margin': '0', 'font-size': '1em'}),
                html.H2(f"{hospitalized:,}", style={'margin': '10px 0', 'font-size': '2em'})
            ])
            if 'Source alimentaire' in filtered_data.columns:
                radar_data = filtered_data.groupby('Source alimentaire')['Nombre affecté'].sum().reset_index()
                radar_fig = go.Figure()
                radar_fig.add_trace(go.Scatterpolar(
                    r=radar_data['Nombre affecté'],
                    theta=radar_data['Source alimentaire'],
                    fill='toself',
                    line=dict(color='#3498db'),
                    fillcolor='rgba(52, 152, 219, 0.5)'
                ))
                radar_fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, radar_data['Nombre affecté'].max()],
                            showline=False,
                            gridcolor='rgba(255,255,255,0.1)'
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.1)'
                        ),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    title="Distribution des Incidents par Source Alimentaire",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
            else:
                radar_fig = go.Figure()
                radar_fig.update_layout(
                    title="Source alimentaire column not found",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
            actions_data = filtered_data.groupby('Actions de suivi')['Nombre affecté'].sum().reset_index()
            actions_fig = px.pie(
                actions_data,
                names='Actions de suivi',
                values='Nombre affecté',
                title="Actions de Suivi Entreprises",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            actions_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
            )
            return map_fig, food_fig, severity_fig, age_fig, bacteria_fig, trend_fig, radar_fig, actions_fig, alerts_html, kpi1_html, kpi2_html, kpi3_html

        @self.app.callback(
            Output("download-csv", "data"),
            Input("download-csv-button", "n_clicks"),
            prevent_initial_call=True
        )
        def download_csv(n_clicks):
            if n_clicks:
                return dcc.send_data_frame(self.data.to_csv, "incidents_alimentaires.csv")

    def get_alerts(self, data):
        alerts = []
        high_risk_regions = data.groupby('Région')['Nombre affecté'].sum().reset_index()
        high_risk_regions = high_risk_regions[high_risk_regions['Nombre affecté'] > 50]
        for _, row in high_risk_regions.iterrows():
            alerts.append(f"⚠️ Région à haut risque : {row['Région']} avec {row['Nombre affecté']} cas signalés.")
        high_risk_foods = data.groupby('Aliment suspecté')['Nombre affecté'].sum().reset_index()
        high_risk_foods = high_risk_foods[high_risk_foods['Nombre affecté'] > 100]
        for _, row in high_risk_foods.iterrows():
            alerts.append(f"⚠️ Aliment à haut risque : {row['Aliment suspecté']} avec {row['Nombre affecté']} cas signalés.")
        return alerts

if __name__ == '__main__':
    app = DashboardApp()
    app.app.run_server(debug=True)
