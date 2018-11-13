
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import pickle
import base64
import os
import flask


# Load candidate data
def init_dash(flask_app):
    with open('dash/Jon Ossoff.pickle', 'rb') as pickle_file:
        cand = pickle.load(pickle_file)

    print(cand['cand_strrep'])
    print("here")
    all_cands = [ cand ]  # TODO: Load in the rest! Lazily? Probably.
    cand_data = {c: cdata for c, cdata in zip(map(lambda x: x['cand_strrep'],
                                                  all_cands), all_cands)}
    #for k in cand_data:
        #print(f'Loaded candidate: {k}')

    all_2018_cands = pd.read_pickle('dash/all_2018_cands.pickle')
    #print(f'Loaded {len(all_2018_cands)} potential candidates')

    css_directory = os.getcwd()
    stylesheets = ['dash/style.css']
    static_css_route = '/static/'

    external_stylesheets = ['http://169.62.194.155:8050/static/style.css']
    #app = dash.Dash(__name__, server=application)
    app = dash.Dash(__name__, url_base_pathname='/dash/',  external_stylesheets=external_stylesheets, server=flask_app)

    available_candidates = all_2018_cands['strrep'].unique()

    app.layout = html.Div([
        html.Div([

            html.Div([
                dcc.Dropdown(
                    id='crossfilter-candidate',
                    options=[{'label': i, 'value': i} for i in available_candidates],
                    value='Jon Ossoff (D): GA06'  # TODO: IP Geolocation
                )
            ],
            style={'width': '49%', 'display': 'inline-block'}),

        ], style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '10px 5px'
        }),

        html.Div([
            html.Img(id='candidate-img',
                     src='data:image/png;base64,{}'.format(base64.b64encode(open('dash/ossoff.jpg', 'rb').read()).decode('utf-8', 'ignore')),
                     height='50')
        ], style={'width': '5%', 'display': 'inline-block', 'padding': '10 20'}),
     
        html.Div([
           html.H2(id='candidate-header',
                    children='Jon Ossoff (D): GA06')
        ], style={'width': '94%', 'display': 'inline-block', 'padding': '0 20'}),


        html.Div([
            dcc.Graph(
                id='candidate-pac-contribs',
                hoverData={'points': [{'customdata': 'C00504530'}]}
            ),
            dcc.Graph(id='candidate-indiv-contribs')
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),

        html.Div([
            dcc.Graph(id='pacbreakdown-indiv-contribs'),
            dcc.Graph(id='pacbreakdown-pac-contribs'),
        ], style={'display': 'inline-block', 'width': '49%'})
    ])


    @app.server.route('{}<stylesheet>'.format(static_css_route))
    def serve_stylesheet(stylesheet):
        if stylesheet not in stylesheets:
            return {}
        return flask.send_from_directory(css_directory, stylesheet)

    @app.callback(
        dash.dependencies.Output('candidate-header', 'children'),
        [dash.dependencies.Input('crossfilter-candidate', 'value')])
    def update_candidate_header(candidate_strrep):
        return candidate_strrep

    @app.callback(
        dash.dependencies.Output('candidate-img', 'src'),
        [dash.dependencies.Input('crossfilter-candidate', 'value')])
    def update_candidate_header(candidate_strrep):
        if candidate_strrep == 'Jon Ossoff (D): GA06':
            return 'data:image/png;base64,{}'.format(base64.b64encode(open('ossoff.jpg', 'rb').read()).decode('utf-8', 'ignore'))
        else:
            return {}


    @app.callback(
        dash.dependencies.Output('candidate-indiv-contribs', 'figure'),
        [dash.dependencies.Input('crossfilter-candidate', 'value')])
    def update_candidate_indiv_contribs(candidate_strrep):
        try:
            this_cand_data = cand_data[candidate_strrep]
        except:
            return {}
            print('Candidate not found in cand_data, using Jon Ossoff')
            this_cand_data = cand_data['Jon Ossoff (D): GA06']

        return {
            'data': [go.Bar(
                x=this_cand_data['indiv_support_direct']['donor_name'],
                y=this_cand_data['indiv_support_direct']['total_amt'],
                text=this_cand_data['indiv_support_direct']['indivs_contribid']
            )],
            'layout': go.Layout(
                title='Individual contributions to candidate',
                yaxis={
                    'title': 'Amount donated'
                },
                margin={'l': 60, 'b': 130, 't': 30, 'r': 30},
                height=350
            )
        }

    @app.callback(
        dash.dependencies.Output('candidate-pac-contribs', 'figure'),
        [dash.dependencies.Input('crossfilter-candidate', 'value')])
    def update_candidate_pac_contribs(candidate_strrep):
        try:
            this_cand_data = cand_data[candidate_strrep]
        except:
            return {}
            print('Candidate not found in cand_data, using Jon Ossoff')
            this_cand_data = cand_data['Jon Ossoff (D): GA06']

        return {
            'data': [go.Bar(
                x=this_cand_data['pac_support_direct']['cmte_name'],
                y=-this_cand_data['pac_support_direct']['pac_bad'],
                text=this_cand_data['pac_support_direct']['cmteid'],
                customdata=this_cand_data['pac_support_direct']['cmteid'],
                name='Contributions against',
                opacity=0.6
            ), go.Bar(
                x=this_cand_data['pac_support_direct']['cmte_name'],
                y=this_cand_data['pac_support_direct']['pac_good'],
                text=this_cand_data['pac_support_direct']['cmteid'],
                customdata=this_cand_data['pac_support_direct']['cmteid'],
                marker={'color': '#1f77b4'},
                name='Contributions for'
            )],
            'layout': go.Layout(
                title='Candidate contributions from PACs',
                yaxis={
                    'title': 'Amount donated'
                },
                margin={'l': 60, 'b': 130, 't': 30, 'r': 30},
                height=350,
                barmode='stack',
                hovermode='closest'
            )
        }



    @app.callback(
        dash.dependencies.Output('pacbreakdown-pac-contribs', 'figure'),
        [dash.dependencies.Input('candidate-pac-contribs', 'hoverData'),
         dash.dependencies.Input('crossfilter-candidate', 'value')])
    def update_pacpac_contribs(hoverData, candidate_strrep):
        try:
            this_cand_data = cand_data[candidate_strrep]
        except:
            return {}
            print('Candidate not found in cand_data, using Jon Ossoff')
            this_cand_data = cand_data['Jon Ossoff (D): GA06']

        hoverpacid = hoverData['points'][0]['customdata']
        hoverpacdata = this_cand_data['cmte_pacpacs'][hoverpacid]

        psd = this_cand_data['pac_support_direct']
        hoverpacname = psd[psd['cmteid'] == hoverpacid]['cmte_name'].iloc[0]
        title = hoverpacname
        return {
            'data': [go.Bar(
                x=hoverpacdata['name'],
                y=hoverpacdata['amount_received_from']
             )],
             'layout': {
                 'yaxis': {
                     'title': 'Amount donated'
                 },
                 'annotations': [{
                    'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                    'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                    'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                    'text': 'PAC contributions for ' + title 
                 }],
                 'height': 350,
                 'margin': {'l': 60, 'b': 130, 'r': 30, 't': 30}
             }
         }
                 
    @app.callback(
        dash.dependencies.Output('pacbreakdown-indiv-contribs', 'figure'),
        [dash.dependencies.Input('candidate-pac-contribs', 'hoverData'),
         dash.dependencies.Input('crossfilter-candidate', 'value')])
    def update_pacindiv_contribs(hoverData, candidate_strrep):
        try:
            this_cand_data = cand_data[candidate_strrep]
        except:
            return {}
            print('Candidate not found in cand_data, using Jon Ossoff')
            this_cand_data = cand_data['Jon Ossoff (D): GA06']

        hoverpacid = hoverData['points'][0]['customdata']
        hoverpacdata = this_cand_data['cmte_indivs'][hoverpacid]

        psd = this_cand_data['pac_support_direct']
        hoverpacname = psd[psd['cmteid'] == hoverpacid]['cmte_name'].iloc[0]
        title = hoverpacname
        return {
            'data': [go.Bar(
                x=hoverpacdata['contributor'],
                y=hoverpacdata['total_amt']
             )],
             'layout': {
                 'yaxis': {
                     'title': 'Amount donated'
                 },
                 'annotations': [{
                    'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                    'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                    'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                    'text': 'Individual contributions for ' + title
                 }],
                 'height': 350,
                 'margin': {'l': 60, 'b': 120, 'r': 10, 't': 30}
             }
         }

    return app

#if __name__ == '__main__':
#    app.run_server(debug=True, host='0.0.0.0')
