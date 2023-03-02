import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


import plotly as py
#import plotly.graph_objs as go
from plotly.subplots import make_subplots


#create plotly plot with 3 subplots
fig = make_subplots(
    rows=1, 
    cols=3, 
    #subplot_titles=('Shop activity per day'), 
    shared_yaxes=False,
    subplot_titles=('New Items',  'Sold Items', ' Number of Reviews')
)

import numpy as np
x = np.linspace(0, 12*np.pi)

fig.add_scatter(x=x, y=np.sin(x), name='sin(x)', row=1, col=1)
fig.add_scatter(x=x, y=np.cos(x), name='cos(x)', row=1, col=2)
fig.add_scatter(x=x, y=np.cos(x)+np.sin(x), name='sin(x)+cos(x)', row=1, col=3)


# Once the fig object has been created, and the traces have been added, 
# one can update any aspect of it by concatenating the .update methods.
# Here are some of the most common use cases:
(
    fig
    .update_layout(
        title='',
        showlegend=True,
        width=900,
        height=500,
    )
    .update_xaxes(
        title='x',
    )
    .update_yaxes(
        title='f(x)',
        col=1,
    )
    .update_traces(
        mode='lines+markers',
    )
)



#create app layout

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")


#st.title('Shop Activity Follower')
st.markdown("<h1 style='text-align: center; color: white;'>Shop Activity Follower</h1>", unsafe_allow_html=True)

st.plotly_chart(fig, theme=None, use_container_width=True)