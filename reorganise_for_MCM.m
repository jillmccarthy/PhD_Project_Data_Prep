function reorganise_for_MCM(new_folder_path, factor_orig_path, factor_folders, factor_name, parcellation_orig_path, parcellation_folders, parcellation_name, ...
parcellation_template, connectome_orig_path, connectome_folders, connectome_name)

% to reorganise imaging data into required format to work with the NeuroPM toolbox (cTI and MCM)
% for data organised in separate folders for subject and for modality ie subject_ID/modality/files or subject_ID/modality/visit/files
%reorganized as subject_ID/files (files named as factor_1_timepoint1 ... connectome_N_timepointN)

%factor/parcellation input files must be .nii or .nii.gz
%connectome input files must be .txt and top half only (as created by Mrtrix3)

% to rename files using the visit number, this must be in the file name or path (V##)
% to rename file using age in years (current method now needed for NeuroPM), scandate and birthdate must be in the file name or path, or in the original (unprocessed) 
	file name, within the same session folder

%inputs ----

%factor/parcellation/connectome_orig_files = path to root folder containing subject folders for the files
%factor/parcellation/connectome_folders = folders containing the files ie {'MRI/toDARTEL', 'fMRI', 'DWI'} (can be single folder or multiple folders (for each session), can include *)
%factor/parcellation/connectome_name = name of the image file(s) (can include *)
%parcellation_template = path to parcellation template
%new_folder_path = path to the new folder to store the copied and renamed files

%inputs equal to 0 if not being included

%% create new_folder_path
if ~exist(new_folder_path, 'dir')
    mkdir(new_folder_path)
end

%% read in text file with full paths of files to be excluded (ones that failed quality control)
fid = fopen('/export02/data/GENFI/QC_excluded.txt');
files_to_exclude = textscan(fid,'%s');
fclose(fid);
files_to_exclude = files_to_exclude{1,1};

%% brain images corresponding to each biological factor of interest, grey matter parcellation images, connectomes for each subject)

