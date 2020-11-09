import matplotlib.pyplot as plt
import plotly.graph_objects as go
import networkx as nx

def net_graph(edges):
  ''' given a dictionary list of nodes '''

  G = nx.Graph(edges)

  pos = nx.spring_layout(G)
  for n, p in pos.items():
    G.nodes[n]['pos'] = p

  return G

def write(graph):
  nx.nx_agraph.write_dot(graph, "test")

def plot(graph):
  plt.show()

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

  nodes_adjacencies = []
  nodes_text = []

  for nodes in graph.nodes():
    x, y = graph.nodes[nodes]['pos']
    nodes_trace['x'] += tuple([x])
    nodes_trace['y'] += tuple([y])

    nodes_text.append('host: {}'.format(nodes))

  for nodes, adjacencies in enumerate(graph.adjacency()):
    connections = len(adjacencies[1])
    nodes_adjacencies.append(connections)
    nodes_text.append('edges: {}'.format(connections))

    nodes_trace.marker.color = nodes_adjacencies
    nodes_trace.text = nodes_text

    fig = go.Figure(data=[edge_trace, nodes_trace],
        layout=go.Layout(
          title='<br>Mon Health Network Graph',
          titlefont_size=16,
          showlegend=False,
          hovermode='closest',
          margin=dict(b=20,l=5,r=5,t=40),
          annotations=[
            dict(
              showarrow=False,
              xref="paper", yref="paper",
              x=0.005, y=-0.002 )
            ],
          width=1800,
          height=1000,
          xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        )
    return fig


