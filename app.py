import graph as g
import netcrawl as nc
import dash
import dash_core_components as dcc
import dash_html_components as html

edges = nc.edges()
graph = g.net_graph(edges)
g.plot(graph)

app = dash.Dash()
app.layout = html.Div([
  dcc.Graph(figure=g.draw(graph))
  ])

app.run_server(debug=True)
