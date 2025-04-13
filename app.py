import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ===== 1. IMPORT LIBRARIES =====
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Scheme

# ===== 2. LOAD AND CLEAN DATA =====
# Load raw data from Excel
excel_path = r"Data/Review_Category_Report.xlsx"
raw_df = pd.read_excel(excel_path, sheet_name='Sheet1')

# Clean data
raw_df = raw_df.dropna(subset=['Company Name', 'Standardized Category'])
raw_df['Review Count'] = pd.to_numeric(raw_df['Review Count'], errors='coerce').fillna(0).astype(int)

# Standardize company types
company_type_mapping = {
    'Modern/High-Class Private Hospital': 'High-Class Private Hospital'
}
raw_df['Company Type'] = raw_df['Company Type'].replace(company_type_mapping)

# Standardize categories to exact specified names
category_mapping = {
    'Slow Services or Lengthy Waiting Times': 'Slow Services or Lengthy Waiting Times',
    'Unprofessional Staff': 'Unprofessional Staff',
    'Hostility': 'Hostility',
    'Poor Compensation': 'Poor Compensation',
    'Unavailability of Medication/Equipment': 'Unavailability of Medication/Equipment',
    'Unavailability of Specialist': 'Unavailability of Specialists',
    'Expensive Costs': 'Expensive Costs',
    'Others': 'Others'
}
raw_df['Standardized Category'] = raw_df['Standardized Category'].replace(category_mapping)

# ===== 3. PREPARE VISUALIZATION DATA =====
# Create visualization dataframe
viz_df = raw_df.copy()

