function ID_subjects = find_subject_directories(path)

% to find subject folders
% input: path = the path to your subjects folders
% output: ID_subjects = string array of subject ids

tmp = dir(path);
tmp_names = {tmp.name};
ID_subjects = tmp_names([tmp.isdir] & ~ismember(tmp_names, {'.', '..'}));

end