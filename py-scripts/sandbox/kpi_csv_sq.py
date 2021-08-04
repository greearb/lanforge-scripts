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
        self.children_div = []
        self.server_html_reports = 'http://192.168.95.6/html-reports/' #TODO pass in server
        self.server = 'http://192.168.95.6/' #TODO pass in server

    # information on sqlite database
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
    def store(self):
        print("reading kpi and storing in db {}".format(self.database))
        path = Path(self.path)
        #self.kpi_list = list(path.glob('**/{}'.format(self.file)))
        self.kpi_list = list(path.glob('**/kpi.csv'))

        for kpi in self.kpi_list: #TODO note empty kpi.csv failed test 
            df_kpi_tmp = pd.read_csv(kpi, sep='\t')  
            df_kpi_tmp['kpi_path'] = str(kpi).replace('kpi.csv','')  # only store the path to the kpi.csv file
            df_kpi_tmp = df_kpi_tmp.append(df_kpi_tmp, ignore_index=True)
            self.df = self.df.append(df_kpi_tmp, ignore_index=True)

        self.conn = sqlite3.connect(self.database) 
        self.df.to_sql(self.table,self.conn,if_exists='append')
        self.conn.close()

    # duplicates the store since the the png are put back into the directory where the kpi are gathered
    def generate_graph_png(self):
        print("generating png files")
        if not self.kpi_list:
            self.store()
        if not self.kpi_list:
            print("no new kpi.csv found, check input paths, will read database")

        #https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html-
        self.conn = sqlite3.connect(self.database)
        # df3 is just a name
        df3 = pd.read_sql_query("SELECT * from {}".format(self.table) ,self.conn) #current connection is sqlite3 /TODO move to SQLAlchemy
        # sort by date column
        df3 = df3.sort_values(by='Date')
        #print(df3.head())
        self.conn.close()

        # graph group and test-tag are used for detemining the graphs
        graph_group_list = list(df3['Graph-Group'])
        graph_group_list = list(set(graph_group_list))  #remove duplicates 

        test_tag_list = list(df3['test-tag'])
        test_tag_list = list(set(test_tag_list))
        
        test_rig_list = list(df3['test-rig'])
        test_rig_list = list(set(test_rig_list))

        for test_rig in test_rig_list:
            for test_tag in test_tag_list:
                for group in graph_group_list:
                    df_tmp = df3.loc[(df3['test-rig'] == test_rig) & (df3['Graph-Group'] == str(group)) & (df3['test-tag'] == str(test_tag))]
                    if df_tmp.empty == False:
                        kpi_fig = (px.scatter(df_tmp, x="Date", y="numeric-score",
                             color="short-description", hover_name="short-description",
                             size_max=60)).update_traces(mode='lines+markers')

                        # remove duplicates from 
                        test_id_list = list(df_tmp['test-id'])
                        test_id = list(set(test_id_list))

                        kpi_path_list = list(df_tmp['kpi_path'])
                        kpi_path = list(set(kpi_path_list))
                        print("kpi_path {}".format(kpi_path))
                        print("kpi_path[0]: {}".format(kpi_path[0]))
                        print("kpi_path[-1]: {}".format(kpi_path[-1]))

                        units_list = list(df_tmp['Units'])
                        units = list(set(units_list))

                        kpi_fig.update_layout(
                            title="{} : {} : {} : {}".format(test_id[-1], group, test_tag, test_rig),
                            xaxis_title="Time",
                            yaxis_title="{}".format(units[0]),
                            xaxis = {'type' : 'date'}
                        )
                        # save the figure - this may need to be re-written
                        print("kpi_path:{}".format(df_tmp['kpi_path']))
                        png_path = os.path.join(kpi_path[-1],"{}_{}_{}_{}_kpi.png".format(test_id[-1], group, test_tag, test_rig))
                        print("png_path {}".format(png_path))
                        kpi_fig.write_image(png_path,scale=1,width=1200,height=350)

                        # use image from above to creat html display
                        self.children_div.append(dcc.Graph(figure=kpi_fig))                    

                        #TODO the link must be to a server to display html
                        # WARNING: os.path.join will use the path for where the script is RUN which can be container.
                        # need to construct path to server manually. DO NOT USE os.path.join
                        #TODO need to work out the reporting paths - pass in path adjust
                        index_html_path = self.server + kpi_path[-1] + "index.html"
                        index_html_path = index_html_path.replace('/home/lanforge/','')
                        self.children_div.append(html.A('{}_{}_{}_{}_index.html'.format(test_id[-1], group, test_tag, test_rig),
                            href=index_html_path, target='_blank'))
                        self.children_div.append(html.Br())
                        self.children_div.append(html.A('html_reports', href=self.server_html_reports, target='_blank'))
                        self.children_div.append(html.Br())
                        self.children_div.append(html.Br())

    # access from server
    # https://stackoverflow.com/questions/61678129/how-to-access-a-plotly-dash-app-server-via-lan
    def show(self):
        if not self.children_div:
            self.generate_graph_png()
        if not self.children_div:
            print("NOTE: test-tag may not be present in the kpi thus no results generated")

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        app.layout = html.Div([
            html.H1(children= "LANforge Testing",className="lanforge",
            style={'color':'green','text-align':'center'}),
            html.H2(children= "Results",className="ts1",
            style={'color':'#00361c','text-align':'left'}),
            # images_div is already a list, children = a list of html components
            html.Div(children= self.children_div, style={"maxHeight": "540px", "overflow": "scroll"} ), 
            html.A('www.candelatech.com',href='http://www.candelatech.com', target='_blank',
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
    parser.add_argument('--table', help='--table qa_table',default='qa_table')
    parser.add_argument('--store', help='--store , store kpi to db',action='store_true')
    parser.add_argument('--png', help='--png,  may store kpi to db and generate png',action='store_true')
    parser.add_argument('--show', help='--show',action='store_true')
    
    args = parser.parse_args()

    __path = args.path
    __file = args.file
    __database = args.database
    __table = args.table

    print("config: path:{} file:{} database:{} table:{} store:{} png:{} show:{} "
        .format(__path,__file,__database,__table,args.store, args.png,args.show))

    csv_dash = csv_sqlite_dash(
                _path = __path,
                _file = __file,
                _database = __database,
                _table = __table)
    if args.store:
        csv_dash.store()
    if args.png:
        csv_dash.generate_graph_png()
    if args.show:        
        csv_dash.show()

    if args.store == False and args.png == False and args.show == False:
        print("Need to enter an action of --store  --png --show ")

if __name__ == '__main__':
    main()
    