# === 3.1 Count of Companies per Category ===
company_counts = (
    raw_df.groupby(['Standardized Category', 'Company Type'])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# Define our company types of interest
company_types = [
    'Government Hospital',
    'Small Private Hospital',
    'High-Class Private Hospital'
]

# Ensure all required columns exist
for ct in company_types:
    if ct not in company_counts.columns:
        company_counts[ct] = 0

# Add Total column
company_counts['Total'] = company_counts[company_types].sum(axis=1).astype(int)
company_counts = company_counts.rename(columns={'Standardized Category': 'Category'})

# === 3.2 Number of Reviews per Company Type ===
reviews_per_type = (
    raw_df.groupby(['Standardized Category', 'Company Type'])
    ['Review Count'].sum()
    .unstack(fill_value=0)
    .reset_index()
)

# Include only the three company types
for ct in company_types:
    if ct not in reviews_per_type.columns:
        reviews_per_type[ct] = 0

# Add Total and format as integers
reviews_per_type['Total'] = reviews_per_type[company_types].sum(axis=1).astype(int)
reviews_per_type = reviews_per_type.rename(columns={'Standardized Category': 'Category'})

# === 3.3 Prepare data for visualizations ===
category_reviews = viz_df.groupby('Standardized Category')['Review Count'].sum().reset_index()
reviews_by_type = viz_df.groupby(['Standardized Category', 'Company Type'])['Review Count'].sum().reset_index()

# Prepare company breakdown data
company_breakdown = viz_df[['Standardized Category', 'Company Name', 'Company Location']].drop_duplicates()
company_breakdown = company_breakdown.groupby('Standardized Category').apply(
    lambda x: x[['Company Name', 'Company Location']].to_dict('records')
).reset_index()
company_breakdown.columns = ['Category', 'Companies']

# Get unique categories for dropdown in exact specified order
available_categories = [
    'Slow Services or Lengthy Waiting Times',
    'Unavailability of Medication/Equipment',
    'Unprofessional Staff',
    'Unavailability of Specialists',
    'Poor Compensation',
    'Hostility',
    'Expensive Costs',
    'Others'
]

# ===== 4. INITIALIZE DASH APP =====
# Initialize Dash app with a professional theme
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Professional color scheme
colors = {
    'background': '#f8fafc',
    'text': '#1e293b',
    'accent': '#3b82f6',
    'secondary': '#64748b',
    'government': '#2563eb',      # Blue
    'small_private': '#ef4444',   # Red
    'high_class': '#10b981',      # Green
    'others': '#8b5cf6',          # Purple
    'header': '#1e293b',
    'card_bg': '#ffffff',
    'table_header': '#1e40af',
    'table_row_even': '#f8fafc',
    'table_row_odd': '#ffffff',
    'table_border': '#e2e8f0',
    'highlight': '#f59e0b'
}

# ===== 5. CUSTOM STYLING =====
# Custom CSS for additional styling
custom_css = {
    'dropdown': {
        'width': '100%',
        'margin': '0 auto 20px auto',
        'fontFamily': '"Inter", sans-serif',
        'borderRadius': '8px',
        'border': f'1px solid {colors["table_border"]}'
    },
    'card': {
        'borderRadius': '12px',
        'boxShadow': '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)',
        'padding': '24px',
        'marginBottom': '24px',
        'backgroundColor': colors['card_bg'],
        'border': 'none'
    },
    'table': {
        'backgroundColor': 'white',
        'textAlign': 'center',
        'fontFamily': '"Inter", sans-serif',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'borderRadius': '12px',
        'overflow': 'hidden',
        'border': 'none'
    },
    'section_header': {
        'borderBottom': f'2px solid {colors["accent"]}',
        'paddingBottom': '12px',
        'marginBottom': '24px',
        'color': colors['header'],
        'fontWeight': '600',
        'fontSize': '1.5rem'
    },
    'metric': {
        'fontSize': '2.5rem',
        'fontWeight': '700',
        'color': colors['accent'],
        'marginBottom': '8px'
    },
    'metric_label': {
        'fontSize': '1rem',
        'color': colors['secondary'],
        'textTransform': 'uppercase',
        'letterSpacing': '0.05em'
    }
}

# ===== 6. APP LAYOUT =====
# Font import and global styles
app.layout = dbc.Container([
    # === 6.1 Header Section ===
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.H1("HEALTHCARE SERVICE QUALITY DASHBOARD", 
                           className="display-4",
                           style={
                               'color': colors['header'],
                               'fontWeight': '700',
                               'marginBottom': '12px',
                               'letterSpacing': '-0.025em'
                           }),
                    html.P("Comprehensive analysis of Customers and Staffs reviews across healthcare company types",
                          style={
                              'color': colors['secondary'],
                              'fontSize': '1.1rem',
                              'marginBottom': '0'
                          })
                ], style={
                    'textAlign': 'center', 
                    'padding': '40px 0 30px',
                    'borderBottom': f'1px solid {colors["table_border"]}',
                    'marginBottom': '30px'
                })
            ])
        ], width=12)
    ]),
    
    # === 6.2 Key Metrics Section ===
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(style={
                        'height': '4px',
                        'width': '100%',
                        'backgroundColor': colors['government'],
                        'marginBottom': '16px',
                        'borderRadius': '2px'
                    }),
                    html.H3(f"{viz_df['Review Count'].sum():,}", 
                           style=custom_css['metric']),
                    html.P("TOTAL REVIEWS ANALYZED", 
                          style=custom_css['metric_label'])
                ], style={'textAlign': 'center'})
            ], style={**custom_css['card'], 'padding': '20px'})
        ], md=4),
        
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(style={
                        'height': '4px',
                        'width': '100%',
                        'backgroundColor': colors['small_private'],
                        'marginBottom': '16px',
                        'borderRadius': '2px'
                    }),
                    html.H3(f"{viz_df['Company Name'].nunique():,}", 
                           style=custom_css['metric']),
                    html.P("HEALTHCARE COMPANIES", 
                          style=custom_css['metric_label'])
                ], style={'textAlign': 'center'})
            ], style={**custom_css['card'], 'padding': '20px'})
        ], md=4),
        
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(style={
                        'height': '4px',
                        'width': '100%',
                        'backgroundColor': colors['high_class'],
                        'marginBottom': '16px',
                        'borderRadius': '2px'
                    }),
                    html.H3(f"{len(available_categories)}", 
                           style=custom_css['metric']),
                    html.P("SERVICE CATEGORIES", 
                          style=custom_css['metric_label'])
                ], style={'textAlign': 'center'})
            ], style={**custom_css['card'], 'padding': '20px'})
        ], md=4)
    ], className="mb-4"),
    
    # === 6.3 Visualization Section ===
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("Review Distribution by Service Category", 
                       style=custom_css['section_header']),
                dcc.Graph(id='pie-chart',
                          config={'displayModeBar': False},
                          style={'height': '750px'})
            ], style=custom_css['card'])
        ], lg=6),
        
        dbc.Col([
            html.Div([
                html.H3("Review Volume by Company Type", 
                       style=custom_css['section_header']),
                dcc.Graph(id='stacked-bar',
                          config={'displayModeBar': False},
                          style={'height': '900px'})
            ], style=custom_css['card'])
        ], lg=6)
    ], className="mb-4"),
    
    # === 6.4 Detailed Analysis Section ===
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("Service Category Deep Dive", 
                       style=custom_css['section_header']),
                html.P("Select a service category to analyze review distribution across company types:",
                      style={'color': colors['secondary'], 'marginBottom': '16px'}),
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': cat, 'value': cat} for cat in available_categories],
                    value='Slow Services or Lengthy Waiting Times',
                    clearable=False,
                    style=custom_css['dropdown']
                ),
                dcc.Graph(id='category-pie-chart',
                          config={'displayModeBar': False},
                          style={'height': '350px'})
            ], style=custom_css['card'])
        ], width=12)
    ], className="mb-4"),
    
    # === 6.5 Data Tables Section ===
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("Company Count by Service Category", 
                       style=custom_css['section_header']),
                dash_table.DataTable(
                    id='company-counts-table',
                    columns=[
                        {"name": "Service Category", "id": "Category"},
                        {"name": "Government", "id": "Government Hospital"},
                        {"name": "Small Private", "id": "Small Private Hospital"},
                        {"name": "High-Class", "id": "High-Class Private Hospital"},
                        {"name": "Total", "id": "Total"}
                    ],
                    data=company_counts.to_dict('records'),
                    style_header={
                        'backgroundColor': colors['table_header'],
                        'color': 'white',
                        'fontWeight': '600',
                        'textAlign': 'center',
                        'border': 'none',
                        'fontSize': '0.85rem',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.05em'
                    },
                    style_cell={
                        'textAlign': 'center',
                        'padding': '12px',
                        'border': 'none',
                        'fontFamily': '"Inter", sans-serif',
                        'borderBottom': f'1px solid {colors["table_border"]}'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': colors['table_row_odd']
                        },
                        {
                            'if': {'row_index': 'even'},
                            'backgroundColor': colors['table_row_even']
                        },
                        {
                            'if': {'column_id': 'Total'},
                            'backgroundColor': '#f1f5f9',
                            'fontWeight': '600'
                        },
                        {
                            'if': {
                                'filter_query': '{Government Hospital} > 0',
                                'column_id': 'Government Hospital'
                            },
                            'color': colors['government'],
                            'fontWeight': '500'
                        },
                        {
                            'if': {
                                'filter_query': '{Small Private Hospital} > 0',
                                'column_id': 'Small Private Hospital'
                            },
                            'color': colors['small_private'],
                            'fontWeight': '500'
                        },
                        {
                            'if': {
                                'filter_query': '{High-Class Private Hospital} > 0',
                                'column_id': 'High-Class Private Hospital'
                            },
                            'color': colors['high_class'],
                            'fontWeight': '500'
                        }
                    ],
                    style_table={
                        'overflowX': 'auto',
                        'borderRadius': '12px',
                        'border': f'1px solid {colors["table_border"]}'
                    }
                )
            ], style=custom_css['card'])
        ], lg=6),
        
        dbc.Col([
            html.Div([
                html.H3("Review Volume by Service Category", 
                       style=custom_css['section_header']),
                dash_table.DataTable(
                    id='reviews-table',
                    columns=[
                        {"name": "Service Category", "id": "Category"},
                        {"name": "Government", "id": "Government Hospital", 
                         "type": "text"},
                        {"name": "Small Private", "id": "Small Private Hospital", 
                         "type": "text"},
                        {"name": "High-Class", "id": "High-Class Private Hospital", 
                         "type": "text"},
                        {"name": "Total", "id": "Total", 
                         "type": "text"}
                    ],
                    data=[{
                        'Category': row['Category'],
                        'Government Hospital': f"{row['Government Hospital']:,} reviews" if row['Government Hospital'] > 0 else "0 reviews",
                        'Small Private Hospital': f"{row['Small Private Hospital']:,} reviews" if row['Small Private Hospital'] > 0 else "0 reviews",
                        'High-Class Private Hospital': f"{row['High-Class Private Hospital']:,} reviews" if row['High-Class Private Hospital'] > 0 else "0 reviews",
                        'Total': f"{row['Total']:,} reviews" if row['Total'] > 0 else "0 reviews"
                    } for row in reviews_per_type.to_dict('records')],
                    style_header={
                        'backgroundColor': colors['table_header'],
                        'color': 'white',
                        'fontWeight': '600',
                        'textAlign': 'center',
                        'border': 'none',
                        'fontSize': '0.85rem',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.05em'
                    },
                    style_cell={
                        'textAlign': 'center',
                        'padding': '12px',
                        'border': 'none',
                        'fontFamily': '"Inter", sans-serif',
                        'borderBottom': f'1px solid {colors["table_border"]}'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': colors['table_row_odd']
                        },
                        {
                            'if': {'row_index': 'even'},
                            'backgroundColor': colors['table_row_even']
                        },
                        {
                            'if': {'column_id': 'Total'},
                            'backgroundColor': '#f1f5f9',
                            'fontWeight': '600'
                        },
                        {
                            'if': {'column_id': 'Government Hospital'},
                            'color': colors['government'],
                            'fontWeight': '500'
                        },
                        {
                            'if': {'column_id': 'Small Private Hospital'},
                            'color': colors['small_private'],
                            'fontWeight': '500'
                        },
                        {
                            'if': {'column_id': 'High-Class Private Hospital'},
                            'color': colors['high_class'],
                            'fontWeight': '500'
                        }
                    ],
                    style_table={
                        'overflowX': 'auto',
                        'borderRadius': '12px',
                        'border': f'1px solid {colors["table_border"]}'
                    }
                )
            ], style=custom_css['card'])
        ], lg=6)
    ], className="mb-4"),
    
    # === 6.6 Company Breakdown Section ===
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("Company Directory by Service Category", 
                       style=custom_css['section_header']),
                html.P("Select a service category to view companies with reported concerns:",
                      style={'color': colors['secondary'], 'marginBottom': '16px'}),
                dcc.Dropdown(
                    id='breakdown-category-dropdown',
                    options=[{'label': cat, 'value': cat} for cat in available_categories],
                    value='Slow Services or Lengthy Waiting Times',
                    clearable=False,
                    style=custom_css['dropdown']
                ),
                html.Div(id='company-breakdown-table', style={
                    'marginTop': '20px',
                    'borderRadius': '12px',
                    'overflow': 'hidden',
                    'border': f'1px solid {colors["table_border"]}'
                })
            ], style=custom_css['card'])
        ], width=12)
    ], className="mb-4"),
    
    # === 6.7 Footer Section ===
    dbc.Row([
        dbc.Col([
            html.Div([
                html.P("Healthcare Analytics Dashboard | © 2025 Quality Care Initiative",
                      style={
                          'textAlign': 'center',
                          'color': colors['secondary'],
                          'padding': '20px 0',
                          'borderTop': f'1px solid {colors["table_border"]}',
                          'marginTop': '20px',
                          'fontSize': '0.9rem'
                      })
            ])
        ], width=12)
    ])
], fluid=True, style={
    'backgroundColor': colors['background'], 
    'fontFamily': '"Inter", sans-serif',
    'padding': '0 20px',
    'maxWidth': '1400px'
})

