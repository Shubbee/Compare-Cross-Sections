"""
XNS Comparison Tool:

This script creates XS comparison plots of 2 or 3 topo IDS froms a *.xns11 file

Created on Wed May 19 2021

@author: Shubhneet Singh 
ssin@dhigroup.com
DHI,US

"""

########################### REQUIREMENTS ##################################### 

# Importing useful Python libs
import os
import sys
import clr
import csv
import time
import math
import array
import System
import datetime
import collections
import matplotlib.pyplot as plt

from math import *
from System import DateTime
from decimal import Decimal

# Path with bin files MIKE SDK
sys.path.append(r'C:\Program Files (x86)\DHI\2020\MIKE SDK\bin')
clr.AddReference("DHI.Mike.Install");
from DHI.Mike.Install import MikeImport, MikeProducts
MikeImport.SetupLatest(MikeProducts.MikeCore)
# MIKE SDK
clr.AddReference("DHI.Mike1D.ResultDataAccess")
clr.AddReference("DHI.Mike1D.CrossSectionModule")
clr.AddReference("DHI.Mike1D.Generic")
clr.AddReference("DHI.Generic.MikeZero.DFS");
clr.AddReference("DHI.Generic.MikeZero.EUM");
clr.AddReference("System");

# Importing SDK
import System
from System import Array
from DHI.Mike1D.ResultDataAccess import *
from DHI.Mike1D.CrossSectionModule import *
from DHI.Mike1D.Generic import *
from DHI.Generic.MikeZero import *
from DHI.Generic.MikeZero import eumUnit, eumItem, eumQuantity
from DHI.Generic.MikeZero.DFS import *
from DHI.Generic.MikeZero.DFS.dfs123 import *


#%%
###################### USER INPUTS ########################################### 

#1 Input files
xns11_filepath = r"C:\Users\ssin\OneDrive - DHI\Desktop\South Boulder Creek\25 XS_AsbuiltvsLiDAR\4 MH-XNSExtraction\4 Asbuilt2013XNS_BasedonCEMxnsShapefile\xns_asbuilt_CEMinterpolated.xns11"

#2 To run the code for all rivers set 1 else 0 for selected rivers
all_rivers = 1
#3 Selected rivers to process (if #2 == 0)
rivers_names = 0     #['South Boulder Creek']

#4 Topo ids to process
topo_id_names = ['100','2020 Model', '2013 Asbuilt']

#5 Tolerance to lookup chainages (in meters)
tol = .1
#6 Max value of range to understand as near section (in meters)
max_range = 3

#7 To plot x-sections set 1 else 0
to_plot = 1

###################### READING INPUT FILE ####################################

# Reading the cross section file
diagnostics = Diagnostics("Errors")
data_factory = CrossSectionDataFactory()
data = data_factory.Open(Connection.Create(xns11_filepath), diagnostics)
rivers = data.GetReachTopoIdEnumerable()

#%%
######################## FUNCTIONS ###########################################

def get_branch_names(rivers):
    # Gets all the branch names
    river_names = []
    for river in rivers:
        if river.ReachId not in river_names: 
            river_names.append(river.ReachId)
    return river_names        
    # river_names=get_branch_names(rivers)

def get_topo_chainages(rivers, river_name, topo_id_name):
    # Gets all chainages of a topo id of a branch
    
    branch_topo_xns = []
    # identifies branch-topo object
    for river in rivers:
        if river.ReachId == river_name and river.TopoId == topo_id_name:
            branch_topo_xns = river.GetEnumerator()
    
    # Loop over xns to get chainages in topo of a branch
    branch_topo_chainages  = []
    
    for xns in branch_topo_xns:
        branch_topo_chainages.append(xns.Location.Chainage)
            
    return branch_topo_chainages
    # branch_topo_chainages=get_topo_chainages(rivers, river_names[0], topo_id_names[0])


         
