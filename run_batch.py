import getopt
import os
import sys
import multiprocessing as mp
from run_experiments import experiment, get_dir_string
from local.sender_hybrid import SenderHybrid
from local.sender_longformer import SenderLongformer
from local.sender_dataset_level import SenderDatasetLevel
from local.sender_idf_baseline import SenderIDFBaseline
from external.receiver import Receiver
from data_manage.oracle import Oracle
from additionalScripts.output_config import OutputConfig

# Convenience script for running batches of experiments
longopts = ['dataset=', 'iterations=', 'keys=', 'model=', 'distribution=', 'average_runs=',
            'buffer_size=', 'buffer_sample_size=', 'split_sample=', 'alpha=',
            'epsilon=', 'term_borrowing=', 'ts_features=', 'seeds=']
optlist, _ = getopt.getopt(sys.argv[1:], '', longopts)

if len(optlist) != len(longopts):

    opts_provided = [x[0] for x in optlist]

    # required options
    for opt in ['--dataset', '--iterations', '--keys']:
      assert opt in opts_provided, f'{opt} must be specified'

    print('...**DEFAULTS**...')
    for opt, default in [('--average_runs', '1'),
    ('--distribution', 'uniform'), ('--alpha', 0.2), ('--epsilon', 0.05),
    ('--buffer_size', 50), ('--buffer_sample_size', 8), ('--split_sample', 'false'),
    ('--model', 'dataset_level'), ('--term_borrowing', 'false'),
    ('--ts_features', 'false'), ('--seeds', None)]:
      if opt not in opts_provided:
        print(f'{opt}={default}')
        optlist.append((opt, default))
    print()

experiment_config = dict()
experiment_config['average_runs'] = []
experiment_config['seeds'] = []
receiver_config = dict()
sender_config = dict()
print('...**ARGS**...')
for opt, arg in optlist:
    print(f'{opt}={arg}')
    if opt == '--dataset':
        dataset_name = arg
    elif opt == '--iterations':
        experiment_config['interactions'] = int(arg)  # iterations to run (i.e., amount of times we try to match tuples)
    elif opt == '--keys':
        experiment_config['query_length'] = int(arg)  # keywords to send (length of query)
    elif opt == '--average_runs':
        for avgRun in arg.split(','):
            experiment_config['average_runs'].append(int(avgRun))  # Spawns <averageRuns> processes
    elif opt == '--model':
        model_opt = arg
    elif opt == '--distribution':
        distribution = arg
    elif opt == '--alpha':
        sender_config['alpha'] = float(arg)
    elif opt == '--epsilon':
        sender_config['epsilon'] = float(arg)
    elif opt == '--buffer_size':
        sender_config['buffer_size'] = int(arg)
    elif opt == '--buffer_sample_size':
        sender_config['buffer_sample_size'] = int(arg)
    elif opt == '--split_sample':
        sender_config['split_sample'] = True if arg.lower() == 'true' else False
    elif opt == '--term_borrowing':
        sender_config['external_term_borrowing'] = True if arg.lower() == 'true' else False
    elif opt == '--ts_features':
        sender_config['external_feat_specific'] = True if arg.lower() == 'true' else False
    elif opt == '--seeds':
        if arg is not None:
            for seed in arg.split(','):
                experiment_config['seeds'].append(int(seed))  # Used for re-creating zipf distributions
    else:
        print(' - Not used! This may be a mistake.')
print()

# Experiment parameters
dataset_path = 'datasets/'
experiment_config['top_k_size'] = 20
experiment_config['dataset_name'] = dataset_name

config_path = 'output_path_config'

# Receiver parameters
receiver_config['data_file_path'] = dataset_path + dataset_name + '/target.csv'
receiver_config['dataset_name'] = dataset_name
receiver_config['config_path'] = config_path

# Sender parameters
sender_config['distribution'] = distribution
sender_config['data_file_path'] = dataset_path + dataset_name + '/source.csv'
sender_config['dataset_name'] = dataset_name
sender_config['window_size'] = 50
sender_config['rr_threshold'] = 1/15
sender_config['config_path'] = config_path

