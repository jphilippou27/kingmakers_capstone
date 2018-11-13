
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import pickle


# Load candidate data
with open('Jon Ossoff.pickle', 'rb') as pickle_file:
    cand = pickle.load(pickle_file)
print(cand['cand_strrep'])
all_cands = [ cand ]  # TODO: Load in the rest! Lazily? Probably.
cand_data = {c: cdata for c, cdata in zip(map(lambda x: x['cand_strrep'],
                                              all_cands), all_cands)}
for k in cand_data:
    print(f'Loaded candidate: {k}')

all_2018_cands = pd.read_pickle('all_2018_cands.pickle')
print(f'Loaded {len(all_2018_cands)} potential candidates')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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


@app.callback(
    dash.dependencies.Output('candidate-indiv-contribs', 'figure'),
    [dash.dependencies.Input('crossfilter-candidate', 'value')])
def update_candidate_indiv_contribs(candidate_strrep):
    try:
        this_cand_data = cand_data[candidate_strrep]
    except:
        print('Candidate not found in cand_data, using Jon Ossoff')
        this_cand_data = cand_data['Jon Ossoff (D): GA06']

    return {
        'data': [go.Bar(
            x=this_cand_data['indiv_support_direct']['donor_name'],
            y=this_cand_data['indiv_support_direct']['total_amt'],
            text=this_cand_data['indiv_support_direct']['indivs_contribid']
        )],
        'layout': go.Layout(
            xaxis={
                'title': 'Contributions from individuals and corporations'
            },
            yaxis={
                'title': 'Amount donated'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }

@app.callback(
    dash.dependencies.Output('candidate-pac-contribs', 'figure'),
    [dash.dependencies.Input('crossfilter-candidate', 'value')])
def update_candidate_pac_contribs(candidate_strrep):
    try:
        this_cand_data = cand_data[candidate_strrep]
    except:
        print('Candidate not found in cand_data, using Jon Ossoff')
        this_cand_data = cand_data['Jon Ossoff (D): GA06']

    return {
        'data': [go.Bar(
            x=this_cand_data['pac_support_direct']['cmte_name'],
            y=-this_cand_data['pac_support_direct']['pac_bad'],
            text=this_cand_data['pac_support_direct']['cmteid'],
            customdata=this_cand_data['pac_support_direct']['cmteid'],
            marker={'color': 'red'}
        ), go.Bar(
            x=this_cand_data['pac_support_direct']['cmte_name'],
            y=this_cand_data['pac_support_direct']['pac_good'],
            text=this_cand_data['pac_support_direct']['cmteid'],
            customdata=this_cand_data['pac_support_direct']['cmteid']
        )],
        'layout': go.Layout(
            xaxis={
                'title': 'Contributions from PACs'
            },
            yaxis={
                'title': 'Amount donated'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
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
             'xaxis': {
                 'title': f'Secondary contributor PACs (via {title})'
             },
             'yaxis': {
                 'title': 'Amount donated'
             },
             'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
             }],
             'height': 225,
             'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10}
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
             'xaxis': {
                 'title': f'Secondary contributor individuals (via {title})'
             },
             'yaxis': {
                 'title': 'Amount donated'
             },
             'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
             }],
             'height': 225,
             'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10}
         }
     }


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
