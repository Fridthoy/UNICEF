import pandas as pd

df = pd.read_csv('C:\\Users\\Fridtjof\\Documents\\skole høst 2020\\dataAnalyse\\gruppeCSV\\Donor_File_Contacts.csv', sep=';')

df.to_pickle('C:\\Users\\Fridtjof\\Documents\\skole høst 2020\\dataAnalyse\\gruppe\\pickle_files\\Donor_File_Contacts.pkl')
print(df)
