function a = computeFeatures(file_path)
% https://doi.org/10.21105/joss.00671
% https://zenodo.org/badge/latestdoi/128659224
addpath(genpath('G:\python project\apneaECGCode\preprocessOfApneaECG\BioSigKit'))
read_path = strcat(file_path, '\denoised_ecg_data.mat');
ecg_data = load(read_path);
ecg_data_1 = ecg_data.denoised_ecg_data;
a = 0;

Analysis = RunBioSigKit(ecg_data_1, 100, 0);          % Uses ECG1 as input,Fs=250
%-------------------- Call Pan Tompkins Algorithm ------------------- %
% Analysis.MTEO_qrstAlg;                        % Runs MTEO algorithm
% QRS = Analysis.Results.R;                     % Stores R peaks in QRS
%-------------------- Call MTEO QRS ------------------- %
try
    Analysis.MTEO_qrstAlg;                        % Runs MTEO algorithm
    Qwave = Analysis.Results.Q;
    Rwave = Analysis.Results.R;
    Swave = Analysis.Results.S;
    Twave = Analysis.Results.T;
    Pwave = Analysis.Results.P;
    EDR = Analysis.EDR_comp;
    save_path = strcat(file_path, '\Qwave.mat');
    save(save_path, 'Qwave');
    save_path = strcat(file_path, '\Rwave.mat');
    save(save_path, 'Rwave');
    save_path = strcat(file_path, '\Swave.mat');
    save(save_path, 'Swave');
    save_path = strcat(file_path, '\Twave.mat');
    save(save_path, 'Twave');
    save_path = strcat(file_path, '\Pwave.mat');
    save(save_path, 'Pwave');
    save_path = strcat(file_path, '\EDR.mat');
    save(save_path, 'EDR');
    disp('Successfully.');
catch
    disp('it is noise.');
end

end

