import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

# Simulated province data
provinces = {
    'Alberta': {'Population': 3375130},
    'British Columbia': {'Population': 4200425},
    'Manitoba': {'Population': 1058410},
    'New Brunswick': {'Population': 648250},
    'Newfoundland and Labrador': {'Population': 433955},
    'Northwest Territories': {'Population': 31915},
    'Nova Scotia': {'Population': 31915},
    'Nunavut': {'Population': 24540},
    'Ontario': {'Population': 11782825},
    'Prince Edward Island': {'Population': 126900},
    'Quebec': {'Population': 93585},
    'Saskatchewan': {'Population': 882760},
    'Yukon': {'Population': 32775}
}

# Load and clean data
df = pd.read_csv('data.csv')

# Clean 'Total', 'Men', 'Women' columns by removing commas and converting to numeric
for col in ['Total', 'Men', 'Women']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(',', '').str.replace('"', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=['Total', 'Men', 'Women'])

# Extract data for essential services
essential_services = ['Police officers', 'Firefighters', 'Registered nurses']
essential_df = df[df['Occupation'].str.contains('|'.join(essential_services), case=False, na=False)]

# Extract top-level NOC categories
pattern = r'^\d\s[A-Za-z]+'
noc_top_level_df = df[df['Occupation'].str.match(pattern, na=False)]

