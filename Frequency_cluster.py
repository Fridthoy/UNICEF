# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 13:49:23 2020

@author: Ingvild
"""

import pandas as pd
from random import randint
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

#UNICEF
#What triggers people to become donors?
#- An analysis based on the giving frequency and patterns of different typical givers

#creating a couple of functions for later use
def month_from_date(date): 
    return(int(date.split('.')[1]))                          #extracting month, date format dd.mm.yyyy
    
def str_to_int(amount):
    return(int(amount.split(',')[0]))                        #converting amount to int
    
#importing files
df_original = pd.read_csv('Payment_File_Cash.csv', sep=';')  #Import data
df = pd.DataFrame(columns=['GiverID', 'Month', 'Amount'])    #Initialize data frame to hold features 
df['GiverID'] = df_original['Giver ID']                      #Insert features to the data frame
df['Amount'] = list(map(str_to_int, df_original['Amount'].fillna('0'))) #Insert features to the data frame
df['Month'] = list(map(month_from_date, df_original['Close Date'])) #Insert features to the data frame

df.head()                                                    #displaying new dataframe


#Group the givers and their typical (averaged) payed per month!
#Obs: use the average because the data set is from januar 2017- september 2020. Thus not fully four years and october, november and december would yield less amounts in not the average was used.¶
df_mean = df.groupby(by=['GiverID', 'Month']).mean()         #Grouping same user ID's and calculating their average amount
df_mean.head(24)


#Month of max payment, checking that it is the same as max of df_mean.

df_max = df_mean.groupby(by='GiverID').max()                #Find max amount per giver per month that is summed over
df_max.head(2)


#Scale the amounts of each user by their maximum gift. Double check that the month which is 1.000000 under neeth here, has the same value as the month that have max bayment to the user of df_mean.
# Normalize the averaged months 
df_scaled = (df_mean / df_max)                               #normalize 
df_scaled.head(24)  

#Create data frame with one row per giver ID, and the frequency in 12 columns (12 months) for each row.
df_transformed = pd.DataFrame(index=df['GiverID'].unique(), columns=[m for m in range(1, 13)])  # New dataframe with a index per giver ID with columns from 1 to 12

length = len(df_transformed.index) #used to print later ;) 

for i, idx in enumerate(df_transformed.index):               #For each index
    
    if i % 50 == 0: #prints every 50 itteration 
        print(f'Did {i+1}/{length} rows!   ', end='\r')      #just to check the time used, this code takes FOREVER! 
   
    # Put in the transformed vector from df_scaled! Shiiiit! Bæææm!
    for col in range(1, 13):  #goes though all the months of each giver
        try:
                df_transformed.loc[idx][col] = df_scaled.loc[idx].T[col].values[0]  #if the giver gave a gift this month it is added to df_transformed 
        except:  #else
                df_transformed.loc[idx][col] = 0             #zero is added to the month

#Save and upload df_transformed, such that the above code don't need to be run each time
#df_transformed.to_csv('df_transformed.csv') #save such that the prosses don't have to be done every run
df_transformed = pd.read_csv('df_transformed.csv', index_col='Unnamed: 0')



#Finally : CLUSTERING
df_transformed.fillna(0, inplace=True)                       #takes away the "NaN's"
n_clusters = 4                                               #number of clusters
mod = KMeans(n_clusters=n_clusters, random_state=0)          #creating model
mod.fit(df_transformed)                                      #training model
df_transformed['ClusterID'] = mod.predict(df_transformed)    #predicting the data set 

#Create new data frame with only one row per giver ID and givers cluster ID
members_in_cluster = df_transformed.groupby(by="ClusterID").count()  #calculating the size of each cluster
fig, ax = plt.subplots()                                     #initializing plot
for i, cl in enumerate(mod.cluster_centers_): #iterating though cluster centers -->  typical donor in this cluster
    plt.plot([i for i in range(1,13)], cl, label='Cluster ' + str(i) + '; Members ' + str(members_in_cluster.loc[i][1])) #ploting each cluster
plt.legend()                                                 #inserting legend
fig.savefig(str(n_clusters) +'cluster centers month plot.png') #save plot for report
plt.xlabel('Months from Jan (1) to Dec (12)')
plt.ylabel('Normalized amount')
plt.show()                                                   #display plot
#I mai kjøper folk ferie. I november kjøper folk julegave. Stakkars fattige barn. 

df_merged = df_transformed.merge(df_original, how='inner', left_index=True, right_on='Giver ID')[['ClusterID', 'Source Channel Recruitment', 'Amount']] #merging Df_transformed and df_original by Giver ID. Wish to extract the channel of recruitment and analyse it by the typical giver groups :) 

members_df = df_merged.groupby(by='ClusterID').count()       #Grouping again by cluster ID
members_df.columns = ['Number', '_']                         #change to more logical name of columns 
members_df = members_df['Number']                            #take away column '-'

# scale the channel of recruitment for each user group 
df_channel = df_merged.groupby(by=['ClusterID', 'Source Channel Recruitment']).count() #find the number of givers for each source 
for i in range(len(members_in_cluster)):                     #go through all the members
    df_channel.loc[i] = [t/members_df.loc[i] for t in df_channel.loc[i].values] #scale the number of givers "convinced to give" by a channel 
    
d = {t: i for i, t in enumerate(df_channel.index.get_level_values(1).unique())} #maping each channel to a number



#Plotting bar plot of which channel the typical givers are convinced by
fig, ax = plt.subplots()                                     #initializing subplots
xticks = [i for i in range(len(d))]                          #labels for x-axis
old_bar = [0]*len(d)                                         #initializing zero vector with length == number of channels
for i in range(n_clusters):                                  #ploting channel for each cluster's 

    y = [0]*len(d)
    
    indices = df_channel['Amount'].loc[i].index
    values = df_channel['Amount'].loc[i].values
    
    for j, v in zip(indices, values):
        y[d[j]] = v                                          #creating new y (height of bar per channel)
    ax.bar(xticks, y, bottom=old_bar, label='Cluster ' + str(i)) #plotting
    
    old_bar = np.add(old_bar, y)                             #adding values to the bars such (since the bars are put on top of each other)
plt.legend()                                                 #inserting legend
    
ax.set_xticks(xticks)                                        #inserting x-labels
ax.set_xticklabels(d.keys(), rotation=90)                    #rotating labels 90 deg
fig.savefig(str(n_clusters) + 'Clusters bar plot.png')       #save bar plot for report
plt.show()                                                   #display plot

