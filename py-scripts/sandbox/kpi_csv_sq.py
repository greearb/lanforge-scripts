#!/usr/bin/env python3

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import sqlite3
from  pathlib import Path


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# get a list of the kpi.csv files not the path needs to be bassed in
#path = Path('./2021-07-31-03-00-01_lf_check')
#path = Path('./test_data3')
path = Path('./lf_check_2')

kpi_list = list(path.glob('**/kpi.csv'))
print("kpi_list {}".format(kpi_list))

html_list = list(path.glob('**/index.html')) # the html is only index.html
print("html_list: {}".format(html_list))

df = pd.DataFrame()


# if there is no KPI then there is not an indication that
# a test was run so need to fix
#not if there is a kpi then there is an index.html
for kpi in kpi_list:
    # load data
    print("kpi {}".format(kpi))
    df_kpi_tmp = pd.read_csv(kpi, sep='\t')  # remove the index
    df_kpi_tmp['kpi_path'] = str(kpi).replace('kpi.csv','')  # only store the path to the kpi.csv file
    df_kpi_tmp = df_kpi_tmp.append(df_kpi_tmp, ignore_index=True)
    df = df.append(df_kpi_tmp, ignore_index=True)

#df.reset_index(drop=True)
print("df {data}".format(data=df))


# information on sqlite database
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

# write to database
conn = sqlite3.connect("qa_db") 
#df.to_sql("dp_table",conn,if_exists='append')
df.to_sql("dp_table",conn,if_exists='replace')
conn.close()


#https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html
conn = sqlite3.connect("qa_db")
df3 = pd.read_sql_query("SELECT * from  dp_table" ,conn)
#print(df3.head())
conn.close()

graph_group_list = list(df3['Graph-Group'])
graph_group_list = list(set(graph_group_list))  #remove duplicates 

test_tag_list = list(df3['test-tag'])
test_tag_list = list(set(test_tag_list))

i = 0 
plot_figure = []
children_div = []
for test_tag in test_tag_list:
    for group in graph_group_list:
        df_tmp = df3.loc[(df3['Graph-Group'] == str(group)) & (df3['test-tag'] == str(test_tag))]
        #print("test_tag: {} group: {} ".format(test_tag,group))
        #print("df_tmp[{}]: {}".format(i,df_tmp))
        i = i + 1 

        if df_tmp.empty == False:
            append_fig = (px.scatter(df_tmp, x="Date", y="numeric-score",
                 color="short-description", hover_name="short-description",
                 size_max=60)).update_traces(mode='lines+markers')
            print("{}".format(df_tmp['Graph-Group']))

            #print('{}'.format(type(append_fig)))
            # remove duplicates 
            test_rig_list = list(df_tmp['test-rig'])
            test_rig = list(set(test_rig_list))

            test_id_list = list(df_tmp['test-id'])
            test_id = list(set(test_id_list))

            kpi_path_list = list(df_tmp['kpi_path'])
            kpi_path = list(set(kpi_path_list))

            # get graph labels from dataframe
            units_list = list(df_tmp['Units'])
            units = list(set(units_list))

            append_fig.update_layout(
                title="{} : {} : {} : {}".format(test_id[0], group, test_tag, test_rig[0]),
                xaxis_title="Time",
                yaxis_title="{}".format(units[0]),
                xaxis = {'type' : 'date'}
            )
            # save the figure - this may need to be re-written
            print("kpi_path:{}".format(df_tmp['kpi_path']))
            #exit(1)
            png_path = os.path.join(kpi_path[0],"{}_{}_{}_{}_kpi.png".format(test_id[0], group, test_tag, test_rig[0]))
            print("png_path {}".format(png_path))
            append_fig.write_image(png_path,scale=1,width=1200,height=350)
            children_div.append(dcc.Graph(figure=append_fig))
            # for now it was designed if there is a kpi.csv then there is an index.html
            #https://dash.plotly.com/urls
            #html_src  = os.path.join(kpi_path[0],"index.html")
            # need to have a share available 
            #local_share = 'file://LAPTOP-T8B2MBJD/Users/chuck/git/lanforge-scripts/py-scripts/sandbox/lf_check_2'
            local_share = 'file://LAPTOP-T8B2MBJD/Users/chuck/git/lanforge-scripts/py-scripts/sandbox/'

            html_src  = os.path.join(local_share,kpi_path[0],"index.html")
            #children_div.append(html.A('link{}'.format(i), href='http://192.168.95.6/html-reports/lf_check--2021-08-03-12-47-01.html', target='_blank'))
            children_div.append(html.A(html_src, href=html_src, target='_blank'))
            #children_div.append(html.Br())
            #children_div.append(html.A('Navigate to google.com {}'.format(i), href='http://google.com', target='_blank'))
            #children_div.append(dcc.Location(id='dog',refresh=False))
            #children_div.append(dcc.Link('Link', href=html_src, target="_blank" ))
            # can add other information 


# access from server
# https://stackoverflow.com/questions/61678129/how-to-access-a-plotly-dash-app-server-via-lan


app.layout = html.Div([
    #  first instance 
    html.H1(children= "LANforge Testing",className="lanforge",
    #style={'color':'#00361c','text-align':'center'}),
    style={'color':'green','text-align':'center'}),
    html.H2(children= "Test Set #1",className="ts1",
    style={'color':'#00361c','text-align':'left'}),
    #test html.Div(children= images_div ), # images_div is already a list, the children = a list
    html.Div(children= children_div ), # images_div is already a list, the children = a list
    html.H2(children= "Test Set #2",className="ts2",
    style={'color':'#00361c','text-align':'left'}),
    #test html.Div(children= images_div, style={"maxHeight": "480px","overflow": "scroll"})
    # danger::: this will cause components to show up twice
    #html.Div(children= children_div, style={"maxHeight": "480px","overflow": "scroll"})
])


# scroll bars
'''
app.layout = html.Div([
    #  first instance 
    html.H1(children= "LANforge Testing",className="lanforge",
    #style={'color':'#00361c','text-align':'center'}),
    style={'color':'green','text-align':'center'}),
    html.H2(children= "Test Set #1",className="ts1",
    style={'color':'#00361c','text-align':'left'}),
    html.Div(children= images_div, style={"maxHeight": "480px","overflow": "scroll"} ), # images_div is already a list , the children = a list
    html.H2(children= "Test Set #2",className="ts2",
    style={'color':'#00361c','text-align':'left'}),
    html.Div(children= images_div, style={"maxHeight": "480px","overflow": "scroll"})
])

'''

if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host= '0.0.0.0', debug=True)  # host = '0.0.0.0'  allows for remote access
    