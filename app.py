import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from metrics import rmse, cross_correlation, power_curve_similarity


pyron_results = pd.read_csv('data/pyron_model_results.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v5.15.4/css/all.css"])
server = app.server

# sidebar filter
sidebar = dbc.Col([
    html.Div(className='sidebar', children=[
        html.H3('Filter Data', style={'margin-top': '10px'})
    ]),

    dbc.Label('Select Model:', style={'margin-top': '20px'}),
    dcc.Dropdown(
        id='model-dropdown',
        value=None,
        options=[
            {'label': 'Physics-Based', 'value': 'phys'},
            {'label': 'Probabilistic', 'value': 'prob'},
            {'label': 'NQF-RNN', 'value': 'rnn'}
        ],
        clearable=True
    ),

    dbc.Label('Select Date Range:', style={'margin-top': '30px'}),

    # dmc.DatePicker(
    #     id='date-dropdown',
    #     type='range',
    #     minDate=pd.to_datetime(pyron_results['datetime'].min()),
    #     maxDate=pd.to_datetime(pyron_results['datetime'].max()),
    #     value=[pyron_results['datetime'].min(), pyron_results['datetime'].max()]
    # )

    dcc.DatePickerRange(
        id='date-dropdown',
        min_date_allowed=pyron_results['datetime'].min(),
        max_date_allowed=pyron_results['datetime'].max(),
        start_date=pyron_results['datetime'].min(),
        end_date=pyron_results['datetime'].max()
    ),

    # download data button
    dbc.Button([html.I(className="fas fa-download me-2"), 'Download Data'],
               id='download-button',
               color='primary', style={'margin-top': '30px', 'width': '100%'}),
    dcc.Download(id='download-dataframe-csv')

], width=3, style={'padding': '20px', 'backgroundColor': '#f8f9fa'})


# main content
content = dbc.Col([
    html.Div(className='app-header', children=[
        html.H1('Pyron Wind Farm - Power Generation Forecast', style={'textAlign': 'center', 'padding': '20px'})
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='time-series'), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='power-curve'),
                html.Div([
                    dbc.Label('Data Opacity:'),
                    dcc.Slider(id='opacity-slider', min=0, max=1, step=0.01, value=0.1,
                               marks={i/10: str(i/10) for i in range(11)})
                ], style={'width': '60%', 'padding-left': '80px'})
            ])
        ], width=7),
        dbc.Col(html.Div(id='metrics-display'), width=5, style={'padding-left': '50px'})
    ])

], width=9)

# app layout
app.layout = dbc.Container([
    dbc.Row([
        sidebar,
        content
    ])
], fluid=True)


# callbacks
@app.callback(
    [Output('time-series', 'figure'),
     Output('power-curve', 'figure'),
     Output('metrics-display', 'children')],
    [Input('model-dropdown', 'value'),
     Input('date-dropdown', 'start_date'),
     Input('date-dropdown', 'end_date'),
     Input('opacity-slider', 'value')]
)
def update_dashboard(selected_model, start_date, end_date, opacity):
    # date filter
    mask = (pd.to_datetime(pyron_results['datetime']) >= pd.to_datetime(start_date)) & (pd.to_datetime(pyron_results['datetime']) <= pd.to_datetime(end_date))
    filtered = pyron_results.loc[mask]

    # model filter
    model_labels = {
        None: '',
        'phys': 'Physics-Based Model Predictions vs ',
        'prob': 'Probabilistic Model Predictions vs ',
        'rnn': 'NQF-RNN Model Predictions vs '
    }

    cols = ['historical_power']
    if selected_model:
        cols.append(f'{selected_model}')

    df = filtered.melt(
        id_vars=['datetime', 'speed'],
        value_vars=cols,
        var_name='series',
        value_name='power'
    )
    df['datetime'] = pd.to_datetime(df['datetime'])


    # plot graphs
    time_series_fig = px.line(df, x='datetime', y='power', color='series', height=350,
                              labels={'datetime': 'Date', 'power': 'Power (MW)', 'series': '', 'historical_power': 'Historical Power'},
                              title=f'Time Series of {model_labels[selected_model]}Historical Power')
    time_series_fig.update_layout(
        title={'font': {'size': 24}, 'x': 0.5},
        margin={'t': 50},
        uirevision='0'
    )

    power_curve_fig = px.scatter(df, x='speed', y='power', color='series', opacity=opacity, height=400,
                                 labels={'speed': 'Wind Speed (m/s)', 'power': 'Power (MW)', 'series': ''},
                                 title='Power Curve Comparison')
    power_curve_fig.update_layout(
        title={'font': {'size': 24}, 'x': 0.45},
        margin={'t': 50, 'b': 20},
        uirevision='0'
    )

    # metrics
    if selected_model:
        rmse_value = rmse(df[df['series'] == 'historical_power']['power'], df[df['series'] == selected_model]['power'])
        cc_value = cross_correlation(df[df['series'] == 'historical_power']['power'], df[df['series'] == selected_model]['power'])
        sim_value = power_curve_similarity(df[df['series'] == 'historical_power']['speed'], df[df['series'] == 'historical_power']['power'], df[df['series'] == selected_model]['power'])

        metric_div = html.Div([
            html.H4('Metrics'),
            html.P(f'RMSE: {rmse_value:.4f}'),
            html.P(f'Cross Correlation: {cc_value:.4f}'),
            html.P(f'Power Curve Similarity: {sim_value:.4f}')
        ])
    else:
        metric_div = html.Div([
            html.H4('Metrics'),
            html.P('Select a model to view metrics.')
        ])

    return time_series_fig, power_curve_fig, metric_div

# download button callback
@app.callback(
    Output('download-dataframe-csv', 'data'),
    Input('download-button', 'n_clicks'),
    # [Input('model-dropdown', 'value'),
    #  Input('date-dropdown', 'start_date'),
    #  Input('date-dropdown', 'end_date')],
    prevent_initial_call=True
)
def download_data(n_clicks):
    # # date filter
    # mask = (pd.to_datetime(pyron_results['datetime']) >= pd.to_datetime(start_date)) & (pd.to_datetime(pyron_results['datetime']) <= pd.to_datetime(end_date))
    # filtered = pyron_results.loc[mask]

    # # model filter
    # if selected_model:
    #     filtered = filtered[['datetime', 'speed', 'historical_power', selected_model]]
    # else:
    #     filtered = filtered[['datetime', 'speed', 'historical_power']]

    # # could customize filename based on filters
    # return dcc.send_data_frame(filtered.to_csv, 'filtered_data.csv', index=False)
    return dcc.send_data_frame(pyron_results.to_csv, 'pyron_full_results.csv', index=False)



if __name__ == '__main__':
    app.run(debug=True)