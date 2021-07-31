# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

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
path = Path('./2021-07-31-03-00-01_lf_check')

kpi_list = list(path.glob('**/kpi.csv'))
#print(kpi_list)

df = pd.DataFrame()

for kpi in kpi_list:
    # load data
    append_df = pd.read_csv(kpi, sep='\t')
    df = df.append(append_df, ignore_index=True)

#print("df {data}".format(data=df))

# information on sqlite database
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

# write to database
conn = sqlite3.connect("qa_db") 
#df.to_sql("dp_table",conn,if_exists='append')
df.to_sql("dp_table",conn,if_exists='replace')
conn.close()


#https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html
conn = sqlite3.connect("qa_db")
df2 = pd.read_sql_query("SELECT * from dp_table" ,conn)
#print(df2.head())
conn.close()
#print(df2)


conn = sqlite3.connect("qa_db")
df3 = pd.read_sql_query("SELECT * from  dp_table" ,conn)
#print(df3.head())
conn.close()

# works df4 = df3.loc[(df3['Graph-Group'] == 'CX-Time') & (df3['test-tag'] == 'ATH10K(9984)')]
# works df4 = df3.loc[(df3['Graph-Group'] == 'CX-Time') ]
# works print(str(df3['test-tag']))

# works df4 = df3.loc[(df3['Graph-Group'] == 'CX-Time') & ('ATH10K' in str(df3['test-tag']) )]
df4 = df3.loc[(df3['Graph-Group'] == 'CX-Time') & ('ATH10K' in str(df3['test-tag']) )]

graph_group_list = list(df3['Graph-Group'])
graph_group_list = list(set(graph_group_list))  #remove duplicates 

test_tag_list = list(df3['test-tag'])
test_tag_list = list(set(test_tag_list))

i = 0 
plot_figure = []
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

            test_rig_list = list(df_tmp['test-rig'])
            test_rig = list(set(test_rig_list))

            test_id_list = list(df_tmp['test-id'])
            test_id = list(set(test_id_list))

            # get graph labels from dataframe
            units_list = list(df_tmp['Units'])
            units = list(set(units_list))

            append_fig.update_layout(
                title="{} : {} : {} : {}".format(test_id[0], group, test_tag, test_rig[0]),
                xaxis_title="Time",
                yaxis_title="{}".format(units[0]),
                xaxis = {'type' : 'date'}
            )
            plot_figure.append(append_fig)

'''
            append_fig.update_layout(
                title="Throughput vs Packet size",
                xaxis_title="Packet Size",
                yaxis_title="Mbps",
                xaxis = {'type' : 'date'}
            )
            plot_figure.append(append_fig)
'''
# there may be more layout with html.Div 
# Maybe a be more OO

images_div = []
for plot_fig in plot_figure:
    images_div.append(dcc.Graph(figure=plot_fig))

app.layout = html.Div(images_div)

'''
fig2 = (px.scatter(df2, x="Date", y="numeric-score",
                 color="short-description", hover_name="short-description",
                 size_max=60)).update_traces(mode='lines+markers')

fig2.update_layout(
    title="Throughput vs Packet size",
    xaxis_title="Packet Size",
    yaxis_title="Mbps",
    xaxis = {'type' : 'date'}
)


app.layout = html.Div([
    dcc.Graph(
        id='packet-size vs rate',
        figure=fig2
    )
])

'''

if __name__ == '__main__':
    app.run_server(debug=True)
    