def compare_chainages(river_name, topo_id_names, log_file):
    # Finds the number of xns matching and gets the matching chainages for 2 or 3 Topo ids
    
    #Gets chainages of all the req topo ids of a river
    topo_chainages = {}
    for a in range(len(topo_id_names)):
        topo_chainages[a] = get_topo_chainages(rivers, river_name, topo_id_names[a])

    # Match xns chainages in all the req topo ids
    topo_chainage_match = {}
    all_topo_chainage_match = []
    number_matching = []
    log_file.write('\nRiver: {}'.format(river_name) + '\n')  
    for i in range(len(topo_chainages[0])):
        
        # List of differences btw a chainage of first chainage of first topo id with all the chainages of other topo ids; to find the closest match 
        dif_list = {} 
        if len(topo_chainages[1]) > 0:   
            dif_list[0] = [abs(round(topo_chainages[0][i],2) - round(topo_chainages[1][j],2)) for j in range(len(topo_chainages[1]))]

        if len(topo_id_names)>2 and len(topo_chainages[2]) > 0:
            dif_list[1] = [abs(round(topo_chainages[0][i],2) - round(topo_chainages[2][k],0)) for k in range(len(topo_chainages[2]))]


        number_matching_chainage = []
        
        # All 3 topo ids have a matching chainage:
        if len(topo_chainages[1]) > 0 and len(topo_chainages[2]) > 0 and any(dif <= tol+max_range for dif in dif_list[0]) and any(dif <= tol+max_range for dif in dif_list[1]):  
            number_matching_chainage = '3_topo_ids'
            topo_chainage_match[0] = topo_chainages[0][i]
            # Gets the plot chainages x-section for seocond topo-ID  
            second_topo_match_index = dif_list[0].index(min(dif_list[0]))
            topo_chainage_match[1] = topo_chainages[1][second_topo_match_index] 
            # Gets the plot chainages x-section for third topo-ID  
            third_topo_match_index = dif_list[1].index(min(dif_list[1]))
            topo_chainage_match[2]= topo_chainages[2][third_topo_match_index]
            
            # if all(dif > tol for dif in dif_list[0]) or all(dif > tol for dif in dif_list[1]):
            #     log_file.write('\nChainage: {}'.format(str(round(topo_chainages[0][i]* 3.28084 ,2))) + ' matched; out of the tolerance range but below max tolerance\n')  
          
        # If 2 topo ids have a matching chainage, 2 cases: second topo absent, third topo absent   
        ## Second topo matches with first
        elif len(topo_chainages[1]) > 0 and any(dif <= tol+max_range for dif in dif_list[0]) and (len(topo_chainages[2]) == 0 or all(dif > tol+max_range for dif in dif_list[1])):
            topo_chainage_match[0] = topo_chainages[0][i]
            # Gets the chainages of matching seocond topo id 
            second_topo_match_index = dif_list[0].index(min(dif_list[0]))
            topo_chainage_match[1] = topo_chainages[1][second_topo_match_index] 
            number_matching_chainage = 'first_second'
            # if all(dif > tol for dif in dif_list[0]):
            #     log_file.write('\nChainage: {}'.format(str(round(topo_chainages[0][i]* 3.28084 ,2))) + ' matched; out of the tolerance range but below max range\n')  
        ## Third topo matches with first
        elif len(topo_chainages[2]) > 0 and any(dif <= tol+max_range for dif in dif_list[1]) and (len(topo_chainages[1]) == 0 or all(dif > tol+max_range for dif in dif_list[0])):
            topo_chainage_match[0] = topo_chainages[0][i]
            # Gets the chainages of matching seocond topo id 
            third_topo_match_index = dif_list[1].index(min(dif_list[1]))
            topo_chainage_match[2] = topo_chainages[2][third_topo_match_index]   
            number_matching_chainage = 'first_third'
            # if all(dif > tol for dif in dif_list[1]):
            #     log_file.write('\nChainage: {}'.format(str(round(topo_chainages[0][i]* 3.28084 ,2))) + ' matched; out of the tolerance range but below max range\n')  
            
        
        # If topo ids do not have a matching chainage:  4 cases
        case1 = len(topo_chainages[1]) == 0 and len(topo_chainages[2]) == 0
        if len(topo_chainages[1]) != 0 and len(topo_chainages[2]) == 0:
            case2 = all(dif > tol+max_range for dif in dif_list[0])
        else:
            case2 = False
        if len(topo_chainages[1]) == 0 and len(topo_chainages[2]) != 0:
            case3 = all(dif > tol+max_range for dif in dif_list[1])
        else:
            case3 = False
        if len(topo_chainages[1]) != 0 and len(topo_chainages[2]) != 0:
            case4 = all(dif > tol+max_range for dif in dif_list[0]) and all(dif > tol+max_range for dif in dif_list[1])
        else:
            case4 = False            
           
    
        if case1 or case2 or case3 or case4:
            topo_chainage_match[0] = topo_chainages[0][i]
            number_matching_chainage = 'first_only'
            log_file.write('\nChainage: {}'.format(str(round(topo_chainages[0][i]* 3.28084,2))) + ' not available in CEM and Asbuilt, within max tolerance \n')
     
        try:
            b = topo_chainage_match[1]
        except:
            b= None
        
        try:
            c = topo_chainage_match[2]
        except:
            c = None        
        
        all_topo_chainage_match.append([topo_chainage_match[0], b,c])
        number_matching.append(number_matching_chainage)
        
    return number_matching, all_topo_chainage_match 
    # number_matching_chainage, all_topo_chainage_match = compare_chainages(river_names[0], topo_id_names[0], log_file=open("log.txt","w+"))