# ===== 7. CALLBACK FUNCTIONS =====
@app.callback(
    Output('pie-chart', 'figure'),
    Output('stacked-bar', 'figure'),
    Input('pie-chart', 'hoverData')
)
def update_figures(hover_data):
    # === 7.1 Enhanced Pie Chart ===
    pie_fig = px.pie(
        category_reviews,
        values='Review Count',
        names='Standardized Category',
        title='',
        hole=0.6,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        category_orders={'Standardized Category': available_categories}
    )
    pie_fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#ffffff', width=1)),
        pull=[0.05 if i == 0 else 0 for i in range(len(category_reviews))]
    )
    pie_fig.update_layout(
        plot_bgcolor=colors['card_bg'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text'], family='"Inter", sans-serif'),
        margin=dict(t=0, b=0, l=0, r=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='"Inter", sans-serif'
        )
    )
    
    # === 7.2 Enhanced Stacked Bar Chart ===
    stacked_fig = px.bar(
        reviews_by_type,
        x='Standardized Category',
        y='Review Count',
        color='Company Type',
        title='',
        color_discrete_map={
            'Government Hospital': colors['government'],
            'Small Private Hospital': colors['small_private'],
            'High-Class Private Hospital': colors['high_class']
        },
        category_orders={'Standardized Category': available_categories}
    )
    stacked_fig.update_layout(
        plot_bgcolor=colors['card_bg'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text'], family='"Inter", sans-serif', size=12),
        barmode='stack',
        xaxis={
            'categoryorder':'array',
            'categoryarray': available_categories,
            'title': None,
            'tickfont': dict(size=12),
            'gridcolor': colors['table_border']
        },
        yaxis={
            'title': None,
            'gridcolor': colors['table_border'],
            'tickformat': ','
        },
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(b=100, t=20),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='"Inter", sans-serif'
        )
    )
    stacked_fig.update_traces(
        hovertemplate='%{y:,} reviews<extra></extra>'
    )
    
    return pie_fig, stacked_fig

@app.callback(
    Output('category-pie-chart', 'figure'),
    Input('category-dropdown', 'value')
)
def update_category_pie(selected_category):
    # === 7.3 Category Pie Chart ===
    # Filter data for selected category
    category_data = viz_df[viz_df['Standardized Category'] == selected_category]
    category_by_type = category_data.groupby('Company Type')['Review Count'].sum().reset_index()
    
    # Create enhanced donut chart
    fig = px.pie(
        category_by_type,
        values='Review Count',
        names='Company Type',
        title=f'<b style="font-size: 16px;">{selected_category}</b><br>Review Distribution by Company Type',
        hole=0.7,
        color_discrete_sequence=[
            colors['government'],
            colors['small_private'],
            colors['high_class']
        ]
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#ffffff', width=1)),
        hovertemplate='%{label}: %{value:,} reviews (%{percent})<extra></extra>'
    )
    fig.update_layout(
        plot_bgcolor=colors['card_bg'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text'], family='"Inter", sans-serif', size=12),
        margin=dict(t=80, b=0, l=0, r=0),
        showlegend=False,
        title_x=0.5,
        title_y=0.95,
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='"Inter", sans-serif'
        )
    )
    
    # Add center text with total reviews
    total_reviews = category_by_type['Review Count'].sum()
    fig.add_annotation(
        text=f"Total<br>{total_reviews:,}",
        x=0.5, y=0.5,
        font=dict(size=14, color=colors['text']),
        showarrow=False
    )
    
    return fig

@app.callback(
    Output('company-breakdown-table', 'children'),
    Input('breakdown-category-dropdown', 'value')
)
def update_company_breakdown(selected_category):
    # === 7.4 Company Breakdown Table ===
    # Find the selected category in our breakdown data
    breakdown = company_breakdown[company_breakdown['Category'] == selected_category]
    
    if breakdown.empty:
        return html.Div(
            "No companies found for this service category",
            style={
                'textAlign': 'center', 
                'color': colors['secondary'], 
                'padding': '40px',
                'backgroundColor': colors['card_bg'],
                'borderRadius': '12px',
                'fontSize': '0.95rem'
            }
        )
    
    # Get the list of companies for this category
    companies = breakdown.iloc[0]['Companies']
    
    # Create a clean table of company names and locations
    return dash_table.DataTable(
        columns=[
            {"name": "Company Name", "id": "Company Name", "type": "text"},
            {"name": "Location", "id": "Company Location", "type": "text"}
        ],
        data=companies,
        style_header={
            'backgroundColor': colors['table_header'],
            'color': 'white',
            'fontWeight': '600',
            'textAlign': 'left',
            'border': 'none',
            'fontSize': '0.85rem',
            'textTransform': 'uppercase',
            'letterSpacing': '0.05em'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'border': 'none',
            'fontFamily': '"Inter", sans-serif',
            'borderBottom': f'1px solid {colors["table_border"]}'
        },
        style_data={
            'border': 'none'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': colors['table_row_odd']
            },
            {
                'if': {'row_index': 'even'},
                'backgroundColor': colors['table_row_even']
            },
            {
                'if': {'column_id': 'Company Name'},
                'fontWeight': '600',
                'color': colors['header']
            },
            {
                'if': {'column_id': 'Company Location'},
                'color': colors['secondary']
            }
        ],
        style_table={
            'overflowX': 'auto',
            'borderRadius': '12px'
        }
    )

# ===== 8. RUN APPLICATION =====
if __name__ == '__main__':
    app.run(debug=True, dev_tools_hot_reload=False)