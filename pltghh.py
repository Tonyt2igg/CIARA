import matplotlib.pyplot as plt
import networkx as nx

# Create directed graph
G = nx.DiGraph()

# Define nodes and their labels
nodes = {
    "input_x": "Input X (Real Image)",
    "gen_g": "Generator G (X → Y)",
    "fake_y": "Fake Y (Generated Sketch)",
    "disc_dy": "Discriminator DY",
    "cycle_x": "Cycle Consistency: Reconstructed X",
    "input_y": "Input Y (Sketch)",
    "gen_f": "Generator F (Y → X)",
    "fake_x": "Fake X (Reconstructed Real Image)",
    "disc_dx": "Discriminator DX",
    "cycle_y": "Cycle Consistency: Reconstructed Y",
}

# Add nodes to the graph
for key, label in nodes.items():
    G.add_node(key, label=label)

# Define edges (flow)
edges = [
    ("input_x", "gen_g"), ("gen_g", "fake_y"), ("fake_y", "disc_dy"),  # Input X Path
    ("fake_y", "cycle_x"), ("cycle_x", "input_x"),  # Cycle Consistency for X
    ("input_y", "gen_f"), ("gen_f", "fake_x"), ("fake_x", "disc_dx"),  # Input Y Path
    ("fake_x", "cycle_y"), ("cycle_y", "input_y"),  # Cycle Consistency for Y
    ("fake_y", "disc_dy"), ("fake_x", "disc_dx"),  # Real/Fake Discrimination
]

# Add edges to the graph
G.add_edges_from(edges)

# Plotting the graph
pos = {
    "input_x": (0, 2), "gen_g": (2, 2), "fake_y": (4, 2), "disc_dy": (6, 2), "cycle_x": (8, 2),
    "input_y": (0, 0), "gen_f": (2, 0), "fake_x": (4, 0), "disc_dx": (6, 0), "cycle_y": (8, 0),
}

plt.figure(figsize=(10, 5))
labels = nx.get_node_attributes(G, 'label')

# Draw nodes and edges
nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=2000)
nx.draw_networkx_labels(G, pos, labels, font_size=9)
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)

# Title and display
plt.title("CycleGAN Block Diagram: Real Image to Sketch and Back")
plt.axis('off')
plt.show()
