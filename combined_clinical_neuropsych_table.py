#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 11:08:29 2020
add relevant columns from clinical and neuropsychological spreadsheets to master table (created with genfi_combined_table.py - but table updated since)
@author: jill
"""
#%%
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 30)

#read in excel files
clinical_genfi1 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_CLINICAL_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI1')
clinical_genfi2 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_CLINICAL_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI2')

neuropsych_genfi1 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_NEUROPSYCH_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI1')
neuropsych_genfi2 = pd.read_excel('/export02/data/GENFI/spreadsheets/GENFI_NEUROPSYCH_DF3_FINAL_BLINDED.xlsx', sheet_name = 'GENFI2')

#remove first row from each
clinical_genfi1 = clinical_genfi1.iloc[1:,:]
clinical_genfi2 = clinical_genfi2.iloc[1:,:]
neuropsych_genfi1 = neuropsych_genfi1.iloc[1:,:]
neuropsych_genfi2 = neuropsych_genfi2.iloc[1:,:]

#find header names
clinical_genfi1_headers = list(clinical_genfi1)
clinical_genfi2_headers = list(clinical_genfi2)

neuropsych_genfi1_headers = list(neuropsych_genfi1)
neuropsych_genfi2_headers = list(neuropsych_genfi2)

#find dataframe size
clinical_genfi1_size = clinical_genfi1.shape
clinical_genfi2_size = clinical_genfi2.shape

neuropsych_genfi1_size = neuropsych_genfi1.shape
neuropsych_genfi2_size = neuropsych_genfi2.shape

#check if genfi1 and genfi2 have the same number of columns and the same header names
clinical_genfi1_size[1] == clinical_genfi2_size[1]  #false
clinical_genfi1_headers == clinical_genfi2_headers  #false

neuropsych_genfi1_size[1] == neuropsych_genfi2_size[1]  #false
neuropsych_genfi1_headers == neuropsych_genfi2_headers  #false

#remove unwanted columns
clinical_genfi1_new = clinical_genfi1.drop(clinical_genfi1.loc[:,'Affected.1':'EMG'].columns, axis=1)
clinical_genfi1_new = clinical_genfi1_new.drop(clinical_genfi1_new.loc[:,'Supranuclear':'Severity'].columns, axis=1)

clinical_genfi2_new = clinical_genfi2.drop(clinical_genfi2.loc[:,'Affected.1':'No_of_drugs'].columns, axis=1)
clinical_genfi2_new = clinical_genfi2_new.drop(clinical_genfi2_new.loc[:,'Supranuclear':'Post_instability'].columns, axis=1)

neuropsych_genfi1_new = neuropsych_genfi1.drop(['Log_memory_immediate', 'TMTA_lines', 'TMTB_lines', 'VF_vegetables', 'Log_memory_delayed'], axis=1)
neuropsych_genfi2_new = neuropsych_genfi2.drop(['Benson_figure_copy', 'C+C', 'Benson_figure_recall', 'Benson_recognition', 'FCRST_free', 'FCRST_total', 'Stroop_color_time', 'Stroop_word_time', 'Stroop_ink_time', 'FCRST_del_free', 'FCRST_del_total'], axis=1)

#check headings again
clinical_genfi1_headers_new = list(clinical_genfi1_new) 
clinical_genfi2_headers_new = list(clinical_genfi2_new)

neuropsych_genfi1_headers_new = list(neuropsych_genfi1_new)
neuropsych_genfi2_headers_new = list(neuropsych_genfi2_new)

#clinical
#columns in genfi1 not in genfi2
list(set(clinical_genfi1_headers_new) - set(clinical_genfi2_headers_new)) #sleep named differently
#rename sleep column in genfi1 to match genfi2
clinical_genfi1_new = clinical_genfi1_new.rename(columns={"Sleep":"Sleep.1"})
#columns in genfi2 not in genfi1
list(set(clinical_genfi2_headers_new) - set(clinical_genfi1_headers_new)) #correct

#neuropsych
#columns in genfi1 not in genfi2
list(set(neuropsych_genfi1_headers_new) - set(neuropsych_genfi2_headers_new)) #none
#columns in genfi2 not in genfi1
list(set(neuropsych_genfi2_headers_new) - set(neuropsych_genfi1_headers_new)) #correct

#%%

#combine tables
clinical_unsorted = pd.concat([clinical_genfi1_new, clinical_genfi2_new], axis=0, ignore_index=True, sort=False)
list(clinical_unsorted)
neuropsych_unsorted = pd.concat([neuropsych_genfi1_new, neuropsych_genfi2_new], axis=0, ignore_index=True, sort=False)
list(neuropsych_unsorted)

#sort table
clinical = clinical_unsorted.sort_values(["Blinded Code", "Visit"])
neuropsych = neuropsych_unsorted.sort_values(["Blinded Code", "Visit"])

#change visit to match master genfi table
clinical.loc[clinical['Visit'] == 1.0, 'Visit'] = 'V01'
clinical.loc[clinical['Visit'] == 2.0, 'Visit'] = 'V02'
clinical.loc[clinical['Visit'] == 3.0, 'Visit'] = 'V03'
clinical.loc[clinical['Visit'] == 11.0, 'Visit'] = 'V11'
clinical.loc[clinical['Visit'] == 12.0, 'Visit'] = 'V12'
neuropsych.loc[neuropsych['Visit'] == 1.0, 'Visit'] = 'V01'
neuropsych.loc[neuropsych['Visit'] == 2.0, 'Visit'] = 'V02'
neuropsych.loc[neuropsych['Visit'] == 3.0, 'Visit'] = 'V03'
neuropsych.loc[neuropsych['Visit'] == 11.0, 'Visit'] = 'V11'
neuropsych.loc[neuropsych['Visit'] == 12.0, 'Visit'] = 'V12'

# Add index
clinical = clinical.set_index(["Blinded Code", "Visit"], drop=False)
clinical.index.names = ['Subject', 'VisitName']
neuropsych = neuropsych.set_index(["Blinded Code", "Visit"], drop=False)
neuropsych.index.names = ['Subject', 'VisitName']

#combine clinical and neuropysch tables
clinical.shape[0] == neuropsych.shape[0] #same number of rows
clinical_neuropsych = pd.merge(clinical, neuropsych, how='outer', on = ['Subject', 'VisitName'], indicator=True)
clinical_neuropsych['_merge'].value_counts()  # all both
del clinical_neuropsych['_merge']
del clinical_neuropsych['Blinded Code_y']
del clinical_neuropsych['Visit_y']
del clinical_neuropsych['Blinded Site_y']
clinical_neuropsych = clinical_neuropsych.rename(columns={"Blinded Code_x":"Blinded Code"})
clinical_neuropsych =clinical_neuropsych.rename(columns={"Visit_x":"Visit"})
clinical_neuropsych =clinical_neuropsych.rename(columns={"Blinded Site_x":"Blinded Site"})

#%% Clean up variable values

#correct ones where no test score
clinical_neuropsych.loc[clinical_neuropsych['MMSE'] == 99, 'MMSE'] = np.nan
clinical_neuropsych.loc[clinical_neuropsych['FRS_%'] == 999, 'FRS_%'] = np.nan
clinical_neuropsych.loc[clinical_neuropsych['FRS_%'] == -1, 'FRS_%'] = np.nan
clinical_neuropsych.loc[clinical_neuropsych['ALSFRS_total'] == 99, 'ALSFRS_total'] = np.nan

clinical_neuropsych_memory = clinical_neuropsych.loc[:, 'Memory.1':'RSMS_SP']
clinical_neuropsych_memory = clinical_neuropsych_memory.drop(['CDR-SOB', 'FTLD-CDR-SOB'], axis=1)
clinical_neuropsych_memory = clinical_neuropsych_memory.replace(-1, 99999)

clinical_neuropsych.update(clinical_neuropsych_memory)
clinical_neuropsych = clinical_neuropsych.replace(99999, np.nan)


#add to genfi table

genfi_table = pd.read_excel('/export02/data/GENFI/spreadsheets/genfi_table_mar25_2020.xlsx')

#add index using subject id and visit
genfi_table = genfi_table.set_index(["Blinded Code", "Visit"], drop=False)
genfi_table.index.names = ['Subject', 'VisitName']
genfi_table = genfi_table.sort_index() #resort table
genfi_table.head()

#delete columns in both tables
clinical_neuropsych_tocombine = clinical_neuropsych.drop(clinical_neuropsych.loc[:, 'Blinded Code': 'El-Escorial'].columns, axis=1)

#merge tables
genfi_clinical_neuropsych = pd.merge(genfi_table, clinical_neuropsych_tocombine, how='outer', on = ['Subject', 'VisitName'], indicator=True)
genfi_clinical_neuropsych['_merge'].value_counts()  # all both
del genfi_clinical_neuropsych['_merge']

#save to excel file
genfi_clinical_neuropsych.to_excel('/export02/data/GENFI/spreadsheets/genfitable_clinical_neuropsych.xlsx', index=False)
clinical_neuropsych.to_excel('/export02/data/GENFI/spreadsheets/clinical_neuropsych_apr162020.xlsx', index=False)

