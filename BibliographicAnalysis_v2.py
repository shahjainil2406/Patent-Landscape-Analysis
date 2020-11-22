import math
import pandas as pd 
from heapq import nlargest  # to find n largest from dictionary
import itertools  
import matplotlib.pyplot as plt
from matplotlib.colors import DivergingNorm
import networkx as nx

def dataframe(filename):
    df = pd.read_csv(filename)
    return df

def assignees_plot(df, top_assignees):
    # converting from pandas Series to list after dropping Empty/Null values
    #applicants = df['Applicants'].dropna().tolist()
    assignees = df['assignee'][df['assignee'] != ''].dropna().tolist()
    # making dictionary for assignee (key) -> # of patents (value) 
    applicants_dict = {}
    for i in assignees:
        l = i.split(';;')
        for j in l:
            if j != '':
                if j in applicants_dict.keys():
                    applicants_dict[j] += 1
                else:
                    applicants_dict[j] = 1
    #for i in applicants:
    #    if i not in applicants_dict.keys():
    #        applicants_dict[i] = 1
    #    else:
    #        applicants_dict[i] += 1
    
    # sorted dictionary from high number of patents to low
    applicants_dict_sorted = {k: v for k, v in sorted(applicants_dict.items(), key=lambda item: item[1], reverse = True)}
    applicants_dict_sorted_items = applicants_dict_sorted.items()

    # parameter to get top n assignees plot
    out_dict = list(applicants_dict_sorted_items)[:top_assignees]
    
    # plotting assignees vs number of patents 
    keys = [k[0] for k in out_dict]
    values = [k[1] for k in out_dict]

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
    inventors = df['inventors'][df['inventors'] != ''].dropna().tolist()

    # making dictionary for assignee (key) -> # of patents (value) 
    inventors_dict = {}
    for i in inventors:
        l = i.split(';;')
        for j in l:
            if j != '':
                if j in inventors_dict.keys():
                    inventors_dict[j] += 1
                else:
                    inventors_dict[j] = 1
                
    # sorted dictionary from high number of patents to low
    inventors_dict_sorted = {k: v for k, v in sorted(inventors_dict.items(), key=lambda item: item[1], reverse = True)}
    inventors_dict_sorted_items = inventors_dict_sorted.items()

    # parameter to get top n invetors plot
    out_dict = list(inventors_dict_sorted_items)[:top_inventors]

    # plotting assignees vs number of patents 
    keys = [k[0] for k in out_dict]
    values = [k[1] for k in out_dict]

    print('Top Inventors vs Number of Patents')
    plt.figure(figsize = (20, 15))
    #df_inventor.plot_bokeh.barh(x = 'Inventors', y = '# of Patents')
    plt.figure(figsize = (20, 15))
    plt.barh(keys, values)
    plt.xlabel('Number of patents')
    plt.ylabel(f'Top {top_inventors} Inventors')
    plt.gca().invert_yaxis()
    plt.show()

def juridiction_plot(df):
   # converting from pandas Series to list after dropping Empty/Null values
    juridictions = df['juridiction'].dropna().tolist()

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

    print('Top Juridictions vs % of Patents')
    plt.figure(figsize = (15, 15))
    plt.pie(sizes, labels = labels, autopct='%1.1f%%', shadow=True, startangle=140)

    plt.axis('equal')
    plt.show()

def prior_country_plot(df):
   # converting from pandas Series to list after dropping Empty/Null values
    juridictions = df['prior_country'].dropna().tolist()

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
    #colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']

    print('Prior Country vs % of Patents')
    plt.figure(figsize = (15, 15))
    plt.pie(sizes, labels = labels, autopct='%1.1f%%', shadow=True, startangle=140)

    plt.axis('equal')
    plt.show()

def inventors_network(df, top_pairs = 100):
    # converting from pandas Series to list after dropping Empty/Null values
    inventors = df['inventors'][df['inventors'] != ''].dropna().tolist()

    # making dictionary for assignee (key) -> # of patents (value) 
    inventors_net = {}
    for j in inventors:
        inventor = j.split(";;")
        for i in inventor:
            if i != '':
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

    # For Prior Country vs % of patents
    prior_country_plot(df)

    # Inventors Network
    inventors_network(df, top_pairs)

#if __name__ == '__main__':
#    bibliographic_plots('ipa200409_v1.csv', top_assignees=20, top_inventors=20, top_pairs=200)