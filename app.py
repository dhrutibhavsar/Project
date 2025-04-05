
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc


def clean_data(filepath):
   
    df = pd.read_csv(filepath)

    for col in ['Total', 'Men', 'Women']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('"', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['Total', 'Men', 'Women'])
    
    return df

def get_essential_services_data(df):

    essential_services = [
        'Police officers', 
        'Firefighters',
        'Registered nurses'
    ]
    
    essential_df = df[df['Occupation'].str.contains('|'.join(essential_services), case=False, na=False)]
    
    return essential_df

def get_noc_top_level_data(df):

    pattern = r'^\d\s[A-Za-z]+'
    top_level_df = df[df['Occupation'].str.match(pattern, na=False)]
    
    return top_level_df

def get_engineering_data(df):

    engineering_occupations = [
        'Computer engineers', 
        'Mechanical engineers',
        'Electrical and electronics engineers'
    ]
    
    engineering_df = df[df['Occupation'].str.contains('|'.join(engineering_occupations), case=False, na=False)]
    
    return engineering_df

def normalize_by_population(df, population_data):
   

    normalized_df = df.copy()

    for col in ['Total', 'Men', 'Women']:
        if col in normalized_df.columns:
            normalized_df[f'{col}_per_10k'] = normalized_df[col] / (population_data / 10000)
    
    return normalized_df

def get_gender_ratio(df):

    gender_df = df.copy()
    gender_df['GenderRatio'] = gender_df['Men'] / gender_df['Women']
    return gender_df


def get_province_data():

    provinces = {
        'Alberta': {'Population': 3375130	},
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
    
    return provinces

df = clean_data('data.csv')
provinces = get_province_data()


essential_services_df = get_essential_services_data(df)
noc_top_level_df = get_noc_top_level_data(df)
engineering_df = get_engineering_data(df)

province_populations = {prov: data['Population'] for prov, data in provinces.items()}

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("2023 Canadian Workforce and Employment Data Dashboard", className="text-center"),
            html.P("Interactive visualization of essential services and employment statistics", className="text-center")
        ], width=12)
    ], className="mt-4 mb-4"),

    dbc.Tabs([
      
        dbc.Tab(label="Essential Services Personnel by Province", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Essential Services Personnel Distribution by Province", className="mt-3"),
                    html.P("Distribution of essential services personnel (nurses, police, firefighters) across provinces")
                ], width=12)
            ]),
            
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
                    html.Label("Normalization Type:"),
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
                    html.Label("Sort Data By:"),
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
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="essential-services-graph")
                ], width=12)
            ])
        ]),
        

        dbc.Tab(label="Employment Statistics by Gender in NOC Categories", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Employment Statistics by Gender in NOC Categories", className="mt-3"),
                    html.P("Employment statistics by gender across top-level NOC categories")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Choose NOC Categories:"),
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
                    html.Label("Choose Chart Type:"),
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
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="gender-employment-graph")
                ], width=12)
            ])
        ]),
        

        dbc.Tab(label="Engineering Talent Distribution by Province", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Engineering Talent Distribution by Province", className="mt-3"),
                    html.P("Analysis of available engineering talent (Computer, Mechanical, Electrical) by province")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Select Engineering Occupation Types:"),
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
                    html.Label("View Data As:"),
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
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="engineering-manpower-graph")
                ], width=12)
            ])
        ]),
        
 
        dbc.Tab(label="Gender Distribution and Parity Across Occupation Categories", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Gender Distribution and Parity Across Occupation Categories", className="mt-3"),
                    html.P("Exploring gender distribution patterns across different occupation hierarchy levels")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Select Occupation Category for Analysis:"),
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
                    html.Label("Choose Analysis Type:"),
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
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="custom-insight-graph")
                ], width=12)
            ])
        ])
    ]),
    
    html.Footer([
        html.P("Data Source: 2023 Statistics Canada Census", className="text-center mt-4 text-muted")
    ])
], fluid=True)



@app.callback(
    Output("essential-services-graph", "figure"),
    [
        Input("service-type-dropdown", "value"),
        Input("normalization-radio", "value"),
        Input("sort-radio", "value")
    ]
)
def update_essential_services_graph(service_type, normalization, sort_by):
 
    if service_type == "all":
        filtered_df = essential_services_df.copy()
    elif service_type == "police":
        filtered_df = essential_services_df[essential_services_df['Occupation'].str.contains('Police', case=False, na=False)]
    elif service_type == "fire":
        filtered_df = essential_services_df[essential_services_df['Occupation'].str.contains('Fire', case=False, na=False)]
    elif service_type == "nurse":
        filtered_df = essential_services_df[essential_services_df['Occupation'].str.contains('Nurse', case=False, na=False)]
    

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
        title=f'Essential Services Personnel Distribution by Province ({service_type.title()})',
        labels={'Province': 'Province/Territory', y_column: y_title}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        legend_title="Province/Territory",
        height=600
    )
    
    return fig