def get_xsection_coords(data, river_name, topo_id_name, chainage):
    # Gets x section for chainage
    location = Location(river_name, chainage)
    xsection = data.FindClosestCrossSection(location, topo_id_name)

    # Get x sections coordinates
    x_list = []
    y_list = []
    # Gets x section points
    xsection_coords = xsection.BaseCrossSection.Points.LstPoints
    
    
    # If xn has a vertical datum:
    if xsection_coords[1].Z ==0:
        for coord in xsection_coords:
             datum = xsection.get_BottomLevel() # to feet
             x = coord.X * 3.28084 # to feet
             z = (datum + coord.Z) * 3.28084 # to feet 
             x_list.append(x)
             y_list.append(z)
    else:     
    # loop over points
        for coord in xsection_coords:
             x = coord.X * 3.28084 # to feet
             z = coord.Z * 3.28084 # to feet 
             datum = xsection.get_BottomLevel()* 3.28084 # to feet
             x_list.append(x)
             y_list.append(z)
    coord_list = [x_list, y_list]

    return coord_list

def get_markers(xsection):
    # Get markers
    marker1 = [xsection.BaseCrossSection.LeftLeveeBank.X*3.28084, xsection.BaseCrossSection.LeftLeveeBank.Z*3.28084] # to feet
    marker2 = [xsection.BaseCrossSection.LowestPoint.X*3.28084, xsection.BaseCrossSection.LowestPoint.Z*3.28084] # to feet
    marker3 = [xsection.BaseCrossSection.RightLeveeBank.X*3.28084, xsection.BaseCrossSection.RightLeveeBank.Z*3.28084] # to feet
    markers = [marker1, marker2, marker3]

    return markers


def plot_xsection(river_name, topo_id_names, chainage, all_topo_coords):
    # Plots a xsection of 1/2/3 input topo ids at a chainage
    
    #river name - string input
    #topo_id_names - List of all the topo ids
    # all_topo_coords - List of coords of all the xns to be ploted
    
    # Plotting xns
    plot_message_CEM = []
    plot_message_Asbuilt = []
    fig, ax = plt.subplots()
    fig.set_size_inches(7, 5)
    ax.plot(all_topo_coords[0][0], all_topo_coords[0][1], label = 'EM', color = 'black', marker = 'o', markersize=3)
    if len(all_topo_coords) >1 and all(y < 30000 for y in all_topo_coords[1][1]):
        ax.plot(all_topo_coords[1][0], all_topo_coords[1][1], label = 'CEM', color = 'red', marker = 'o', markersize=3)
    if len(all_topo_coords) >1 and any(y > 30000 for y in all_topo_coords[1][1]):
        plot_message_CEM = str ('\n' + 'Chainage ' + str(round(chainage*3.28084, 2)) + ': CEM topo had elevation above 30000 ft, hence excluded\n')      
        
    if len(all_topo_coords) >2 and all(y < 30000 for y in all_topo_coords[2][1]): 
        ax.plot(all_topo_coords[2][0], all_topo_coords[2][1], label = 'Asbuilt', color = 'green', marker = 'o', markersize=3)    
    if len(all_topo_coords) >2 and any(y > 30000 for y in all_topo_coords[2][1]):
        plot_message_Asbuilt = str ('\n' + 'Chainage ' + str(round(chainage*3.28084, 2)) + ': Asbuilt topo had elevatioin above 30000 ft, hence excluded\n')

    # Marker 1 
