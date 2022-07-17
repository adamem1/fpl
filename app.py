# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_table

df = pd.read_csv('/home/adam/jupyter/fpl/final_expected_data2.csv')

# TODO: Drop a lot of shit from this table you don't care about
# TODO: Make table filterable with callbacks
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


app = dash.Dash(__name__)

fig = px.scatter(df,
                 x='total_points',
                 y='Expected Value Above Average',
                 size='minutes',
                 render_mode='svg',
                 color='position',
                 hover_name='name',
                 hover_data=['cost','npxg_90','xA_90'])

fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="red")
fig.update_layout(showlegend=False)

app.layout = html.Div(children=[
    html.Div(className="intro", children=[
    html.H1(
        children='FPL + FBRef xG/xA Stats',
        style={
            'textAlign': 'center'
        }
    ),

    # TODO: Are we usually actually expected value above average? If so link to it. if not we should.
    # TODO: Add title to graph
    dcc.Markdown('''
    	### Intro

    	This is a first attempt at organizing some stats from last year + this year\'s player pricing. The graph and table are sortable and filterable by position.
    	Table is filterable. 
    	Working on making some pre-define filters because right now trying to find a player or sort by defenders isn't great. Also, let's ignore the CSS for right now. 
    	''', style={
        'textAlign': 'left',
        'padding': 25

    })]),

# TODO: Put dropdown and slider on the same horizontal line using float https://codepen.io/nitinhepat/pen/ZEbKaRZ?ref=morioh.com&utm_source=morioh.com
    html.Div(className="float-container", children=[
    html.Div(className="float-child", children=[
        dcc.Markdown('''
        (Optional): Select a position...
        ''', style={
                    'textAlign': 'left',
                }),
        dcc.Dropdown(
            df['position'].unique(),
            'Player Position',
            placeholder='Select a position',
            id='position-selector'
        ),
]),

    html.Div(className="float-child", children=[
        dcc.Markdown('''
        (Optional): Select a cost
        ''', style={
            'textAlign': 'left',
        }),
        dcc.Slider(
            df['cost'].min(),
            df['cost'].max(),
            step=None,
            value=df['cost'].max(),
            marks={str(cost): str(cost) for cost in df['cost'].unique()},
            id='cost-slider',
            tooltip={"placement": "bottom", "always_visible": True}
            )]),
    html.Div(className="graph", children=[
    dcc.Graph(
        id='graph-with-slider',
        figure=fig
    )]),


# TODO: Add drop-downs
    html.Div(className="table", children=[
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i}
                     for i in df.columns],
            data=df.to_dict('records'),
            sort_action="native",
            sort_mode="multi",
            filter_action="native",
            style_cell={
            },
            style_table={'height': '300px', 'overflowY': 'auto'}
        )
    ])
    ]),
])

# TODO: Graph FPL League performance over time
# TODO: Table of top points getters
# TODO: Table of who's overperforming xG
# TODO: Table of clubs by xG and xGA
# TODO: Run nginx proxy

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('position-selector', 'value'),
    Input('cost-slider', 'value'))
def update_figure(selected_position, selected_cost):
    if (selected_position is None or selected_position == 'Player Position'):
        position_filtered_df = df
    else:
        position_filtered_df = df[df.position == selected_position]
    cost_filtered_df = position_filtered_df[df.cost <= selected_cost]
    fig = px.scatter(cost_filtered_df,
                     x='total_points',
                     y='Expected Value Above Average',
                     size='minutes',
                     render_mode='svg',
                     color='position',
                     hover_name='name',
                     hover_data=['cost','npxg_90','xA_90'])
    fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="red")
    fig.update_layout(showlegend=False)
    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
