# -*- coding: utf-8 -*-
"""
Created on Fri May 22 23:05:06 2020

@author: Lenovo
"""



"""
Created on Fri May 22 22:35:51 2020

@author: Lenovo
"""

""" Shows how to use flask and matplotlib together.
Shows SVG, and png.
The SVG is easier to style with CSS, and hook JS events to in browser.
python3 -m venv venv
. ./venv/bin/activate
pip install flask matplotlib
python flask_matplotlib.py
"""
import io
from flask import Flask, Response, request
from flask_table import Table, Col
from matplotlib.backends.backend_agg import FigureCanvasAgg
import random
import numpy as np
import matplotlib.pyplot as plt
from random import randint
from pandas import DataFrame
from matplotlib.figure import Figure


app = Flask(__name__)


@app.route("/")
def index():
    """ Returns html with the img tag for your plot.
    """
    lvec = int(request.args.get("lvec", 10))
    abstates = int(request.args.get("abstates", 3))
    ntrials = int(request.args.get("ntrials", 100))
    s_changes = int(request.args.get("s_changes", 1))
    m_changes = int(request.args.get("m_changes", 0))

    # in a real app you probably want to use a flask template.
    return f"""
    <h1>Flask and matplotlib</h1>
    <h2>Markov Chan Plot</h2>
        <h4>Matrix Dimensions</h1>
    <form method=get action="/">
      <input name="lvec" type=number value="{lvec}" />
        <h4>Number of Absorbing States</h1>
      <input name="abstates" type=number value="{abstates}" />
        <h4>Number of Trials (x-axis)</h1>
      <input name="ntrials" type=number value="{ntrials}" />
        <h4>Does the state matrix S get regenerated with random values when S stops changing? (1=yes, 0=no)</h1>
      <input name="s_changes" type=number value="{s_changes}" />
        <h4>Does the transition matrix P get regenerated with random values when S stops changing? (1=yes, 0=no)</h1>
      <input name="m_changes" type=number value="{m_changes}" />
      <input type=submit value="Update Plot">
    </form>
    <h3>Plot as a png</h3>
    <img src="/matplot-as-image-{lvec}-{abstates}-{ntrials}-{s_changes}-{m_changes}.png"
         alt="Markov chain plot as png"
         height="500"
    >
    """
    # from flask import render_template
    # return render_template("yourtemplate.html", num_x_points=num_x_points)



@app.route("/matplot-as-image-<int:lvec>-<int:abstates>-<int:ntrials>-<int:s_changes>-<int:m_changes>.png")


# function for producing a transition state matrix
# with one or more than one absorbing states
# define a function that makes an absorbing transition matrix


# Run the experiment over so many trials
# Define the number of trials

def markov_chain_plotter(lvec=10, abstates=3, ntrials=100, s_changes=1, m_changes=0):

    
    def absorbing_matrix(lvec, abstates): 
        lvec = lvec # vector length
        m = list()
    
        for k in range(0,lvec): # len.vector - 1 in order to have a spare state for the absorbing state
            v = [0]
            v = np.append(v, random.random())
            for i in range(0,lvec-2):
                if i == lvec - 1:
                    v = np.append(v, 1-sum(v))
                else: v = np.append(v, random.uniform(0,1-sum(v)))
            random.shuffle(v) # shuffle v
            m = np.append(m, v)
    
        shape = (lvec, lvec )
        m = m.reshape( shape )
    
        abstates = abstates
        abstates = random.sample(range(0,lvec), k= abstates) 
    
        for i in range(0, len(abstates)):
            x = int(abstates[i])
            m[x][range(0,len(m))] = 0
            m[abstates[i]][abstates[i]] = 1     
        
        #m = np.transpose(m)
        return m
    
    m = absorbing_matrix(lvec, abstates)
    
    #ntrials = ntrials # Write value here
    
    # state matrix s
    s = random.sample(range(1,99), k = lvec )
    
    #return str(m,s)
    
    ll = list(s)
    
    s_current = s
    
    for i in range(1,ntrials):
        s = np.dot(m,s) # matrix multiplicatoin is %*%
        ll = np.append(ll,s)
        
        if s_changes == 1:
            if all(np.round(s, 1) == np.round(s_current, 1)):
                s = random.sample(range(1,99), k = lvec )
        s_current = s
        if m_changes == 1:
            if all(np.round(s, 1) == np.round(s_current, 1)):
                m = absorbing_matrix(lvec, abstates)
    
    shape = (ntrials, lvec)
    ll = ll.reshape(shape)
    
#    from pandas import DataFrame
    ll = DataFrame(np.array(ll))
    
#    import matplotlib.pyplot as plt
#    from random import randint
    
    color = []
    
    for i in range(0,lvec):
        color.append('#%06X' % randint(0, 0xFFFFFF))

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    
    for i in range(0,lvec):
        if sum(m[i]) == 1:
                 axis.scatter(range(0,ntrials), ll[i], s = 2, c = "black")    
        else:
            axis.scatter(range(0,ntrials), ll[i], s = 15, color="none", edgecolor = color[i])
 
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")