#     ax.plot(markers_first_x_section[0][0], markers_first_x_section[0][1], label = "Marker 1", color = 'orange',marker = '*', markersize=22)
#     ax.plot(markers_second_x_section[0][0], markers_second_x_section[0][1], label='_nolegend_', color = 'orange',marker = '*', markersize=22)
#     # Marker 2
#     ax.plot(markers_first_x_section[1][0], markers_first_x_section[1][1], label = "Marker 2", color = 'green',marker = '*', markersize=22)
#     ax.plot(markers_second_x_section[1][0], markers_second_x_section[1][1], label='_nolegend_', color = 'green',marker = '*', markersize=22)
#     # Marker 3
#     ax.plot(markers_first_x_section[2][0], markers_first_x_section[2][1], label = "Marker 3", color = 'blue',marker = '*', markersize=22)
#     ax.plot(markers_second_x_section[2][0], markers_second_x_section[2][1], label='_nolegend_', color = 'blue',marker = '*', markersize=22)
      #ax.set(xlabel="X - [feet]", ylabel="Elevation - [feet]", title= river_name + '_' + str(round(chainage, 2)), fontsize=15)
    
    ax.set_xlabel("Horizontal distance along cross section (feet)", fontsize = 12)
    ax.set_ylabel("Elevation (feet)", fontsize = 12)
    ax.set_title(river_name + ', Chainage ' + str(round(chainage*3.28084, 2)) + ' (' + str(round(chainage, 2)) + ' m)' , fontsize=14)
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)

    plt.grid(color = 'grey', linestyle='-', linewidth=0.5)
    plt.legend(loc= 'upper right')
    plt.savefig(river_name + '_' + str(round(chainage*3.28084, 2)) + ".png") # to feet
    #plt.savefig(river_name + '_' + str(round(chainage, 2)) + ".png") # in meters
    plt.close()
    return plot_message_CEM, plot_message_Asbuilt

########################### MAIN FLOW ###########################

# Log file

os.chdir(r"C:\Users\ssin\OneDrive - DHI\Desktop\South Boulder Creek\25 XS_AsbuiltvsLiDAR\5 XNSComparison-EM_CEM_AsbuiltDEM-AllBranches\XS Plots - EM, CEM, Asbuilt")
start_time = time.time()
log_file = open("XNS Comparison log.txt","w+")
log_file.write('XNS Comparison \nDeveloped by Shubhneet Singh\nssin@dhigroup.com\nJune 2021\n')

# Option to run all rivers or rivers list
if all_rivers == 1:
    rivers_names = get_branch_names(rivers)

# Loop over rivers names list
Total_xns_EM = 0
Three_topo_count = 0
Two_topo_count = 0
One_topo_count = 0

horizontal_datumshift_chainages = [19411.02, 19463.91, 21092.52, 21494.16, 25377.1, 25559.38, 25694.0, 27755.91, 27903.28, 28047.21, 28185.57, 28314.21, 28460.27, 28564.96, 28703.45, 28810.47, 28913.39, 29090.26,29145.6, 31145.47, 31224.57, 33444.42, 46771.82, 47052.1, 50157.81 ]
horizontal_datum_move = [-80, -100, -130, -100, -180, -250, -150, -130, -160, -140, -130, -50, -100, -100, -100, -100, -50, -70, -70, -80, -65, -340, -140, -160, -100  ]

