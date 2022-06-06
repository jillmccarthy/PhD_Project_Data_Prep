# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:52:52 2018
Combine 3 original GENFI spreadsheets
Extract relevant info to make one combined table
Add info about imaging to table - which subjects have which scans (T1, fMRI, DWI, ASL) for which visits
@author: jill
"""

#%%
import pandas as pd
import numpy as np
import os
import glob #find files using wildcards
#import fnmatch
import re
import datetime as dt

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 30)


#read in excel files
demographics_genfi1 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_DEMOGRAPHICS_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI1')
demographics_genfi2 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_DEMOGRAPHICS_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI2')

imaging_genfi1 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_IMAGING_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI1')
imaging_genfi2 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_IMAGING_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI2')

clinical_genfi1 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_CLINICAL_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI1')
clinical_genfi2 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_CLINICAL_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI2')

#remove unneeded columns
imaging_genfi1 = imaging_genfi1.iloc[:,0:7]  #removing regional volume columns
imaging_genfi2 = imaging_genfi2.iloc[:,0:7]

clinical_genfi1 = clinical_genfi1.loc[:,"Blinded Code":"El-Escorial"]  #removing behaviours, etc
clinical_genfi2 = clinical_genfi2.loc[:,"Blinded Code":"El-Escorial"]
clinical_genfi1 = clinical_genfi1.drop(['First symptom', 'First symptom.1', 'First symptom.2'], axis=1)
clinical_genfi2 = clinical_genfi2.drop(['First symptom', 'First symptom.1', 'First symptom.2'], axis=1)

#find header names
demographics_genfi1_headers = list(demographics_genfi1) #or can do: demographics_genfi1.columns.values.tolist()
demographics_genfi2_headers = list(demographics_genfi2)

imaging_genfi1_headers = list(imaging_genfi1)
imaging_genfi2_headers = list(imaging_genfi2)

clinical_genfi1_headers = list(clinical_genfi1)
clinical_genfi2_headers = list(clinical_genfi2)

#find dataframe size
demographics_genfi1_size = demographics_genfi1.shape
demographics_genfi2_size = demographics_genfi2.shape

imaging_genfi1_size = imaging_genfi1.shape
imaging_genfi2_size = imaging_genfi2.shape

clinical_genfi1_size = clinical_genfi1.shape
clinical_genfi2_size = clinical_genfi2.shape

#check if genfi1 and genfi2 have the same number of columns and the same header names
demographics_genfi1_size[1] == demographics_genfi2_size[1]  #true
demographics_genfi1_headers == demographics_genfi2_headers  #true

imaging_genfi1_size[1] == imaging_genfi2_size[1]  #true  
imaging_genfi1_headers == imaging_genfi2_headers  #false

clinical_genfi1_size[1] == clinical_genfi2_size[1]  #true
clinical_genfi1_headers == clinical_genfi2_headers  #true

#so need to fix imaging dataframes (not worried about neuropsych)
#find different header names
print(imaging_genfi1_headers)
print(imaging_genfi2_headers)
imaging_genfi1 = imaging_genfi1.rename(columns={"Date":"Date of scan"})
imaging_genfi2 = imaging_genfi2.rename(columns={"T1 Protocol":"T1 protocol used"})
del imaging_genfi1["QC_include in VBM"]
del imaging_genfi2["Unnamed: 6"]
#update headers
imaging_genfi1_headers = list(imaging_genfi1)
imaging_genfi2_headers = list(imaging_genfi2)
imaging_genfi1_headers == imaging_genfi2_headers  #true
print(imaging_genfi1_headers)
print(imaging_genfi2_headers)

#combine GENFI1 and GENFI2 for each dataframe
demographics_unsorted = demographics_genfi1.append(demographics_genfi2)
imaging_unsorted = imaging_genfi1.append(imaging_genfi2)
clinical_unsorted = clinical_genfi1.append(clinical_genfi2)

#sort dataframes by subject id
demographics = demographics_unsorted.sort_values(["Blinded Code"])
imaging = imaging_unsorted.sort_values(["Blinded Code"])
clinical = clinical_unsorted.sort_values(["Blinded Code"])

#reset index after sorting dataframe (resets to numbered index - don't do if want labeled index)
demographics = demographics.reset_index(drop=True)
imaging = imaging.reset_index(drop=True)
clinical = clinical.reset_index(drop=True)

#display first 5 rows for each dataframe
demographics.head()
imaging.head()
clinical.head()

#Check length is the same for all
demographics.shape[0] == imaging.shape[0] == clinical.shape[0]  #True

## Create one table with all the information I want

#extract data from each of the dataframes
clinical_selected = clinical.loc[:, "Affected":]
imaging_selected = imaging.loc[:, "Date of scan":"T1 protocol used"]

#concatenate tables
genfi = pd.concat([demographics, imaging_selected, clinical_selected], axis=1)
genfi.head(n=20)

#add index using subject id and visit
genfi = genfi.set_index(["Blinded Code", "Visit"], drop=False)
genfi.index.names = ['Subject', 'Visit']
genfi = genfi.sort_index() #resort table
genfi.head()

#edit values in columns
genfi.loc[(genfi['Genetic status 1'] == 'P'), 'Genetic status 1'] = 'asymp'
genfi.loc[(genfi['Genetic status 1'] == 'A'), 'Genetic status 1'] = 'symp'

genfi.loc[(genfi['Genetic status 2'] == 0), 'Genetic status 2'] = 'neg'
genfi.loc[(genfi['Genetic status 2'] == 1), 'Genetic status 2'] = 'pos - asymp'
genfi.loc[(genfi['Genetic status 2'] == 2), 'Genetic status 2'] = 'pos - symp'

genfi.loc[(genfi['Gender'] == 0), 'Gender'] = 'F'
genfi.loc[(genfi['Gender'] == 1), 'Gender'] = 'M'

genfi.loc[(genfi['Affected'] == 1), 'Affected'] = 'Y'
genfi.loc[(genfi['Affected'] == 0), 'Affected'] = 'N'

genfi.loc[(genfi['Handedness'] == 1), 'Handedness'] = 'L'
genfi.loc[(genfi['Handedness'] == 0), 'Handedness'] = 'R'
genfi.loc[(genfi['Handedness'] == 2), 'Handedness'] = '?'

genfi['Diagnosis'].unique()  #find labels for diagnosis
genfi.Rascovsky.unique()   #find bvFTD labels (1 probable, 2 possible, 0 ??, nan asymp)

genfi.loc[genfi['Rascovsky'] == 1, 'Rascovsky'] = 'probable'
genfi.loc[genfi['Rascovsky'] == 2, 'Rascovsky'] = 'possible'
# 1=NOS; 2=nfv; 3=sv; 4=lv
genfi.loc[genfi['Gorno-Tempini'] == 1, 'Gorno-Tempini'] = 'NOS'
genfi.loc[genfi['Gorno-Tempini'] == 2, 'Gorno-Tempini'] = 'nfv'
genfi.loc[genfi['Gorno-Tempini'] == 3, 'Gorno-Tempini'] = 'sv'
genfi.loc[genfi['Gorno-Tempini'] == 4, 'Gorno-Tempini'] = 'lv'
# 1=definite; 2=probable; 3=lab-supported; 4=possible
genfi.loc[genfi['El-Escorial'] == 1, 'El-Escorial'] = 'definite'
genfi.loc[genfi['El-Escorial'] == 2, 'El-Escorial'] = 'probable'
genfi.loc[genfi['El-Escorial'] == 3, 'El-Escorial'] = 'lab-supported'
genfi.loc[genfi['El-Escorial'] == 4, 'El-Escorial'] = 'possible'

#remove first row (that is not a subject)
genfi = genfi.iloc[2:,:]

#replace NaNs with 'N/A'
genfi = genfi.fillna('N/A')

#Add data for those visits with imaging but no data in tables (GRN169, GRN206)
grn169 = genfi.loc['GRN169',:]
grn169_11 = grn169
grn169_11 = grn169_11.reset_index(drop=True)
grn169_11.loc[:,'Visit'] = 11.0
grn169_11.loc[:,['Date of assessment', 'Age at visit', 'EYO', 'Scanner', 'Diagnosis', 'Rascovsky', 'Gorno-Tempini', 'El-Escorial']] = np.nan
scandate_matlab = int(736265)
scandate_python = (dt.datetime.fromordinal(scandate_matlab) + dt.timedelta(days=scandate_matlab%1) - dt.timedelta(days = 366)) #convert matlab date into regular date
grn169_11.loc[:,'Date of scan'] = scandate_python
grn169_11 = grn169_11.set_index(["Blinded Code", "Visit"], drop=False)
grn169_11.index.names = ['Subject', 'Visit']
genfi = pd.concat([genfi, grn169_11])
genfi = genfi.sort_index() #resort table

scandate_matlab = int(736666)
scandate_python = (dt.datetime.fromordinal(scandate_matlab) + dt.timedelta(days=scandate_matlab%1) - dt.timedelta(days = 366)) #convert matlab date into regular date
genfi.loc[('GRN206', 12.0),['Date of scan']] = scandate_python 
genfi.loc[('GRN206', 12.0),['Scanner']] = 'Philips 3T' 

#%% Create new columns indicated what imaging each subject had at what visit

# Get list of subject folders containing imaging files

path = "/data/SD_FTD/jill/subject_folders/"
filenames= os.listdir(path) # get all files' and folders' names in the current directory

subjects = []
for filename in filenames: # loop through all the files and folders
    if os.path.isdir(os.path.join(path, filename)): # check whether the current object is a folder or not
        subjects.append(filename)
subjects.sort()

#Initialize tables for each modality
T1s = pd.DataFrame(columns = ['Subject', 'Visit', 'Date of scan', 'scandate_python', 'T1'])
fMRIs = pd.DataFrame(columns = ['Subject', 'Visit', 'Date of scan', 'scandate_python', 'fMRI'])
DWIs = pd.DataFrame(columns = ['Subject', 'Visit', 'Date of scan', 'Visit Name', 'DWI'])
ASLs = pd.DataFrame(columns = ['Subject', 'Visit', 'Date of scan', 'Visit Name', 'ASL'])

#Get list of all subjects from table
all_subjects = list(genfi.index.levels[0])

#Append information on which modality each subject visit has to each table

for subject in all_subjects:
    #print(subject)

    #Get rows for corresponding subject
    genfi_subject = genfi.loc[(subject,), :]
    
    #For MRI

    #Find MRI files for each subject
    mod_path = os.path.join(path, subject, 'MRI')
    if os.path.isdir(mod_path):
       niftis = glob.glob(os.path.join(mod_path, 'T1*.nii')) 
       #glob.glob(mod_path + '/T1*.nii')  #this also works! (but need the extra / in front)
       
       #extract scandate from files and compare to Date of scan table column; append relevant data to modality table                                 
       for index, row in genfi_subject.iterrows():
           for scan in niftis:
               dates = re.findall(r'\d{6}', scan) #use regular expressions to find scandate
               scandate_matlab = int(dates[0])
               scandate_python = (dt.datetime.fromordinal(scandate_matlab) + dt.timedelta(days=scandate_matlab%1) - dt.timedelta(days = 366)) #convert matlab date into regular date
               
               if row['Date of scan'] == scandate_python:
                   T1s = T1s.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'scandate_python': scandate_python, 'T1': 'Y'}, ignore_index=True)
                   
           if T1s.empty == True:
               T1s = T1s.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'scandate_python': 'NaN', 'T1': 'N'}, ignore_index=True)
    
                   
           elif not (T1s.iloc[-1, 0] == subject and T1s.iloc[-1, 1] == index):
               T1s = T1s.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'scandate_python': 'NaN', 'T1': 'N'}, ignore_index=True)
    else:
        for index, row in genfi_subject.iterrows():
            T1s = T1s.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'scandate_python': 'NaN', 'T1': 'N'}, ignore_index=True)
           
    #For fMRI
    mod_path = os.path.join(path, subject, 'FUNC')
    if os.path.isdir(mod_path):
        niftis = glob.glob(os.path.join(mod_path, 'fMRI*.nii'))
       
        for index, row in genfi_subject.iterrows():
            for scan in niftis:
               dates = re.findall(r'\d{6}', scan) #use regular expressions to find scandate
               scandate_matlab = int(dates[0])
               scandate_python = (dt.datetime.fromordinal(scandate_matlab) + dt.timedelta(days=scandate_matlab%1) - dt.timedelta(days = 366)) #convert matlab date into regular date
               
               if row['Date of scan'] == scandate_python:
                   fMRIs = fMRIs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'scandate_python': scandate_python, 'fMRI': 'Y'}, ignore_index=True)
           
            if fMRIs.empty == True:
              fMRIs = fMRIs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'scandate_python': 'NaN', 'fMRI': 'N'}, ignore_index=True)
           
            elif not (fMRIs.iloc[-1, 0] == subject and fMRIs.iloc[-1, 1] == index):
               fMRIs = fMRIs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'scandate_python': 'NaN', 'fMRI': 'N'}, ignore_index=True)
    else:
         for index, row in genfi_subject.iterrows():
             fMRIs = fMRIs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'scandate_python': 'NaN', 'fMRI': 'N'}, ignore_index=True)  
             
    #For DTI
    mod_path = os.path.join(path, subject, 'DTI')
    if os.path.isdir(mod_path):
       # file are in separate folders for visit within subject folder
       folders = glob.glob(os.path.join(mod_path, 'V*'))
       #match visit numbers from folder names and table
       for index, row in genfi_subject.iterrows():
           for scan in folders:
               visit_name = re.findall(r'V\d\d', scan)   #find visit
               
               if visit_name[0] == 'V01':
                   visit = 1.0
               elif visit_name[0] == 'V02':
                   visit = 2.0
               elif visit_name[0] == 'V03':
                   visit = 3.0
               elif visit_name[0] == 'V11':
                   visit = 11.0
               elif visit_name[0] == 'V12':
                   visit = 12.0
                  
               if index == visit:
                  DWIs = DWIs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'Visit Name': visit_name[0], 'DWI': 'Y'}, ignore_index=True)
           
           if DWIs.empty == True:
               DWIs = DWIs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'Visit Name': 'NaN', 'DWI': 'N'}, ignore_index=True)
    
           elif not (DWIs.iloc[-1, 0] == subject and DWIs.iloc[-1, 1] == index):
               DWIs = DWIs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'Visit Name': 'NaN', 'DWI': 'N'}, ignore_index=True)
               
    else:
        for index, row in genfi_subject.iterrows():
            DWIs = DWIs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'Visit Name': 'NaN', 'DWI': 'N'}, ignore_index=True)
            
    #For ASL
    mod_path = os.path.join(path, subject, 'VASC')
    if os.path.isdir(mod_path):
        folders = glob.glob(os.path.join(mod_path, 'Nifti*'))
        #match visit numbers
        for index, row in genfi_subject.iterrows():
           for scan in folders:
               visit_name = re.findall(r'V\d\d', scan)   #find visit
               
               if visit_name[0] == 'V01':
                   visit = 1.0
               elif visit_name[0] == 'V02':
                   visit = 2.0
               elif visit_name[0] == 'V03':
                   visit = 3.0
               elif visit_name[0] == 'V11':
                   visit = 11.0
               elif visit_name[0] == 'V12':
                   visit = 12.0
                   
               if index == visit:
                  ASLs = ASLs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'Visit Name': visit_name[0], 'ASL': 'Y'}, ignore_index=True)
                  
           if ASLs.empty == True:
               ASLs = ASLs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'Visit Name': 'NaN', 'ASL': 'N'}, ignore_index=True)

           elif not (ASLs.iloc[-1, 0] == subject and ASLs.iloc[-1, 1] == index):
               ASLs = ASLs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'Visit Name': 'NaN', 'ASL': 'N'}, ignore_index=True)
    else:
        for index, row in genfi_subject.iterrows():
            ASLs = ASLs.append({'Subject': subject, 'Visit': index, 'Date of scan': row['Date of scan'], 'Visit Name': 'NaN', 'ASL': 'N'}, ignore_index=True)
  
#Add index to modality tables          
T1s = T1s.set_index(["Subject", "Visit"], drop=False)
fMRIs = fMRIs.set_index(["Subject", "Visit"], drop=False)
DWIs = DWIs.set_index(["Subject", "Visit"], drop=False)
ASLs = ASLs.set_index(["Subject", "Visit"], drop=False)

#Rename scandate_python column
T1s = T1s.rename(columns={"scandate_python":"T1 Scandate"})
fMRIs = fMRIs.rename(columns={"scandate_python":"fMRI Scandate"})

#Add modality columns to genfi table
genfi['T1'] = T1s['T1']
genfi['fMRI'] = fMRIs['fMRI']
genfi['DWI'] = DWIs['DWI']
genfi['ASL'] = ASLs['ASL']



#%%

#save genfi to an excel file
#genfi.to_excel('/export02/data/GENFI/spreadsheets/genfi_table_py.xlsx', index=False)


