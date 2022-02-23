HCP_S3_MOUNT_PATH = ~/s3_hcp
HCP_REST_DATA = https://osf.io/g759t/download/
HCP_TASK_DATA = https://osf.io/s4h8j/download/ 
BRAIN_ATLAS = https://osf.io/j5kuc/download
DATA_PATH = ~/hcp_data

s3fs_install:
	sudo apt install s3fs

s3_hcp_mount:
	mkdir $(HCP_S3_MOUNT_PATH)
	s3fs hcp-openaccess $(HCP_S3_MOUNT_PATH) -o passwd_file=/content/drive/Othercomputers/My\ Laptop/Working_Memory/.cred/.passwd-s3fs

s3_hcp_unmount:
	unmount $(HCP_S3_MOUNT_PATH)

#Preprocessed data from NeuroMatchAcademy
#Mineault, Patrick, Carsen Stringer, Jorge A Menendez, Pierre-Étienne Fiquet, Byron Galbraith, Michael Waskom, Bernard M ’t Hart, et al. 2022. “Neuromatch Academy.” OSF. January 7. osf.io/hygbm.
get_task_data:
	mkdir $(DATA_PATH)
	cd $(DATA_PATH)
	wget $(HCP_TASK_DATA) -o hcp_task.tar.gz
	tar -xf hcp_task.tar.gz

get_rest_data:
	mkdir $(DATA_PATH)
	cd $(DATA_PATH)
	wget $(HCP_REST_DATA) -o hcp_rest.tar.gz

get_brain_atlas:
	mkdir $(DATA_PATH)
	cd $(DATA_PATH)
	wget $(BRAIN_ATLAS) -o brain_atlas.npy

get_all:
	get_task_data get_rest_data get_brain_atlas
