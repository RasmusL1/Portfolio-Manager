# -*- coding: utf-8 -*-


import dash
import dash_html_components as html
import pandas as pd
import dash_table as dt
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import fetch_data
import plotly.graph_objs as go


def get_data():
    data=fetch_data.fetch_stockdata()
    df = pd.DataFrame([i[0] for i in data])
    
    #### Some data manipulation
    df['market_cap']=df['market_cap'].str.replace('M', '0000').str.replace('.', '')
    df['market_cap']=df['market_cap'].str.replace('B', '0000000').str.replace('.', '')
    df['market_cap']=df['market_cap'].str.replace('T', '0000000000').str.replace('.', '')
    df['market_cap']=df['market_cap'].astype(float)
    df.loc[df.market_cap >= 0, 'company_size'] = "Small"
    df.loc[df.market_cap >= 1000000000, 'company_size'] = "Mid"
    df.loc[df.market_cap >= 10000000000, 'company_size'] = "Large"
    df.loc[df.market_cap >= 200000000000, 'company_size'] = "Mega"
    df['price']= round(df['bid'],2)
    
    df=df[['company', 'country', 'sector', 'price', 'wkn', 'ticker', 'company_size', 'spread', 'forw_pe', 'price_book', 'dividend_rate', 'profit_margin', 'momentum_30d', 'momentum_365d']]
    
    df.rename(columns={'company': 'Unternehmen', 'country': 'Land', 'sector': 'Sektor', 'price': 'Preis', 'wkn': 'WKN', 'ticker': 'Symbol',
           'company_size': 'Unternehmensgröße', 'spread': 'Spread', 'forw_pe': 'KGV', 'price_book': 'P/B', 'dividend_rate': 'Dividende %',
           'profit_margin' :'Profit Margin', 'momentum_30d': '30-Tage Perf.', 'momentum_365d': '1-Jahr Perf.'}, inplace=True)
    
    df['Spread']=round(df['Spread'],2)
    df['1-Jahr Perf.'] = round((pd.to_numeric(df['1-Jahr Perf.'],errors='coerce').fillna(0)),1)
    df['30-Tage Perf.'] = round((pd.to_numeric(df['30-Tage Perf.'],errors='coerce').fillna(0)),1)
    df['Dividende %']=df['Dividende %'].replace('N/A', '0%').str.replace(',', '.').str.replace('%', '').astype(float)
    #df['profit_margin']=df['profit_margin'].replace('N/A', '0%').str.replace(',', '.').str.replace('%', '').astype(float)
    df['P/B']=df['P/B'].replace('N/A', '0').str.replace('k', '').astype(float)
    df['KGV']=df['KGV'].replace('N/A', '0').str.replace('k', '').astype(float)  
    df=df[['Unternehmen', 'Land', 'Sektor', 'WKN', 'Symbol', 'Unternehmensgröße', 'KGV', 'P/B','Dividende %', '30-Tage Perf.', '1-Jahr Perf.', 'Preis', 'Spread']]
    return df

df=get_data()

df['count']=1
region_df=df.groupby(['Land']).sum()
region_df['region']=region_df.index
Sektor_df=df.groupby(['Sektor']).sum()
Sektor_df['Sektor']=Sektor_df.index
cap_df=df.groupby(['Unternehmensgröße']).sum()
cap_df['Unternehmensgröße']=cap_df.index
row1 = html.Tr([html.Td("Erw. KGV"), html.Td(round(df['KGV'].mean(),2))])
row2 = html.Tr([html.Td("P/B"), html.Td(round(df['P/B'].mean(),2))])
row3 = html.Tr([html.Td("Dividende %"), html.Td(round(df['Dividende %'].mean(),2))])
row4 = html.Tr([html.Td("Spread %"), html.Td(round(df['Spread'].mean(),2))])
row5 = html.Tr([html.Td("Performance 1 Jahr %"), html.Td(round(df['1-Jahr Perf.'].mean(),2))])
table_body = [html.Tbody([row1, row2, row3, row4, row5])]
df = df.drop('count', axis=1)
    
app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = 'Portfolio Manager'

SIDEBAR_STYLE_LEFT = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

