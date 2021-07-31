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
print(kpi_list)

df = pd.DataFrame()

for kpi in kpi_list:
    # load data
    append_df = pd.read_csv(kpi, sep='\t')
    df = df.append(append_df, ignore_index=True)

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
df2 = pd.read_sql_query("SELECT * from dp_table" ,conn)
print(df2.head())
conn.close()
print(df2)


conn = sqlite3.connect("qa_db")
df3 = pd.read_sql_query("SELECT * from  dp_table" ,conn)
#print(df3.head())
conn.close()

# works df4 = df3.loc[(df3['Graph-Group'] == 'CX-Time') & (df3['test-tag'] == 'ATH10K(9984)')]
# works df4 = df3.loc[(df3['Graph-Group'] == 'CX-Time') ]
# works print(str(df3['test-tag']))

# works df4 = df3.loc[(df3['Graph-Group'] == 'CX-Time') & ('ATH10K' in str(df3['test-tag']) )]

print("df4: {}".format(df4))

#print(df3['Graph-Group'],df3['Date'])

exit(1)
                 
fig = (px.scatter(df2, x="Date", y="numeric-score",
                 color="short-description", hover_name="short-description",
                 size_max=60)).update_traces(mode='lines+markers')

'''
fig = px.scatter(df, x="Date", y="numeric-score",
                 color="short-description", hover_name="short-description",
                 size_max=60)
'''              
'''
fig = px.scatter(df, x="short-description", y="numeric-score",
                 color="short-description", hover_name="short-description",
                 size_max=60)
'''
fig.update_layout(
    title="Throughput vs Packet size",
    xaxis_title="Packet Size",
    yaxis_title="Mbps",
    xaxis = {'type' : 'date'}
)


app.layout = html.Div([
    dcc.Graph(
        id='packet-size vs rate',
        figure=fig
    ),
    #dcc.Graph(
    #    id='packet-size vs rate2',
    #    figure=fig
    #)

])

if __name__ == '__main__':
    app.run_server(debug=True)
    