# Filepath for where experiment results will be saved "<config_path>/<experiment_details>"
# Add additional configuration settings here to distinguish between experiments run
if model_opt == 'idf':
    model_name = 'idf_baseline'
else:
    model_name = model_opt

if model_opt == 'idf':
    experiment_config['save_path'] = OutputConfig(config_path).paths['experiment_results'] + \
                                     get_dir_string(experiment_config, ['dataset_name', 'query_length', 'interactions', 'distribution']) + '/' + \
                                     model_name + '-' + get_dir_string(sender_config, ['distribution'])
elif model_opt == 'longformer':
    experiment_config['save_path'] = OutputConfig(config_path).paths['experiment_results'] + \
                                     get_dir_string(experiment_config, ['dataset_name', 'query_length', 'interactions', 'distribution']) + '/' + \
                                     model_name + '-' + get_dir_string(sender_config, ['epsilon', 'distribution', 'external_feat_idf', 'external_feat_specific', 'external_term_borrowing', 'buffer_size', 'buffer_sample_size', 'split_sample'])
else:
    experiment_config['save_path'] = OutputConfig(config_path).paths['experiment_results'] + \
                                     get_dir_string(experiment_config, ['dataset_name', 'query_length', 'interactions', 'distribution']) + '/' + \
                                     model_name + '-' + get_dir_string(sender_config, ['alpha', 'distribution', 'external_feat_idf', 'external_feat_specific', 'external_term_borrowing'])

    if model_opt == 'hybrid':
        experiment_config['save_path'] += '-' + get_dir_string(sender_config, ['window_size', 'rr_threshold'])

if len(experiment_config['seeds']) > 0:
    check_path = experiment_config['save_path'] + '/' + str(experiment_config['interactions']) + '_seed=' + str(experiment_config['seeds'][0]) + '_AverageRun=' + str(experiment_config['average_runs'][0]) + '.zip'
else:
    check_path = experiment_config['save_path'] + '/' + str(experiment_config['interactions']) + '_AverageRun=' + str(experiment_config['average_runs'][0]) + '.zip'

if os.path.exists(check_path):
    print('experiments exist')
    exit()

if not os.path.exists(experiment_config['save_path']):
    print(experiment_config['save_path'] + " does not exist.")
    print('Averaged runs: {}'.format(experiment_config['average_runs']))
    print('creating: ' + experiment_config['save_path'])
    os.makedirs(experiment_config['save_path'])
else:
    print(experiment_config['save_path'] + " exists.")
    print('Averaged runs: {}'.format(experiment_config['average_runs']))

# Create models
    # Receiver
receiver = Receiver(receiver_config)

    # Sender
if model_opt == 'dataset_level':
    sender = SenderDatasetLevel(sender_config, receiver)
elif model_opt == 'hybrid':
    sender = SenderHybrid(sender_config, receiver)
elif model_opt == 'longformer':
    sender = SenderLongformer(sender_config, receiver)
elif model_opt == 'idf':
    sender = SenderIDFBaseline(sender_config, receiver)
else:
    print(f'{model_opt} is not a valid model option')

    # Oracle
oracle = Oracle(dataset_path + dataset_name + '/ground_truth.csv')

if model_opt == 'longformer':
    assert len(experiment_config['average_runs']) == 1
    assert len(experiment_config['seeds']) == 1
    experiment(experiment_config, sender, oracle, receiver, experiment_config['average_runs'][0], experiment_config['seeds'][0])
else:
    process_list = []
    for i, run in enumerate(experiment_config['average_runs']):
        if len(experiment_config['seeds']) > 0:
            p = mp.Process(target=experiment, args=(experiment_config, sender, oracle, receiver, run, experiment_config['seeds'][i]))
        else:
            p = mp.Process(target=experiment, args=(experiment_config, sender, oracle, receiver, run))
        p.start()
        process_list.append(p)

    for p in process_list:
        p.join()

print('Complete.')