SIDEBAR_STYLE_RIGHT = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar_left = html.Div(
    [
        html.H4("Portfolio Manager", className="display-8"),
        html.Hr(),
        html.Div([
            html.Div([ 
                html.Div(["Investitionssumme:"],style = {'padding': 5, 'width': 120}),
                dbc.Input(id="summe-input", value=10000, placeholder="10000 €", type="number", min=1, max=10000, step=1, style={'width': 140, 'textAlign':'center'}),
                ],className='col-1.7'),
            html.Div([ 
                html.Div(["Anzahl Einzelaktien:"],style = {'padding': 5, 'width': 160}),
                dbc.Input(id="aktien-input", value=30, placeholder="30", type="number", min=1, max=10000, step=1, style={'width': 60, 'textAlign':'center'}),
                ],className='col-2'),
        ],className = 'row', style = {'padding': 5}),
        html.Hr(),
        html.P(
            "Kriterien für ein diversifiziertes Portfolio", className="lead"
        ),
        html.Hr(),
        html.Div([
            html.Div([ 
            html.Div(["Unternehmensgröße:"],style = {'padding': 5, 'width': 120, 'font-size': 12}),
            dcc.Checklist(
                id="cap",
                options=[
                    {"label": " Small", "value": "Small"},
                    {"label": " Mid", "value": "Mid"},
                    {"label": " Large", "value": "Large"},
                    {"label": " Mega", "value": "Mega"},
                ],
                labelStyle={"display": "block"},
                value=['Small', 'Mid', 'Large', 'Mega'],
                ),
            ],className='col-1.6'),
            
            html.Div([ 
            html.Div(["Region:"],style = {'padding': 5, 'width': 120, 'font-size': 12}),   
            dcc.Checklist(
                id="reg",
                options=[
                    {"label": " USA", "value": "USA"},
                    {"label": " Europa", "value": "EU"},
                ],
                labelStyle={"display": "block"},
                value=['USA', 'EU'],
                ),
            ],className='col-2.1'),
            html.Div([ 
                html.Div(["Sektoren:"],style = {'padding': 5, 'width': 120, 'font-size': 12}),
                dcc.Dropdown(id='sector-input', 
                             options=[{'label': x, 'value': x} for x in list(set(list(set(df.Sektor.to_list()))) - set(['nan', '']))]+ [{'label': 'alle ', 'value': 'all_values'}], 
                             value='all_values',
                             multi=True),
            ],className='col-2.6'),
            
        ],className = 'row', style = {'padding': 5}),
        html.Hr(),

        ###
        
        
        html.Div([
            html.Div([ 
            html.Div(["Dividende:"],style = {'padding': 5, 'width': 100}),
            dbc.Input(id="dividend-input", value=0, type="number", min=0, max=20, step=0.1, style={'width': 80, 'textAlign':'center'}),
            ],className='col-1.7'),
            
            html.Div([
            html.Div(["Max. Kurs/Gewinn:"],style = {'padding': 5, 'width': 180}),
            dbc.Input(id="kgv-input", value=30, type="number", min=0, max=1000, step=1, style={'width': 80, 'textAlign':'center'}),
            ],className='col-2'),
            
        ],className = 'row', style = {'padding': 10}),
        
        html.Hr(),
        
        html.Div([
            html.Div([ 
                html.Div(["Max. Spread:"],style = {'padding': 5, 'width': 120}),
                dbc.Input(id="Spread-input", value=0.5, type="number", min=0, max=5, step=0.01, style={'width': 80, 'textAlign':'center'}),
                ],className='col-1.7'),

        ],className = 'row', style = {'padding': 10}),
        html.Hr(),
        html.Div([
            html.Div([
                    dbc.Button(                                                       
                            "Berechnen",
                                color="success",
                                id='submit-button'                                
                                ),
                    ],className='col-2'),
        ],className = 'row', style = {'padding': 15}), 
        
    ],
    style=SIDEBAR_STYLE_LEFT,
)

sidebar_right = html.Div(
    [
        html.H4("Portfolio Zusammensetzung", className="display-8"),
        html.Hr(),
        dbc.Table(table_body, bordered=True, id='übersicht'),
        
        
        

        #dcc.Graph(figure=px.pie(region_df, values='count', names='region', title='Region'),style={'display': 'inline-block','width': '100%', 'height': '30vh'}, id='region'),
        dcc.Graph(id='region', figure = {'data': [go.Pie(labels=region_df['region'],
                             values=region_df['count'],
                             title='Region',
                             showlegend=True,
                             textinfo='value')],
                            'layout': {
                                    'margin': {'l': 10,'r': 10,'b': 10,'t': 10,},
                                    'legend': {'x': 0, 'y': 1},
                                    }
                            },
                      style={'display': 'inline-block', 'width': '100%', 'height': '20%'},
                      ),
        dcc.Graph(figure = {'data': [go.Pie(labels=Sektor_df['Sektor'],
                             values=Sektor_df['count'],
                             title='Sektoren',
                             showlegend=False,
                             textinfo='value')],
                            'layout': {
                                    'margin': {'l': 10,'r': 10,'b': 10,'t': 10,},
                                    'legend': {'x': 0, 'y': 1},
                                    }
                            },
                      style={'display': 'inline-block', 'width': '100%', 'height': '20%'},
                      id='Sektor'),
        dcc.Graph(figure = {'data': [go.Pie(labels=cap_df['Unternehmensgröße'],
                             values=cap_df['count'],
                             title='Unternehmensgröße',
                             showlegend=True,
                             textinfo='value')],
                            'layout': {
                                    'margin': {'l': 10,'r': 10,'b': 10,'t': 10,},
                                    'legend': {'x': 0, 'y': 1},
                                    }
                            },
                      style={'display': 'inline-block', 'width': '100%', 'height': '20%'},
                      id='capsize'),
        #dcc.Graph(figure=px.pie(Sektor_df, values='count', names='Sektor', title='Sektor'),style={'display': 'inline-block', 'width': '100%', 'height': '40vh'}, id='Sektor')

        

    ],
    style=SIDEBAR_STYLE_RIGHT,
)