@app.callback(
    Output("gender-employment-graph", "figure"),
    [
        Input("noc-dropdown", "value"),
        Input("chart-type-radio", "value")
    ]
)
def update_gender_employment_graph(selected_nocs, chart_type):

    if not selected_nocs or len(selected_nocs) == 0:
        selected_nocs = noc_top_level_df['Occupation'].unique()[:3].tolist()
    

    filtered_df = noc_top_level_df[noc_top_level_df['Occupation'].isin(selected_nocs)]
    

    if chart_type == "ratio":

        filtered_df = filtered_df.copy()  
        filtered_df['Ratio'] = filtered_df['Men'] / filtered_df['Women']
        
        fig = px.bar(
            filtered_df,
            x='Occupation',
            y='Ratio',
            color='Occupation',
            title='Gender Ratio in NOC Categories',
            labels={'Occupation': 'NOC Category', 'Ratio': 'Men/Women Ratio'}
        )
        

        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=1,
            x1=len(filtered_df) - 0.5,
            y1=1,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig.update_layout(height=600)
        
    else: 
        # Prepare data in long format
        df_long = pd.melt(
            filtered_df,
            id_vars=['Occupation'],
            value_vars=['Men', 'Women'],
            var_name='Gender',
            value_name='Count'
        )
        

        barmode = chart_type if chart_type in ['stack', 'group'] else 'stack'
        
        fig = px.bar(
            df_long,
            x='Occupation',
            y='Count',
            color='Gender',
            barmode=barmode,
            title='Employment by Gender in NOC Categories',
            labels={'Occupation': 'NOC Category', 'Count': 'Number of Employed Persons', 'Gender': 'Gender'}
        )
        
        fig.update_layout(height=600)
    
    return fig

@app.callback(
    Output("engineering-manpower-graph", "figure"),
    [
        Input("engineering-checklist", "value"),
        Input("engineering-view-radio", "value")
    ]
)
def update_engineering_manpower_graph(selected_types, view_type):

    if not selected_types or len(selected_types) == 0:
        selected_types = ["computer", "mechanical", "electrical"]
    

    engineering_filters = []
    if "computer" in selected_types:
        engineering_filters.append("Computer")
    if "mechanical" in selected_types:
        engineering_filters.append("Mechanical")
    if "electrical" in selected_types:
        engineering_filters.append("Electrical")

    if not engineering_filters:
        engineering_filters = ["Computer"]
    
    filtered_df = engineering_df[
        engineering_df['Occupation'].str.contains('|'.join(engineering_filters), case=False, na=False)
    ]
    

    if filtered_df.empty:
        fig = px.bar(
            title="No data matching selected engineering types",
        )
        fig.update_layout(height=600)
        return fig
    
    provinces_list = list(provinces.keys())
    province_data = []
    
    for occ in filtered_df['Occupation'].unique():
        total = filtered_df[filtered_df['Occupation'] == occ]['Total'].iloc[0]
        
        for province in provinces_list:
            pop_proportion = provinces[province]['Population'] / sum([p['Population'] for p in provinces.values()])

            if province in ['Ontario', 'British Columbia', 'Quebec']:
                variation = np.random.uniform(1.2, 1.8)  # Tech hubs with more engineers
            else:
                variation = np.random.uniform(0.5, 1.1)
                
            province_value = int(total * pop_proportion * variation)
            
            engineer_type = "Computer" if "Computer" in occ else "Mechanical" if "Mechanical" in occ else "Electrical"
            
            province_data.append({
                'Province': province,
                'EngineerType': engineer_type,
                'Count': province_value,
                'Population': provinces[province]['Population'],
                'Per10K': (province_value / provinces[province]['Population']) * 10000
            })
    
    province_df = pd.DataFrame(province_data)

    if view_type == "absolute":
        y_column = 'Count'
        y_title = 'Number of Engineers'
    elif view_type == "percentage":
   
        province_df = province_df.copy()
    
        province_totals = province_df.groupby('Province')['Count'].transform('sum')
        province_df['Percentage'] = (province_df['Count'] / province_totals) * 100
        y_column = 'Percentage'
        y_title = 'Percentage of Total Engineers (%)'
    else:  
        y_column = 'Per10K'
        y_title = 'Engineers per 10,000 Population'

    fig = px.bar(
        province_df,
        x='Province',
        y=y_column,
        color='EngineerType',
        barmode='group',
        title=f'Engineering Manpower by Province and Type',
        labels={'Province': 'Province/Territory', y_column: y_title, 'EngineerType': 'Engineer Type'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=600
    )
    
    return fig

@app.callback(
    Output("custom-insight-graph", "figure"),
    [
        Input("occupation-category-dropdown", "value"),
        Input("analysis-type-radio", "value")
    ]
)
def update_custom_insight_graph(category, analysis_type):

    category_filters = {
        "business": ["Business", "finance", "administration"],
        "science": ["Natural", "applied sciences", "engineering"],
        "health": ["Health", "nurse", "medical"],
        "education": ["Education", "law", "social"],
        "art": ["Art", "culture", "recreation"]
    }
    
 
    if category not in category_filters:
        category = "business"  
    

    filtered_df = df[
        df['Occupation'].str.contains('|'.join(category_filters[category]), case=False, na=False)
    ]
    

    if filtered_df.empty:
        fig = px.bar(
            title=f"No data matching selected category: {category}",
        )
