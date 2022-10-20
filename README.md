# Effective Entity Augmentation By Querying External Data Sources
Datasets can be found here: https://drive.google.com/drive/folders/18sxf7d_VWSre9nZ2kXk7eDVOf_2hSs4Q?usp=sharing

Save paths must be specified prior to running the code. This is done by creating the "output_path_config" in 
the additionalScripts directory (i.e., "additionalScripts/output_path_config"). The file should contain this content
(but paths should be specified for your machine):
```
processed_data|F:/data/processed_data/
database_index|F:/data/index/
experiment_results|F:/
```
Local and external data structures are stored at "processed_data" path. The indexed database is stored at 
"database_index" path. Experiment results are stored at "experiment_results" path. Set these to your preferred paths
depending on the machine.

Experiments are run using run_experiments.py. Much of both the experimental and mediator (i.e., sender) parameters can 
be changed through their respective config dictionaries. Using different models is as easy as changing which is 
instantiated (i.e.; SenderIDFBaseline, SenderDatasetLevel, SenderHybrid, SenderLongformer).