import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_pickle_file(filename):
    df = pd.read_pickle(ROOT_DIR + '\\pickle_files\\' + filename + '.pkl')

    return df

if __name__ == '__main__':
    df = load_pickle_file('Donor_File_Contacts')
    print(df)