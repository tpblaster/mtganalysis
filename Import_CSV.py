import pandas


def read_csv_from_path(path):
    df = pandas.read_csv(path)
    return df
