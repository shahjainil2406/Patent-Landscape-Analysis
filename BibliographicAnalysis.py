import math
import pandas as pd 
from heapq import nlargest  # to find n largest from dictionary
import itertools  
import matplotlib.pyplot as plt
from matplotlib.colors import DivergingNorm
import networkx as nx
#import seaborn as sns
#import pandas_bokeh
#import bokeh
#import pandas_profiling
#from bokeh.io import output_file, show
#from bokeh.palettes import Category20c
#from bokeh.plotting import figure
#from bokeh.transform import cumsum
#pd.set_option('plotting.backend', 'pandas_bokeh')
#pandas_bokeh.output_notebook()


def dataframe(filename):
    df = pd.read_csv(filename)
    return df

def assignees_plot(df, top_assignees):
    # converting from pandas Series to list after dropping Empty/Null values
    applicants = df['Applicants'].dropna().tolist()

    # making dictionary for assignee (key) -> # of patents (value) 
    applicants_dict = {}
    for i in applicants:
        if i not in applicants_dict.keys():
            applicants_dict[i] = 1
        else:
            applicants_dict[i] += 1
    
    # sorted dictionary from high number of patents to low
    applicants_dict_sorted = {k: v for k, v in sorted(applicants_dict.items(), key=lambda item: item[1], reverse = True)}

    # parameter to get top n assignees plot
    out_dict = dict(itertools.islice(applicants_dict_sorted.items(), top_assignees))  
    
    # plotting assignees vs number of patents 
    keys = list(out_dict.keys())
    values = list(out_dict.values())

    #df_assignee = pd.DataFrame({
    #    'Assignee' : keys, 
    #    '# of Patents' : values
    #})
    print('Top Assignees vs Number of Patents')
    plt.figure(figsize = (20, 15))
    #df_assignee.plot_bokeh.barh(x = 'Assignee', y = '# of Patents')
    plt.barh(keys, values, )
    plt.xlabel('Number of patents')
    plt.ylabel(f'Top {top_assignees} Assignees')
    plt.gca().invert_yaxis()
    plt.show()  

def inventors_plot(df, top_inventors):
    # converting from pandas Series to list after dropping Empty/Null values
    inventors = df["Inventors"].dropna().tolist()

    # making dictionary for assignee (key) -> # of patents (value) 
    inventors_dict = {}
    for j in inventors:
        inventor = j.split(";;")
        for i in inventor:
            if i not in inventors_dict.keys():
                inventors_dict[i] = 1
            else:
                inventors_dict[i] += 1
                
    # sorted dictionary from high number of patents to low
    inventors_dict_sorted = {k: v for k, v in sorted(inventors_dict.items(), key=lambda item: item[1], reverse = True)}

    # parameter to get top n invetors plot
    out_dict_inventor = dict(itertools.islice(inventors_dict_sorted.items(), top_inventors))  

    # plotting assignees vs number of patents 
    keys_inventors = list(out_dict_inventor.keys())
    values_inventors = list(out_dict_inventor.values())

    #df_inventor = pd.DataFrame({
    #    'Inventors' : keys_inventors, 
    #    '# of Patents' : values_inventors
    #})

    print('Top Inventors vs Number of Patents')
    plt.figure(figsize = (20, 15))
    #df_inventor.plot_bokeh.barh(x = 'Inventors', y = '# of Patents')
    plt.figure(figsize = (20, 15))
    plt.barh(keys_inventors, values_inventors)
    plt.xlabel('Number of patents')
    plt.ylabel(f'Top {top_inventors} Inventors')
    plt.gca().invert_yaxis()
    plt.show()

def juridiction_plot(df):
   # converting from pandas Series to list after dropping Empty/Null values
    juridictions = df['Jurisdiction'].dropna().tolist()

    # making dictionary for assignee (key) -> # of patents (value) 
    juridictions_dict = {}
    for i in juridictions:
        if len(i) <= 3:
            if i not in juridictions_dict.keys():
                juridictions_dict[i] = 1
            else:
                juridictions_dict[i] += 1

    # Pie Chart for Juridictions vs # of patents
    labels = list(juridictions_dict.keys())
    sizes = list(juridictions_dict.values())
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']

    print('Top Juridictions vs Number of Patents')
    plt.figure(figsize = (15, 15))
    plt.pie(sizes, labels = labels, colors = colors, autopct='%1.1f%%', shadow=True, startangle=140)

    plt.axis('equal')
    plt.show()

    #data = pd.Series(juridictions_dict).reset_index(name='value').rename(columns={'index':'country'})
    #data['angle'] = data['value']/data['value'].sum() * 2*math.pi
    #data['color'] = Category20c[len(juridictions_dict)]

    #p = figure(plot_height=350, title="Pie Chart", toolbar_location=None, tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))
    #p.wedge(x=0, y=1, radius=0.4, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'), line_color="white", fill_color='color', legend_field='country', source=data)
    #p.axis.axis_label=None
    #p.axis.visible=False
    #p.grid.grid_line_color = None

def inventors_network(df, top_pairs = 100):
    # converting from pandas Series to list after dropping Empty/Null values
    inventors = df["Inventors"].dropna().tolist()

    # making dictionary for assignee (key) -> # of patents (value) 
    inventors_net = {}
    for j in inventors:
        inventor = j.split(";;")
        for i in inventor:
            for j in inventor:
                if i != j:
                    key1 = i + ',' + j
                    key2 = j + ',' + i
                    if key1 not in inventors_net.keys() and key2 not in inventors_net.keys():
                        inventors_net[key1] = 1
                    elif key1 in inventors_net.keys():
                        inventors_net[key1] += 1
                    elif key2 in inventors_net.keys():
                        inventors_net[key2] += 1
    
    # sorted dictionary from high number of patents to low
    inventors_net_sorted = {k: v for k, v in sorted(inventors_net.items(), key=lambda item: item[1], reverse = True)}   

    # parameter to get top n invetors plot
    out_net_inventor = dict(itertools.islice(inventors_net_sorted.items(), top_pairs))  

    inventor1 = []
    inventor2 = []
    count = []
    for i in out_net_inventor:
        inven = i.split(',')
        inventor1.append(inven[0])
        inventor2.append(inven[1])
        count.append(out_net_inventor[i])

    df_net = pd.DataFrame({
        'inventor1' : inventor1,
        'inventor2' : inventor2,
        'patent_count' : count
    })

    print('Inventors Network')

    G = nx.Graph()
    G = nx.from_pandas_edgelist(df_net, 'inventor1', 'inventor2', edge_attr = 'patent_count')
    #count = [i['patent_count'] for i in dict(G.edges).values()]
    #labels = [i for i in dict(G.nodes).keys()]
    #labels = {i:i for i in dict(G.nodes).keys()}
    plt.figure(figsize = (15, 15))
    nx.draw_random(G, with_labels=True)
    plt.show()
    

def bibliographic_plots(filename, top_assignees = 20, top_inventors = 20, top_pairs = 100):
    df = dataframe(filename)

    # For top assignees vs number of patents
    assignees_plot(df, top_assignees)
    
    # For top Inventors vs number of patents
    inventors_plot(df, top_inventors)

    # For Juridictions vs number of patents 
    juridiction_plot(df)

    # Inventors Network
    inventors_network(df, top_pairs)


bibliographic_plots('trail_1_AI.csv', top_assignees=20, top_inventors=20, top_pairs=200)