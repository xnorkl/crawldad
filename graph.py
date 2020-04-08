import netcrawl as nc
import plotly.graph_objects as go
import networkx as nx

def net_graph(adj) -> dict:
  ''' given a dictionary list of nodes '''

  G = nx.Graph.from_dict_of_dicts(adj)
  pos = nx.spring_layout(G, k=0.5, iterations=50)
  for n, p in pos.items():
    G.nodes[n]['pos'] = p

  return G

def draw(graph):
  edge_trace = go.Scatter(
      x=[],
      y=[],
      line=dict(width=0.5,color='#888'),
      hoverinfo='none',
      mode='lines'
      )

  for edge in graph.edges():
    x0, y0 = graph.nodes[edge[0]]['pos']
    x1, y1 = graph.nodes[edge[1]]['pos']
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])

  nodes_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='Rainbow',
        reversescale=True,
        color=[],
        size=15,
        colorbar=dict(
            thickness=10,
            title='node Connections',
            xanchor='left',
            titleside='right'
        ),
        line=dict(width=0)
        )
    )

  for nodes in graph.nodes():
    x, y = graph.nodes[nodes]['pos']
    nodes_trace['x'] += tuple([x])
    nodes_trace['y'] += tuple([y])

  nodes_adjacencies = []
  nodes_text = []

  for nodes, adjacencies in enumerate(graph.adjacency()):
    nodes_adjacencies.append(len(adjacencies[1]))
    nodes_text.append('# of connections: '+str(len(adjacencies[1])))

    nodes_trace.marker.color = nodes_adjacencies
    nodes_trace.text = nodes_text

    fig = go.Figure(data=[edge_trace, nodes_trace],
        layout=go.Layout(
          title='<br>Network graph made with Python',
          titlefont_size=16,
          showlegend=False,
          hovermode='closest',
          margin=dict(b=20,l=5,r=5,t=40),
          annotations=[
            dict(text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
              showarrow=False,
              xref="paper", yref="paper",
              x=0.005, y=-0.002 )
            ],
          xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        )
    return fig


