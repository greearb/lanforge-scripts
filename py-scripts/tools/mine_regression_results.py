#!/usr/bin/env python3
import pandas as pd
import argparse


class MineRegression:
    def __init__(self,
                 system_information=None,
                 save_csv=False):
        self.df = None
        self.system_info = system_information
        self.save_csv = save_csv

    def generate_csv(self):
        ips = ['192.168.92.18', '192.168.92.12', '192.168.93.51', '192.168.92.15']
        results = [pd.read_html('http://%s/html-reports/latest.html' % url, attrs={'id': 'myTable2'})[0] for url in ips]
        systems = [pd.read_html('http://%s/html-reports/latest.html' % url, attrs={'id': 'SystemInformation'})[0] for
                   url in ips]
        for df in range(0, len(ips)):
            results[df]['IP'] = ips[df]
            systems[df]['IP'] = ips[df]
        dfs = [pd.merge(results[n], systems[n], on='IP') for n in range(len(ips))]
        self.df = pd.concat(dfs)
        self.df = self.df[self.df['STDOUT'] == 'STDOUT']
        print(self.df['IP'].value_counts())

    def generate_report(self):
        system_variations = self.df[
            ['IP', 'Python version', 'LANforge version', 'OS Version', 'Hostname']].drop_duplicates(
            ['Python version', 'LANforge version', 'OS Version']).reset_index(drop=True)
        errors = list()
        for index in system_variations.index:
            variation = system_variations.iloc[index]
            result = self.df.loc[self.df[['Python version', 'LANforge version', 'OS Version']].isin(dict(
                variation).values()).all(axis=1), :].dropna(subset=['STDERR']).shape[0]
            errors.append(result)
        system_variations['errors'] = errors
        if self.save_csv:
            system_variations.to_csv('regression_suite_results.csv')
        else:
            print(system_variations.sort_values('errors'))


def main():
    parser = argparse.ArgumentParser(description='Compare regression results from different systems')
    parser.add_argument('--system_info', help='location of system information csv', default=None)
    parser.add_argument('--save_csv', help='save CSV of results', default=False)

    args = parser.parse_args()

    Miner = MineRegression(system_information=args.system_info,
                           save_csv=args.save_csv)

    Miner.generate_csv()

    Miner.generate_report()


if __name__ == '__main__':
    main()
