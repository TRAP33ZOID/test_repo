import plotly.graph_objects as go

# Labels, parents, and values for the sunburst chart
labels = ["World", "Europe", "England", "France", "Asia", "Japan", "India", 
          "Alec Guinness", "Ben Kingsley", "Claudette Colbert", "Joan Fontaine", 
          "Julie Christie", "America", "Canada", "Mexico", "Anna Paquin", "Anthony Quinn"]

parents = ["", "World", "Europe", "Europe", "World", "Asia", "Asia", 
           "England", "England", "France", "Japan", "India", 
           "World", "America", "America", "Canada", "Mexico"]

values = [115, 87, 53, 4, 10, 4, 2, 
          1, 1, 1, 1, 1, 
          14, 11, 3, 1, 2]

# Create the sunburst chart
fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
))

# Update chart layout
fig.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
    sunburstcolorway=[
        "#345E80", "#00838F", "#00BFA5", "#ff6e40", "#d4e157", "#64B5F6"
    ],
    title="Non-U.S. Born Oscar Winners for Acting"
)

# Show the plot
fig.show()
