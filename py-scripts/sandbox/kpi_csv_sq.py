#!/usr/bin/env python3
'''
File: use kpi.csv placed in sql database, create png of historical kpi and present on dashboard 
Usage: csv_sqlite.py --path <path to directories to traverse> --database <name of database>
'''
# visit http://127.0.0.1:8050/ in your web browser.

import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import sqlite3
import argparse
from  pathlib import Path

# Any style components can be used
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

class csv_sqlite_dash():
    def __init__(self,
                _path = '.',
                _file = 'kpi.csv',
                _database = 'qa_db',
                _table = 'qa_table'):
        self.path = _path
        self.file = _file
        self.database = _database
        self.table = _table
        self.kpi_list = []
        self.html_list = []
        self.conn = None
        self.df = pd.DataFrame()
        self.plot_figure = []
        children_div = []

    # information on sqlite database
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
    def store(self):
        print("reading kpi and storing in db {}".format(self.database))
        path = Path(self.path)
        #self.kpi_list = list(path.glob('**/{}'.format(self.file)))
        self.kpi_list = list(path.glob('**/kpi.csv'))

        self.html_list = list(path.glob('**/index.html')) # the html is only index.html
        print("html_list: {}".format(self.html_list))

        for kpi in self.kpi_list: #TODO note empty kpi.csv failed test 
            df_kpi_tmp = pd.read_csv(kpi, sep='\t')  
            df_kpi_tmp['kpi_path'] = str(kpi).replace('kpi.csv','')  # only store the path to the kpi.csv file
            df_kpi_tmp = df_kpi_tmp.append(df_kpi_tmp, ignore_index=True)
            self.df = self.df.append(df_kpi_tmp, ignore_index=True)

        self.conn = sqlite3.connect(self.database) 
        #data may be appended setting if_exists='append'
        self.df.to_sql(self.table,self.conn,if_exists='replace')
        self.conn.close()

    # duplicates the store since the the png are put back into the directory where the kpi are gathered
    def generate_png(self):
        print("generating png files")
        if not self.kpi_list:
            self.store()
        if not self.kpi_list:
            print("no kpi.csv found, check input paths, exiting")
            exit(1)

        #https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html
        self.conn = sqlite3.connect(self.database)
        # df3 is just a name
        df3 = pd.read_sql_query("SELECT * from  dp_table" ,self.conn)
        #print(df3.head())
        self.conn.close()

        # graph group and test-tag are used for detemining the graphs
        graph_group_list = list(df3['Graph-Group'])
        graph_group_list = list(set(graph_group_list))  #remove duplicates 

        test_tag_list = list(df3['test-tag'])
        test_tag_list = list(set(test_tag_list))

        for test_tag in test_tag_list:
            for group in graph_group_list:
                df_tmp = df3.loc[(df3['Graph-Group'] == str(group)) & (df3['test-tag'] == str(test_tag))]
                if df_tmp.empty == False:
                    kpi_fig = (px.scatter(df_tmp, x="Date", y="numeric-score",
                         color="short-description", hover_name="short-description",
                         size_max=60)).update_traces(mode='lines+markers')

                    # remove duplicates from 
                    test_rig_list = list(df_tmp['test-rig'])
                    test_rig = list(set(test_rig_list))

                    test_id_list = list(df_tmp['test-id'])
                    test_id = list(set(test_id_list))

                    kpi_path_list = list(df_tmp['kpi_path'])
                    kpi_path = list(set(kpi_path_list))

                    units_list = list(df_tmp['Units'])
                    units = list(set(units_list))

                    kpi_fig.update_layout(
                        title="{} : {} : {} : {}".format(test_id[0], group, test_tag, test_rig[0]),
                        xaxis_title="Time",
                        yaxis_title="{}".format(units[0]),
                        xaxis = {'type' : 'date'}
                    )
                    # save the figure - this may need to be re-written
                    print("kpi_path:{}".format(df_tmp['kpi_path']))
                    png_path = os.path.join(kpi_path[0],"{}_{}_{}_{}_kpi.png".format(test_id[0], group, test_tag, test_rig[0]))
                    print("png_path {}".format(png_path))
                    kpi_fig.write_image(png_path,scale=1,width=1200,height=350)
                    # store the image so it may be displayed
                    self.children_div.append(dcc.Graph(figure=kpi_fig))

    # access from server
    # https://stackoverflow.com/questions/61678129/how-to-access-a-plotly-dash-app-server-via-lan
    def show(self):
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        app.layout = html.Div([
            html.H1(children= "LANforge Testing",className="lanforge",
            style={'color':'green','text-align':'center'}),
            html.H2(children= "Test Set #1",className="ts1",
            style={'color':'#00361c','text-align':'left'}),
            # images_div is already a list, children = a list of html components
            html.Div(children= self.children_div, style={"maxHeight": "480px", "overflow": "scroll"} ), 
            html.H2(children= "Test Set #2",className="ts2",
            style={'color':'#00361c','text-align':'left'}),
        ])
        app.run_server(host= '0.0.0.0', debug=True)
        # host = '0.0.0.0'  allows for remote access,  local debug host = '127.0.0.1'
        # app.run_server(host= '0.0.0.0', debug=True) 


def main():

    parser = argparse.ArgumentParser(
        prog='kpi_csv_sq.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        read kpi.csv into sqlite database , save png of history and preset on dashboard

            ''',
        description='''\
File: will search path recursivly for kpi.csv and place into sqlite database
Usage: kpi_csv_sq.py --path <path to directories to traverse> --database <name of database>

        ''')
    parser.add_argument('--path', help='--path ./top directory path to kpi',required=True)
    parser.add_argument('--file', help='--file kpi.csv',default='kpi.csv') #TODO is this needed
    parser.add_argument('--database', help='--database qa_test_db',default='qa_test_db')
    parser.add_argument('--store', help='--store , store kpi to db',action='store_true')
    parser.add_argument('--png', help='--png,  may store kpi to db and generate png',action='store_true')
    parser.add_argument('--show', help='--show',action='store_true')
    
    args = parser.parse_args()

    __path = args.path
    __file = args.file
    __database = args.database

    csv_dash = csv_sqlite_dash(
                _path = __path,
                _file = __file,
                _database = __database)
    if args.store:
        csv_dash.store()
    if args.png:
        csv_dash.generate_png()
    if args.show:        
        csv_dash.show()


if __name__ == '__main__':
    main()
    