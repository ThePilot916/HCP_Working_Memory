import os
import numpy as np
from enum import Enum
from typing import List

class PhaseEncoding(Enum):
    RL = 0
    LR = 1

N_REGIONS = 360 #glasser et.al 2016 MSMAll 360 cortical parcellations
N_HCP_NMA_SUBJECTS = 339    #unclear on the subject subset specifics
TR = 0.72   #temporal resolution of 720ms
FPS = 1/0.72 #MRI frames per sec
N_RUNS = 2  #two runs viz. [Right to Left] and [Left to Right] phase encoding scans

EXPERIMENTS = {
    'REST'       : {'runs':[1,2,3,4], 'cond':[], 'res':[]},
    'MOTOR'      : {'runs':[5,6],     'cond':['lf','rf','lh','rh','t','cue'], 'res':[]},
    'WM'         : {'runs':[7,8],     'cond':['0bk_body','0bk_faces','0bk_places','0bk_tools','2bk_body','2bk_faces','2bk_places','2bk_tools'], 'res':['0bk_cor','2bk_cor','0bk_err','2bk_err','all_bk_cor','all_bk_err']},#how to extract fixation blocks
    'EMOTION'    : {'runs':[9,10],    'cond':['fear','neut'], 'res':[]},
    'GAMBLING'   : {'runs':[11,12],   'cond':['loss','win'], 'res':['loss_event','neut_event','win_event']},
    'LANGUAGE'   : {'runs':[13,14],   'cond':['math','story'], 'res':['present_math','question_math','response_math','present_story','question_story','response_story']},
    'RELATIONAL' : {'runs':[15,16],   'cond':['match','relation'], 'res':[]},
    'SOCIAL'     : {'runs':[17,18],   'cond':['mental','rnd'], 'res':['mental_resp','other_resp']}
}

def run_identifier(run: int) -> str:
    """Return run phase encoding direction given the run identifier for timeseries data

    Args:
        run(int): run identifier number
    
    Returns:
        (str): phase encoding direction - "LR" or "RL" 
    """
    if run % 2 == 0:
        return 'LR'
    return 'RL'

def load_brain_atlas(path: str) -> dict:
    """ Loads brain atlas

    Args:
        path(str): path to brain_atlas.npy
    
    Returns:
        (dict): brain_atlas dict
    """
    with np.load(path) as npz_obj:
        brain_atlas = dict(npz_obj)
    return brain_atlas

def load_regions(path: str) -> dict:
    """Loads brain_parcellations(associated with glasser 360 brain parcellation) region name and network info as dict

    Args:
        path(str): path to regions.npy
    
    Returns:
        (dict): dict consisting of "name" and "network" associated with glasser 360 brain parcellation
    """
    regions_transpose = np.load(path).T
    regions = dict(name = regions_transpose[0].tolist(),
                   network = regions_transpose[1].tolist(),
              )
    return regions

def normalize_data(data: np.ndarray) -> np.ndarray:
    """ Normalizes numpy nparray to the range [0, 1]

    Args:
        data (np.ndarray): input numpy array to be normalized

    Returns:
        np.ndarray: normalized data
    """
    data = (data - np.min(data)) / np.ptp(data)
    return data

def load_subject_data(nma_data_path: str, subject_id: int, experiment: str, run: str = None, run_id: int = None, normalize: bool = True) -> np.ndarray:
    """Loads single subject's timeseries data for specified experiment, run(phase encoding) and condition

    Args:
        data_path (str): path to hcp_nma_data (task/rest)
        subject_id (int): id of subject to be loaded
        experiment (str): experiment name
        run (str): phase encoding 'RL' or 'LR' (not applicable for REST data)
        condition (str): condition of the experiment (EVs) (not applicable for REST data)
        run_id (int): returns data for the specified run (overrides run str parameters)
    Returns:
        np.ndarray: timeseries data of the subject for specified experiment, run and condition
    """
    if experiment != "REST":
        if run_id is None:
            if run == "RL":
                run_id = PhaseEncoding.RL
            else:
                run_id = PhaseEncoding.LR
    else:
        run_id -= 1
    run_id = EXPERIMENTS[experiment]["runs"][run_id]
    subject_data_path = os.path.join(data_path,f"hcp_task/subjects/{str(subject_id)}/timeseries/bold{run_id}_Atlas_MSMAll_Glasser360Cortical.npy")
    subject_timeseries_data = np.load(subject_data_path)
    if normalize:
        subject_timeseries_data = normalize_data(subject_timeseries_data)
    return subject_timeseries_data

def load_EV_mapped_data(nma_data_path: str, subject_ids: Any, experiment: str, run: str, conditions: Any, normalize: bool = True) -> dict:
    """extracts subject timeseries data mapped to specified condition

    Args:
        nma_data_path (str): path to nma_hcp_data
        subject_id (List[int] or int): ids of subjects to be loaded
        experiment (str): name of the experiment
        run (str): phase encoding (LR/RL)
        cond (List[str]): condition of the experiment (block)
        normalize (bool, optional): normalize data to 0-1. Defaults to True.

    Returns:
        dict: returns mapped subject timeseries data to EV condition
    """
    if isinstance(subject_ids, int):
        subject_ids = [subject_ids]
    subject_dicts = {}
    for subject_id in subject_ids:
        subject_dict = {}
        subject_data = load_subject_data(nma_data_path, subject_id, experiment)
        if isinstance(conditions, str):
            conditions = [conditions]
        for condition in conditions:
            ev_file_path = os.path.join(nma_data_path, f"hcp_task/subjects/{str(subject)}/EVs/tfMRI_{experiment}_{run}/{condition}.txt")
            ev_array = np.loadtxt(fname=ev_file_path,ndmin=2)
            ev_count = 0
            ev_dict = {}
            for ev in ev_array:
                start = np.floor(ev[0]*FPS).astype(int)
                duration = np.ceil(ev[1]*FPS).astype(int)
                ev_dict.update({ev_count:{"ev_details":{"start":ev[0], "duration":ev[1]},
                                        "frame_details":{"start":start, "duration":duration},
                                        "timeseries":subject_data[:][start:start+duration]}})
                ev_count += 1
            subject_dict.update({condition:ev_dict})
        subject_dicts.update({subject:subject_data})
    return subject_dicts