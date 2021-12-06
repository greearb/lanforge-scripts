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
        if self.system_info:
            systems = pd.read_csv(self.system_info)
            ips = systems['Machine']
        else:
            system_info = {'192.168.92.18': ['3.7.7', '5.4.4', 'F30', '.local'],
                           '192.168.92.12': ['3.9.7', '5.4.4', 'F34', '.local'],
                           '192.168.93.51': ['3.7.7', '5.4.4', 'F30', 'venv'],
                           '192.168.92.15': ['3.6.6', '5.4.4', 'F27', '.local']}
            ips = list(system_info.keys())
            systems = pd.DataFrame(system_info).transpose().reset_index()
            systems.columns = ['Machine', 'Python version', 'LF version', 'Fedora version', 'environment']
        results = [pd.read_html('http://%s/html-reports/latest.html' % url)[0] for url in ips]
        for result in list(range(0, len(ips))):
            results[result]['Machine'] = ips[result]
        self.df = pd.concat(results)
        self.df = pd.merge(self.df, systems, on='Machine')
        self.df = self.df[self.df['STDOUT'] == 'STDOUT']

    def generate_report(self):
        system_variations = self.df[['Python version', 'LF version', 'Fedora version', 'environment']].drop_duplicates().reset_index(
            drop=True)
        errors = list()
        for index in system_variations.index:
            variation = system_variations.iloc[index]
            result = self.df.loc[self.df[['Python version', 'LF version', 'Fedora version', 'environment']].isin(dict(
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