# Extract data for engineering roles
engineering_occupations = ['Computer engineers', 'Mechanical engineers', 'Electrical and electronics engineers']
engineering_df = df[df['Occupation'].str.contains('|'.join(engineering_occupations), case=False, na=False)]

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("2023 Canadian Census Data Dashboard", className="text-center"),
            html.P("Interactive visualization of essential services and employment statistics", className="text-center")
        ], width=12)
    ], className="mt-4 mb-4"),
    
    # Tabs for different visualizations
    dbc.Tabs([
        dbc.Tab(label="Essential Services Distribution", children=[
            dbc.Row([dbc.Col([html.H3("Essential Services Distribution")], width=12)]),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Service Type:"),
                    dcc.Dropdown(
                        id="service-type-dropdown",
                        options=[
                            {"label": "All Essential Services", "value": "all"},
                            {"label": "Police Officers", "value": "police"},
                            {"label": "Firefighters", "value": "fire"},
                            {"label": "Registered Nurses", "value": "nurse"}
                        ],
                        value="all",
                        clearable=False
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("Normalization:"),
                    dcc.RadioItems(
                        id="normalization-radio",
                        options=[
                            {"label": "Absolute Numbers", "value": "absolute"},
                            {"label": "Per 10,000 Population", "value": "normalized"}
                        ],
                        value="absolute",
                        inline=True
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("Sort By:"),
                    dcc.RadioItems(
                        id="sort-radio",
                        options=[
                            {"label": "Province (A-Z)", "value": "province"},
                            {"label": "Value (Descending)", "value": "value"}
                        ],
                        value="value",
                        inline=True
                    )
                ], width=4)
            ], className="mb-4"),
            
            dbc.Row([dbc.Col([dcc.Graph(id="essential-services-graph")], width=12)])
        ]),

        dbc.Tab(label="Gender-based Employment", children=[
            dbc.Row([dbc.Col([html.H3("Gender-based Employment Statistics")], width=12)]),
            dbc.Row([
                dbc.Col([
                    html.Label("Select NOC Categories:"),
                    dcc.Dropdown(
                        id="noc-dropdown",
                        options=[
                            {"label": occ, "value": occ} 
                            for occ in noc_top_level_df['Occupation'].unique()
                        ],
                        value=noc_top_level_df['Occupation'].unique()[:3].tolist(),
                        multi=True
                    )
                ], width=6),
                
                dbc.Col([
                    html.Label("Chart Type:"),
                    dcc.RadioItems(
                        id="chart-type-radio",
                        options=[
                            {"label": "Stacked Bar", "value": "stack"},
                            {"label": "Grouped Bar", "value": "group"},
                            {"label": "Gender Ratio", "value": "ratio"}
                        ],
                        value="stack",
                        inline=True
                    )
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([dbc.Col([dcc.Graph(id="gender-employment-graph")], width=12)])
        ]),

        dbc.Tab(label="Engineering Manpower", children=[
            dbc.Row([dbc.Col([html.H3("Engineering Manpower for EV Factory Setup")], width=12)]),
            dbc.Row([
                dbc.Col([
                    html.Label("Engineering Type:"),
                    dcc.Checklist(
                        id="engineering-checklist",
                        options=[
                            {"label": "Computer Engineers", "value": "computer"},
                            {"label": "Mechanical Engineers", "value": "mechanical"},
                            {"label": "Electrical Engineers", "value": "electrical"}
                        ],
                        value=["computer", "mechanical", "electrical"],
                        inline=True
                    )
                ], width=6),
                
                dbc.Col([
                    html.Label("View:"),
                    dcc.RadioItems(
                        id="engineering-view-radio",
                        options=[
                            {"label": "Absolute Numbers", "value": "absolute"},
                            {"label": "Percentage of Total", "value": "percentage"},
                            {"label": "Per Capita", "value": "per_capita"}
                        ],
                        value="absolute",
                        inline=True
                    )
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([dbc.Col([dcc.Graph(id="engineering-manpower-graph")], width=12)])
        ]),

        dbc.Tab(label="Custom Insight", children=[
            dbc.Row([dbc.Col([html.H3("Custom Insight: Gender Distribution Across Occupation Levels")], width=12)]),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Occupation Category:"),
                    dcc.Dropdown(
                        id="occupation-category-dropdown",
                        options=[
                            {"label": "Business & Finance", "value": "business"},
                            {"label": "Sciences & Engineering", "value": "science"},
                            {"label": "Health", "value": "health"},
                            {"label": "Education & Law", "value": "education"},
                            {"label": "Art & Culture", "value": "art"}
                        ],
                        value="science",
                        clearable=False
                    )
                ], width=6),
                
                dbc.Col([
                    html.Label("Analysis Type:"),
                    dcc.RadioItems(
                        id="analysis-type-radio",
                        options=[
                            {"label": "Hierarchy Level Analysis", "value": "hierarchy"},
                            {"label": "Gender Parity Index", "value": "parity"}
                        ],
                        value="hierarchy",
                        inline=True
                    )
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([dbc.Col([dcc.Graph(id="custom-insight-graph")], width=12)])
        ])
    ]),
    
    html.Footer([
        html.P("Data Source: 2023 Statistics Canada Census", className="text-center mt-4 text-muted")
    ])
], fluid=True)

# Callbacks for interactive visualizations
@app.callback(
    Output("essential-services-graph", "figure"),
    [
        Input("service-type-dropdown", "value"),
        Input("normalization-radio", "value"),
        Input("sort-radio", "value")
    ]
)
def update_essential_services_graph(service_type, normalization, sort_by):
    # Filter data based on service type
    if service_type == "all":
        filtered_df = essential_df.copy()
    elif service_type == "police":
        filtered_df = essential_df[essential_df['Occupation'].str.contains('Police', case=False, na=False)]
    elif service_type == "fire":
        filtered_df = essential_df[essential_df['Occupation'].str.contains('Fire', case=False, na=False)]
    elif service_type == "nurse":
        filtered_df = essential_df[essential_df['Occupation'].str.contains('Nurse', case=False, na=False)]
    
    # Create simulated data for provinces
    provinces_list = list(provinces.keys())
    province_data = []
    for occ in filtered_df['Occupation'].unique():
        total = filtered_df[filtered_df['Occupation'] == occ]['Total'].iloc[0]
        for province in provinces_list:
            pop_proportion = provinces[province]['Population'] / sum([p['Population'] for p in provinces.values()])
            variation = np.random.uniform(0.7, 1.3)
            province_value = int(total * pop_proportion * variation)
            province_data.append({
                'Province': province,
                'Occupation': occ,
                'Count': province_value,
                'Population': provinces[province]['Population'],
                'Per10K': (province_value / provinces[province]['Population']) * 10000
            })
    
    province_df = pd.DataFrame(province_data)
    
    if service_type == "all":
        province_df = province_df.groupby('Province').agg({
            'Count': 'sum',
            'Population': 'first',
            'Per10K': 'sum'
        }).reset_index()

    y_column = 'Per10K' if normalization == 'normalized' else 'Count'
    y_title = 'Personnel per 10,000 Population' if normalization == 'normalized' else 'Number of Personnel'
    
    if sort_by == 'province':
        province_df = province_df.sort_values('Province')
    else:
        province_df = province_df.sort_values(y_column, ascending=False)
    
    fig = px.bar(
        province_df,
        x='Province',
        y=y_column,
        color='Province',
        title=f'Essential Services Distribution by Province ({service_type.title()})',
        labels={'Province': 'Province/Territory', y_column: y_title}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        legend_title="Province/Territory",
        height=600
    )
    
    return fig

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
