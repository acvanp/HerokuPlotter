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
from flask import Flask, Response, request, url_for
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
    lvec = int(request.args.get("lvec", 25))
    abstates = int(request.args.get("abstates", 2))
    ntrials = int(request.args.get("ntrials", 160))
    s_changes = int(request.args.get("s_changes", 1))
    m_changes = int(request.args.get("m_changes", 0))

    # in a real app you probably want to use a flask template.
    return f"""
    <link rel="stylesheet" type="text/css" href="/static/CSS/main.css">
    
    <h4 class="top" >Markov Chain Plot</h4>
    <form method=get action="/">
    <input  id = "button" class="top" type=submit value="Update Plot">
    <img  class="top" id="content" src="/matplot-as-image-{lvec}-{abstates}-{ntrials}-{s_changes}-{m_changes}.png"
         alt="Markov chain plot as png"
         
    >
    <body>
        <p>Matrix Dimensions</p>
          <input name="lvec" type=number value="{lvec}" />
        <p>Number of Absorbing States</p>
      <input name="abstates" type=number value="{abstates}" />
        <p>Number of Trials (x-axis)</p>
      <input name="ntrials" type=number value="{ntrials}" />
        <p>Does the state matrix S get regenerated with random values when S stops changing? (1=yes, 0=no)</p>
      <input name="s_changes" type=number value="{s_changes}" />
        <p>Does the transition matrix P get regenerated with random values when S stops changing? (1=yes, 0=no)</p>
      <input name="m_changes" type=number value="{m_changes}" />
    </form>
    <a href="https://github.com/acvanp/HerokuPlotter">  Github page  </a>
    </body>
    
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
        if 1 in m[i]:
            axis.scatter(range(0,ntrials), ll[i], s = 2, c = "black")    

        else:
            axis.scatter(range(0,ntrials), ll[i], s = 16, color="none", edgecolor = color[i], linewidth=0.6)
            axis.set_xlabel("timesteps")
            axis.set_ylabel("state values")
            axis.set_title('Markov Chain Plot as PNG')

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")