table=html.Div([                                             
    dt.DataTable(id= 'table1', 
                 #editable=True, 
                 columns=[{"name": i, "id": i} for i in (df.columns)],
                 data=df.to_dict('rows'),
                 row_deletable=False, 
                 sort_action="native", 
                 sort_mode="multi",                                  
                 style_cell={'textAlign': 'left',
                             'fontSize':12,
                             'padding-left': '3px',
                             'font-family':'Helvetica'},
                 style_as_list_view=True,
                 style_header={
                     'backgroundColor': 'rgb(230, 230, 230)',
                     'fontWeight': 'bold'},)
                ])


app.layout = dbc.Container([table, sidebar_left, sidebar_right])

@app.callback ([dash.dependencies.Output('table1','data'),
                dash.dependencies.Output('table1','columns'),
                dash.dependencies.Output('region','figure'),
                dash.dependencies.Output('Sektor','figure'),
                dash.dependencies.Output('capsize','figure'),
                dash.dependencies.Output('übersicht','children'),
                ],

            [Input('submit-button','n_clicks')],
            [State('table1', 'data'),
             State('table1', 'columns'),
             State('Spread-input', 'value'),
             State('cap', 'value'),
             State('summe-input', 'value'),
             State('aktien-input', 'value'),
             State('dividend-input', 'value'),
             State('kgv-input', 'value'),
             State('sector-input', 'value'),
             
            ])

def update_datatable(n_clicks,rows, columns, Spread, cap_list, summe, aktien_anzahl, dividend_rate, kgv_rate, sectors):         
    if n_clicks:
        
        #### get data from table

        df = pd.DataFrame(rows, columns=[c['name'] for c in columns]) 
        
        ### filter based on chosen criteria
        df=df.loc[df['Spread'] <= Spread]
        df=df.loc[df['Dividende %'] >= dividend_rate]
        df=df.loc[df['KGV'] <= kgv_rate]
        if not 'all_values' in sectors:
            df=df[df['Sektor'].isin(sectors)]
        
        df=df[df['Unternehmensgröße'].isin(cap_list)]        
        
        
        df['count']=1
        region_df=df.groupby(['Land']).sum()
        region_df['region']=region_df.index
        Sektor_df=df.groupby(['Sektor']).sum()
        Sektor_df['Sektor']=Sektor_df.index
        cap_df=df.groupby(['Unternehmensgröße']).sum()
        cap_df['Unternehmensgröße']=cap_df.index
        
        df = df.sample(frac=1).reset_index(drop=True)
        df=df.head(aktien_anzahl)
        pro_aktie=summe/len(df)
        df['Anzahl']=round(pro_aktie/df['Preis'],0)
        df = df.drop('count', axis=1)

        data = df.to_dict('rows')
        
        
        
        #### update table and figures after 'submit' button
        columns =  [{"name": i, "id": i,'editable':(i=='Points', 'Max %')} for i in (df.columns)]
        row1 = html.Tr([html.Td("Erw. KGV"), html.Td(round(df['KGV'].mean(),2))])
        row2 = html.Tr([html.Td("P/B"), html.Td(round(df['P/B'].mean(),2))])
        row3 = html.Tr([html.Td("Dividende %"), html.Td(round(df['Dividende %'].mean(),2))])
        row4 = html.Tr([html.Td("Spread %"), html.Td(round(df['Spread'].mean(),2))])
        row5 = html.Tr([html.Td("Performance 1 Jahr %"), html.Td(round(df['1-Jahr Perf.'].mean(),2))])
        table_body = [html.Tbody([row1, row2, row3, row4, row5])]
        
        figure1= {'data': [go.Pie(labels=region_df['region'],
                             values=region_df['count'],
                             title='Region',
                             showlegend=True,
                             textinfo='value')],
                            'layout': {
                                    'margin': {'l': 10,'r': 10,'b': 10,'t': 10,},
                                    'legend': {'x': 0, 'y': 1},
                                    }},
        figure2= {'data': [go.Pie(labels=Sektor_df['Sektor'],
                             values=Sektor_df['count'],
                             title='Sektoren',
                             showlegend=False,
                             textinfo='value')],
                            'layout': {
                                    'margin': {'l': 10,'r': 10,'b': 10,'t': 10,},
                                    'legend': {'x': 0, 'y': 1},
                                    }},
        figure3= {'data': [go.Pie(labels=cap_df['Unternehmensgröße'],
                             values=cap_df['count'],
                             title='Unternehmensgröße',
                             showlegend=True,
                             textinfo='value')],
                            'layout': {
                                    'margin': {'l': 10,'r': 10,'b': 10,'t': 10,},
                                    'legend': {'x': 0, 'y': 1},
                                    }},
        
        
        return data, columns, figure1[0], figure2[0], figure3[0], table_body
        
if __name__ == '__main__':
    app.run_server()