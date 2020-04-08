import graph as g
import dash
import dash_core_components as dcc
import dash_html_components as html

edges = [('a','b'),('a','c'),('d','c'),('c','b')]
graph = g.gen_graph(edges)

app = dash.Dash()
app.layout = html.Div([
  dcc.Graph(figure=g.draw(graph))
  ])

app.run_server(debug=True)