possible_inputs = ["factor" "parcellation" "connectome"];
for input = 1:length(possible_inputs)
    
    inputs_types = possible_inputs(input);
    switch inputs_types     
        case "factor"
            if ~isempty(factor_name)
                
                disp ' ';
                disp '-----------';
                disp 'Copying brain images corresponding to each biological factor of interest ...';
                disp ' ';
                
                inputs_path = factor_orig_path;
                inputs_folders = factor_folders;
                inputs_name = factor_name;
                
                input_type = "factor";
            else
                disp 'no brain images corresponding to each biological factor of interest provided'
                continue
            end
            
        case "parcellation"  
            %if using subject-specific parcellations ...
            if ~isempty(parcellation_name)
                
                disp ' ';
                disp '-----------';
                disp 'Copying grey matter parcellation images ...';
                disp ' ';
                
                inputs_path = parcellation_orig_path;
                inputs_folders = parcellation_folders;
                inputs_name = parcellation_name;
                
                input_type = "parcellation";
           
            %if using parcellation template, copy template to root folder 
            elseif ~isempty(parcellation_template)
                
                disp ' ';
                disp '-----------';
                disp 'Copying parcellation template ...';
                disp ' ';
                
                copyfile(parcellation_template, new_folder_path)
                continue
                
            else
                disp 'no parcellation images provided'
                continue
                
            end
            
        case "connectome"
            
            if ~isempty(connectome_name)
                
                disp ' ';
                disp '-----------';
                disp 'Copying connectome images ...';
                disp ' ';
                
                input_type = "connectome";
                
                inputs_path = connectome_orig_path;
                inputs_folders = connectome_folders;
                inputs_name = connectome_name

            else
                disp 'no connectome images provided'
                continue
            end
    end
    
    
    
    %Find subject directories
    subject_IDs = find_subject_directories(inputs_path);
    
    for subject = 1:length(subject_IDs)
        ID_subject = char(subject_IDs(subject));
        disp(['Subject -> ' ID_subject])
        
        %path to subject folder containing original output files
        subject_dir = [inputs_path filesep ID_subject];
        
        %create subject folder in new_folder_path
        if ~exist([new_folder_path filesep ID_subject], 'dir')
            mkdir([new_folder_path filesep ID_subject])
        end
        
        %if files already exist in new folder, skip
        if input_type == "factor"
            existing_files = dir([new_folder_path filesep ID_subject filesep 'factor*']);
            if ~isempty(existing_files)
                % files already exist
                disp(['Subject ' ID_subject ' already has factor files'])
                continue
            end
        elseif input_type == "parcellation"
            existing_files = dir([new_folder_path filesep ID_subject filesep 'parcellation*']);
            if ~isempty(existing_files)
                % files already exist
                disp(['Subject ' ID_subject ' already has parcellation files'])
                continue
            end
        elseif input_type == "connectome"
            existing_files = dir([new_folder_path filesep ID_subject filesep 'connectome*']);
            if ~isempty(existing_files)
                % files already exist
                disp(['Subject ' ID_subject ' already has connectome files'])
                continue
            end
        end
        
        %for each folder within the subject folder - loop over folders (will be either folders for modality or session (for parcellation/connectomes))
        for input_folder_num = 1:length(inputs_folders)
            
            %if file_folders contains * for multiple folders
            if contains(inputs_folders{input_folder_num}, '*')
                session_dirs = dir([subject_dir filesep inputs_folders{input_folder_num}]);   %subject session folders
                
                %if subject does not have this modality (only relevant for factors)
                if isempty(session_dirs)
                    disp(['Subject ' ID_subject ' does not have modality ' num2str(input_folder_num)])
                    continue
                end
                %for each session folder
                clear files_dir
                for session_num = 1:length(session_dirs)
                    files_dir(session_num,:) = [session_dirs(session_num).folder filesep session_dirs(session_num).name];   %subjects session output folders
                end
                
                %if file_folders does not contain multiple folders
            else
                files_dir = [subject_dir filesep inputs_folders{input_folder_num}];   %subjects output folder
                %if subject does not have this modality
                if ~exist(files_dir, 'dir')
                    disp(['Subject ' ID_subject ' does not have modality ' num2str(input_folder_num)])
                    continue
                end
            end
            
            %for each output folder
            for file_folder_num = 1:size(files_dir, 1)
                file_folder = files_dir(file_folder_num, :);
                
                % to test
                %cd(file_folder)
                
                %find output files (factors or parcellation or connectome)
                for inputs_num = 1:length(inputs_name)
                    input_files = dir([file_folder filesep inputs_name{inputs_num}]);  %could be muiltple files or single file here
                    
                    %if no files for this factor in this folder, skip
                    if isempty(input_files)
                        continue
                    end
                    
                    for input_files_num = 1:length(input_files)
                        file_path = [input_files(input_files_num).folder filesep input_files(input_files_num).name];
                        
                        % check if file failed QC
                        
                        % check file_path against list
                        excluded_file = files_to_exclude(strcmp(file_path, files_to_exclude));
                        if ~isempty(excluded_file)
                            % if it is in the list, skip it
                            disp([inputs_name{inputs_num} ' -> file failed QC and will be excluded'])
                            continue
                        end
                        
                        % if file is .gz need to gunzip
                        if file_path(end-5:end) ==  "nii.gz"
                                file_path_gz = file_path;
                                file = gunzip(file_path_gz);
                                file_path = [input_files(input_files_num).folder filesep file{1}];
                                delete(file_path_gz)
                        end
                        
                        %check files are the correct type
                        if input_type == "factor" || input_type == "parcellation"
                            %if file is not a 'nii', give error
                            if ~(file_path(end-2:end) == "nii")
                                warning('file must be .nii')
                            end
                        elseif input_type == "connectome"
                            %if file is not a 'txt', give error
                            if ~(file_path(end-2:end) == "txt")
                                warning('file must be .txt')
                            end
                            %Add bottom half to connectomes
                            C = load(file_path);
                            C = C + (C - C.*eye(size(C)))';
                            ind = find(file_path == '/');
                            new_file_path = [file_path(1:ind(end)) 'full_' file_path(ind(end)+1:end)];
                            save(new_file_path, 'C', '-ascii', '-double'); 
                            file_path = new_file_path;
                        end
                        
                        ind_visit = regexp(file_path, 'V[0-3]{2}');  %to find visit name for GENFI files
                        file_visit = file_path(ind_visit:ind_visit+2);
                        ind_date = regexp(file_path, '\d{6}');
                        
                        %if dates are not in the factor file, get from orig files
                        if length(ind_date) < 2
                            orig_files = dir([file_folder filesep '*scandate*birthdate*']);
                            clear orig_scandates orig_birthdates
                            for i = 1:length(orig_files)
                                orig_ind_date = regexp(orig_files(i).name, '\d{6}');
                                orig_scandates(i) = str2double(orig_files(i).name(orig_ind_date(1):orig_ind_date(1)+5));
                                orig_birthdates(i) = str2double(orig_files(i).name(orig_ind_date(2):orig_ind_date(2)+5));
                            end
                            orig_scandate_unique = unique(orig_scandates);
                            orig_birthdates_unique = unique(orig_birthdates);
                            if length(orig_birthdates_unique) ~= 1
                                error('birthdates are different!')
                            end
                            scandates_sorted = sort(orig_scandate_unique);    
                            file_scandate = scandates_sorted(input_files_num);
                            file_birthdate = orig_birthdates_unique;
                        else
                            %Get scandate and birthdate for factors when dates are in the name
                            file_scandate = str2double(file_path(ind_date(1):ind_date(1)+5));
                            file_birthdate = str2double(file_path(ind_date(2):ind_date(2)+5));
                        end
                        
                        %get age at scan aquisition in years
                        file_aqu_days = file_scandate - file_birthdate;
                        file_aqu_years = num2str(file_aqu_days/365);
                        
                        %rename file (with factor/parcellation/connectome number and age at aquisition in name)
                        input_number = num2str(inputs_num);
                        
                        if input_type == "factor"
                            %new_file_name = ['factor_' input_number '_' file_visit '.nii'];
                            new_file_name = ['factor_' input_number '_' file_aqu_years '.nii'];
                        elseif input_type == "parcellation"
                            %new_file_name = ['parcellation_' input_number '_' file_visit '.nii'];
			    new_file_name = ['parcellation_' input_number '_' file_aqu_years '.nii'];
                        elseif input_type == "connectome"
                            %new_file_name = ['connectome_' input_number '_' file_visit '.txt'];
                            new_file_name = ['connectome' input_number '_' file_aqu_years '.txt'];
                        end
                        
                        %copy file to new folder, with new name
                        try
                            copyfile(file_path, [new_folder_path filesep ID_subject filesep new_file_name])
                        catch
                            warning('error copying file, %s, %s, %s', ID_subject, file_visit, inputs_name);
                        end  
                    end
                end
            end           
        end
    end  
