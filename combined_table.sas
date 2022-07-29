/* combine genfi spreadsheets into one table */
/* keep and clean relevant columns */
/* create baseline and most recent visit tables */
/* June14/22, Jill McCarthy */

/* libname statement */
%let path=~/GENFI;
libname genfi "&path/data";

/* compare number and names of variables in genfi1 and genfi2 */
proc compare data=genfi.clinical1 compare=genfi.clinical2 novalues;
run;
/* demographics is all the same, clinical, imaging and neuropsych are not */

/* combine genfi1 and genfi2 and sort */
data demographics;
	set genfi.demographics1 genfi.demographics2;
proc sort; by 'Blinded Code'n Visit;
run;

/* Many of the variable names have spaces in them - will change later */
options validvarname=any;

/* combine clinical genfi1 and 2, keep only wanted variables, sort */
data clinical;
	set genfi.clinical1(drop=Sleep) genfi.clinical2(drop=Sleep); *sleep is different type in genfi 1 and 2;
	keep 'Blinded Code'n -- 'Age at Onset'n Diagnosis -- 'El-Escorial'n 'CDR-SOB'n 
		'FTLD-CDR-SOB'n MMSE CBI_Total 'FRS_%'n'CDR-SOB'n 'FTLD-CDR-SOB'n MMSE CBI_Total 'FRS_%'n;
proc sort; by 'Blinded Code'n Visit;
run;

/* combine imaging, keep wanted imaging variables, */
/* rename 2 with different names in genfi1 and 2, sort */
data imaging;
	set genfi.imaging1(rename=('T1 Protocol Used'n = T1_protocol Date=Scan_date)) 
		genfi.imaging2(rename=('T1 Protocol'n = T1_protocol 'Date of scan'n = Scan_date));
	keep 'Blinded Code'n -- T1_protocol;
proc sort; by 'Blinded Code'n Visit;
run;

/* combine neuropsych, drop unneeded variables, sort */
data neuropsych;
	set genfi.neuropsych1 genfi.neuropsych2;
	drop  DS_B_max DS_F_max Log_memory_delayed Log_memory_immediate TMTA_errors TMTB_errors 
			 Benson_figure_copy Benson_figure_recall Benson_recognition TMTA_lines TMTB_lines 
			  'C+C'n VF_vegetables  Ekman_SUBSCORE Faux_pas_SUBSCORE FCRST_del_free FCRST_del_total 
			  FCRST_free FCRST_total Language MiniSEA_total Stroop_color_time Stroop_ink_time 
			  Stroop_word_time;
proc sort; by 'Blinded Code'n Visit;
run;

/* merge tables */
data combined;
	merge demographics(in=d) imaging(in=i) clinical(in=c) neuropsych(in=n);
	by 'Blinded Code'n Visit;
	if d; 
run;
/* 2 rows in imaging not in any others - no info except t1 protocol */
/*  two rows in others not in imaging - no scan for that visit */

/* rename columns, rename categories, missing data, etc */
data combined2(rename=(Affected1=Affected));
length Genetic_Status Gorno_Tempini El_Escorial $25;
format Assessment_date Scan_date date9.;
set combined;
if _N_ < 3 then delete;
rename 'Blinded Code'n = Blinded_Code
		'Blinded Site'n = Blinded_Site
		'Genetic Group'n = Genetic_group
		'Blinded Family'n = Blinded_Family
		'Age at Visit'n = Age_at_visit
		'Age at Onset'n = Age_at_onset
		 'FRS_%'n = FRS_percent
		 'FTLD-CDR-SOB'n = FTLD_CDR_SOB;
		 
CDR_SOB = input('CDR-SOB'n, 2.);

if 'Genetic Status 1'n = "P" and 'Genetic Status 2'n = 0 then Genetic_Status = "Negative";
else if 'Genetic Status 1'n = "P" and 'Genetic Status 2'n = 1 then Genetic_Status = "Positive - Asymptomatic";
else if 'Genetic Status 1'n = "A" and 'Genetic Status 2'n = 2 then Genetic_Status = "Positive - Symptomatic";

if Gender = "0" then Gender = "Female";
else if Gender = "1" then Gender = "Male";
else if Gender ne " " then Gender = "Unknown";

if Handedness = "0" then Handedness = "Right";
else if Handedness = "1" then Handedness = "Left";
else if Handedness ne " " then Handedness = "Unknown";

if Affected = 1 then Affected1 = "Yes";
else if Affected = 0 then Affected1 = "No";
else if Affected ne . then Affected1 = "Unknown";

if Rascovsky = "1" then Rascovsky = "Probable";
else if Rascovsky = "2" then Rascovsky = "Possible";
else if Rascovsky ne " " then Rascovsky = "Unknown";

if 'Gorno-Tempini'n = "1" then Gorno_Tempini = "NOS";
else if 'Gorno-Tempini'n = "2" then Gorno_Tempini = "nfv";
else if 'Gorno-Tempini'n = "3" then Gorno_Tempini = "sv";
else if 'Gorno-Tempini'n = "4" then Gorno_Tempini = "lv";
else if 'Gorno-Tempini'n  ne " " then Gorno_Tempini = "Unknown";

if 'El-Escorial'n = "1" then El_Escorial = "Definite";
else if 'El-Escorial'n = "2" then El_Escorial = "Probable";
else if 'El-Escorial'n = "2" then El_Escorial = "Lab-supported";
else if 'El-Escorial'n = "2" then El_Escorial = "Possible";
else if 'El-Escorial'n ne " " then El_Escorial = "Unknown";

/* Convert dates from excel to sas dates */
Assessment_date = 'Date of Assessment'n - 21916;
Scan_date = Scan_date - 21916;

drop 'Genetic Status 1'n 'Genetic Status 2'n Affected 'Gorno-Tempini'n 'El-Escorial'n 'Date of Assessment'n 'CDR-SOB'n;
run;

/* clean up values in clinical, neuropsych tests */

proc means data=combined2;
var MMSE -- Block_Design;
run;

data combined3;
set combined2;
if MMSE = 99 then MMSE = .;
if FRS_percent = 999 or FRS_percent = -1 then FRS_percent = .;
if CBI_Total = -1 then CBI_Total = .;
run;

proc means data=combined3;
var MMSE -- Block_Design;
run;

data genfi.all_genfi;
retain Blinded_Code Blinded_Site Visit Genetic_Group Blinded_Family Genetic_Status Assessment_date Age_at_visit 
		Gender Handedness Education Employment Ethnicity EYO Scan_date Scanner T1_Protocol Affected
		Age_at_onset Diagnosis Rascovsky Gorno_Tempini El_Escorial CDR_SOB FTLD_CDR_SOB;
set combined3; 
run;

/* create baseline dataset */
data genfi.bl_genfi;
set genfi.all_genfi;
by Blinded_Code Visit;
if first.Blinded_Code and first.Visit;
run;

/* create dataset of most recent visits */
data genfi.recent_genfi;
set genfi.all_genfi;
by Blinded_Code Visit;
if last.Blinded_Code and last.Visit;
run;


	













