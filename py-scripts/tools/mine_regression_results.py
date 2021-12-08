#!/usr/bin/env python3
import pandas as pd
import argparse


class MineRegression:
    def __init__(self,
                 system_information=None,
                 save_csv=False,
                 ips=None):
        self.df = None
        self.ips = ips
        self.system_info = system_information
        self.save_csv = save_csv

    def generate_csv(self):
        results = [pd.read_html('http://%s/html-reports/latest.html' % url, attrs={'id': 'myTable2'})[0] for url in self.ips]
        systems = [pd.read_html('http://%s/html-reports/latest.html' % url, attrs={'id': 'SystemInformation'})[0] for
                   url in self.ips]
        for df in range(0, len(self.ips)):
            results[df]['IP'] = self.ips[df]
            systems[df]['IP'] = self.ips[df]
        dfs = [pd.merge(results[n], systems[n], on='IP') for n in range(len(self.ips))]
        self.df = pd.concat(dfs)
        self.df = self.df[self.df['STDOUT'] == 'STDOUT']
        print(self.df.columns)

    def generate_report(self):
        system_variations = self.df[
            ['IP', 'Python version', 'LANforge version', 'OS Version', 'Hostname', 'Python Environment']].drop_duplicates(
            ['IP', 'Python version', 'LANforge version', 'OS Version', 'Hostname', 'Python Environment']).reset_index(drop=True)
        print(self.df.drop_duplicates('IP'))
        print(self.df['IP'].value_counts())
        print(system_variations['IP'].value_counts())
        errors = list()
        lanforge_errors = list()
        for index in system_variations.index:
            print(system_variations['IP'][index])
            variation = system_variations.iloc[index]
            result = self.df.loc[self.df[['Python version', 'LANforge version', 'OS Version', 'Python Environment', 'IP']].isin(dict(
                variation).values()).all(axis=1), :].dropna(subset=['STDERR']).shape[0]
            print(result)
            errors.append(result)

            lanforge_result = self.df.loc[self.df[['Python version', 'LANforge version', 'OS Version', 'Python Environment', 'IP']].isin(dict(
                variation).values()).all(axis=1), :].dropna(subset=['LANforge Error']).shape[0]
            print(result)
            lanforge_errors.append(lanforge_result)
        system_variations['errors'] = errors
        system_variations['LANforge errors'] = lanforge_errors
        system_variations['Python errors'] = system_variations['errors'] - system_variations['LANforge errors']
        if self.save_csv:
            system_variations.to_csv('regression_suite_results.csv')
        else:
            print(system_variations.sort_values('errors'))


def main():
    parser = argparse.ArgumentParser(description='Compare regression results from different systems')
    parser.add_argument('--system_info', help='location of system information csv', default=None)
    parser.add_argument('--save_csv', help='save CSV of results', default=False)
    parser.add_argument('--ip', help='IP addresses of LANforge devices you want to probe', action='append')
    args = parser.parse_args()

    if args.ip is None:
        args.ip = ['192.168.92.18', '192.168.92.12', '192.168.93.51', '192.168.92.15']
    #args.ip = ['192.168.93.51']
    Miner = MineRegression(system_information=args.system_info,
                           save_csv=args.save_csv,
                           ips=args.ip)

    Miner.generate_csv()

    Miner.generate_report()


if __name__ == '__main__':
    main()
