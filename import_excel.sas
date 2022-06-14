*to import all genfi spreadsheets;
*June14/22, Jill McCarthy;

*libname statement;
%let path=~/GENFI;
libname genfi "&path/data";

*import all genfi spreadsheets;
%macro excel_import(file_name, sheet_name, out_name);

proc import datafile="&path/data/&file_name"
	out=genfi.&out_name dbms=xlsx replace;
	sheet="&sheet_name";
run;

%mend excel_import;

%excel_import(GENFI_DEMOGRAPHICS_DF3_FINAL_BLINDED.xlsx, genfi1, demographics1);
%excel_import(GENFI_DEMOGRAPHICS_DF3_FINAL_BLINDED.xlsx, genfi2, demographics2);

%excel_import(GENFI_IMAGING_DF3_FINAL_BLINDED.xlsx, genfi1, imaging1);
%excel_import(GENFI_IMAGING_DF3_FINAL_BLINDED.xlsx, genfi2, imaging2);

%excel_import(GENFI_CLINICAL_DF3_FINAL_BLINDED.xlsx, genfi1, clinical1);
%excel_import(GENFI_CLINICAL_DF3_FINAL_BLINDED.xlsx, genfi2, clinical2);

%excel_import(GENFI_NEUROPSYCH_DF3_FINAL_BLINDED.xlsx, genfi1, neuropsych1);
%excel_import(GENFI_NEUROPSYCH_DF3_FINAL_BLINDED.xlsx, genfi2, neuropsych2);