for river_name in rivers_names:
    print('Procesing: {}'.format(river_name))
    # Getting the river object for input topo of rivers
    first_river_chainages = get_topo_chainages(rivers, river_name, topo_id_names[0])
    second_river_chainages = get_topo_chainages(rivers, river_name, topo_id_names[1])
    # If three input topos:
    if len(topo_id_names)>2:
        third_river_chainages = get_topo_chainages(rivers, river_name, topo_id_names[2])
    else:
        third_river_chainages = None

    number_matching_chainage, all_topo_chainage_match = compare_chainages(river_name, topo_id_names, log_file) 
    
    Total_xns_EM += len(all_topo_chainage_match)
   
    for chainage in range(len(all_topo_chainage_match)):
        
        if number_matching_chainage[chainage]=='3_topo_ids':
                Three_topo_count += 1           
                all_topo_coords = [get_xsection_coords(data, river_name, topo_id_names[i], all_topo_chainage_match[chainage][i]) for i in range(len(topo_id_names))]
                # Move few EM topo xns to match with CEM plots
                curr_chainage =  round(all_topo_chainage_match[chainage][0]*3.28084, 2)                
                if river_name == 'South Boulder Creek' and (curr_chainage in horizontal_datumshift_chainages):
                    horizontal_shift_index =  horizontal_datumshift_chainages.index(curr_chainage)                    
                    horizontal_datum_move_this = horizontal_datum_move[horizontal_shift_index]
                    all_topo_coords[0][0]= [x + horizontal_datum_move_this  for x in all_topo_coords[0][0]]
                    
                plot_message_CEM, plot_message_Asbuilt = plot_xsection(river_name, topo_id_names, all_topo_chainage_match[chainage][0], all_topo_coords)
                if len(plot_message_Asbuilt) != 0:
                    log_file.write(plot_message_Asbuilt)  
                    
        elif number_matching_chainage[chainage]=='first_second':
                Two_topo_count += 1
                all_topo_coords = [get_xsection_coords(data, river_name, topo_id_names[i], all_topo_chainage_match[chainage][i]) for i in [0,1]]
                plot_message_CEM, plot_message_Asbuilt = plot_xsection(river_name, topo_id_names, all_topo_chainage_match[chainage][0], all_topo_coords)
                if len(plot_message_CEM) != 0:
                    log_file.write(plot_message_CEM)
                plot_message_CEM
                
        elif number_matching_chainage[chainage]=='first_third':
                 Two_topo_count += 1
                 all_topo_coords = [get_xsection_coords(data, river_name, topo_id_names[i], all_topo_chainage_match[chainage][i]) for i in [0,2]]
                 plot_message_CEM, plot_message_Asbuilt = plot_xsection(river_name, topo_id_names, all_topo_chainage_match[chainage][0], all_topo_coords) 
                 if len(plot_message_Asbuilt) != 0:
                    log_file.write(plot_message_Asbuilt)                  
        elif number_matching_chainage[chainage]=='first_only':
                 One_topo_count += 1
                 all_topo_coords = [get_xsection_coords(data, river_name, topo_id_names[i], all_topo_chainage_match[chainage][i]) for i in [0]]
                 plot_xsection(river_name, topo_id_names, all_topo_chainage_match[chainage][0], all_topo_coords) 

# Some additional info for log_file
log_file.write('\n############\n')
log_file.write('\nNumber of 3 topo plots [EM, CEM, Asbuilt]: {}\n'.format(Three_topo_count))
log_file.write('\nNumber of 2 topo plots [EM, CEM or EM, Asbuilt]: {}\n'.format(Two_topo_count))
log_file.write('\nNumber of 1 topo plots [EM only]: {}\n'.format(One_topo_count))
log_file.write('\nTotal cross-sections in EM: {}\n'.format(Total_xns_EM))
log_file.write('\nTime taken: {}'.format(str(round(((time.time() - start_time)/60),0))) + ' minutes')
log_file.close()