end

% delete empty subject directories
ids = find_subject_directories(new_folder_path);
for folder = 1:length(ids)
    status = rmdir([new_folder_path filesep ids{folder}]);
    if status == 1
        disp(['no files copied for ' char(ids(folder)) ' -> folder removed'])
    end
end
 
%% List which factor/parcellation/connectome is which in case of multiple (ie T1 = Factor 1, fMRI = Factor 2 ...)

 for input = 1:length(possible_inputs)
     
     inputs_types = possible_inputs(input);
     switch inputs_types
         case "factor"
             % if factor_name input does not exist, then skip this section ...
             if ~isempty(factor_name)
                 
                 disp ' ';
                 disp '-------------------------';
                 for inputs_num = 1:length(factor_name)
                     disp([factor_name{inputs_num} ' = Factor ' num2str(inputs_num)])
                 end
             end
             
         case "parcellation"
             
             if ~isempty(parcellation_name)
                 
                 disp ' ';
                 disp '-------------------------';
                 for inputs_num = 1:length(parcellation_name)
                     disp([parcellation_name{inputs_num} ' = GM_parcellation ' num2str(inputs_num)])
                 end
             end
             
         case "connectome"
             
             if ~isempty(connectome_name)
                 disp ' ';
                 disp '-------------------------';
                 for inputs_num = 1:length(connectome_name)
                     disp([connectome_name{inputs_num} ' = Connectome ' num2str(inputs_num)])
                 end
             end
     end
     
 end