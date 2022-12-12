from contextlib import closing
import logging
import socket
import parsl
from parsl.addresses import address_by_hostname
from parsl.executors import WorkQueueExecutor, ThreadPoolExecutor
from parsl.launchers import SrunLauncher
from parsl.monitoring.monitoring import MonitoringHub
from parsl.providers import SlurmProvider, LocalProvider
from parsl.utils import get_all_checkpoints


def get_free_port():
    """Return a free port on the local host.
    See https://stackoverflow.com/questions/1365265/
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = s.getsockname()[1]
        return port


def set_parsl_logging(log_level=logging.INFO):
    """Set parsl logging levels."""
    loggers = [_ for _ in logging.root.manager.loggerDict
               if _.startswith('parsl')]
    loggers.append('database_manager')
    for logger in loggers:
        logging.getLogger(logger).setLevel(log_level)
    return log_level


def set_config_options(retries, monitoring, workflow_name, checkpoint,
                       monitoring_debug):
    """
    Package retries, monitoring, and checkpoint options for
    parsl.config.Config as a dict.
    """
    config_options = {'retries': retries}
    if monitoring:
        config_options['monitoring'] \
            = MonitoringHub(hub_address=address_by_hostname(),
                            hub_port=55055,
                            monitoring_debug=monitoring_debug,
                            resource_monitoring_interval=60,
                            workflow_name=workflow_name)
    if checkpoint:
        config_options['checkpoint_mode'] = 'task_exit'
        config_options['checkpoint_files'] = get_all_checkpoints()

    return config_options


def local_provider(nodes_per_block=1):
    """
    Factory function to provide a LocalProvider, with the option to
    set the number of nodes to use.  If nodes_per_block > 1, then
    use `launcher=SrunLauncher(overrides='-K0 -k --slurmd-debug=verbose')`,
    otherwise use the default, `launcher=SingleNodeLauncher()`.
    """
    provider_options = dict(nodes_per_block=nodes_per_block,
                            init_blocks=0,
                            min_blocks=0,
                            max_blocks=1,
                            parallelism=0,
                            cmd_timeout=300)
    if nodes_per_block > 1:
        provider_options['launcher'] \
             = SrunLauncher(overrides='-K0 -k --slurmd-debug=verbose')
    return LocalProvider(**provider_options)


def slurm_provider(nodes_per_block=1, constraint='cpu', qos='regular',
                   walltime='10:00:00', time_min=None):
    """Factory function to provide a SlurmProvider for running at NERSC."""
    scheduler_options = (f'#SBATCH --constraint={constraint}\n'
                         f'#SBATCH --qos={qos}\n'
                         '#SBATCH --module=cvmfs\n'
                         '#SBATCH -L cvmfs')
    if time_min:
        scheduler_options = '\n'.join((scheduler_options,
                                       f'#SBATCH --time-min={time_min}'))
    provider_options = dict(walltime=walltime,
                            scheduler_options=scheduler_options,
                            nodes_per_block=nodes_per_block,
                            exclusive=True,
                            init_blocks=0,
                            min_blocks=0,
                            max_blocks=1,
                            parallelism=0,
                            launcher=SrunLauncher(
                                overrides='-K0 -k --slurmd-debug=verbose'),
                            cmd_timeout=300)
    return SlurmProvider('None', **provider_options)


def thread_pool_config(max_threads=1, monitoring=False, workflow_name=None,
                       checkpoint=False, retries=1,
                       labels=('local',),
                       monitoring_debug=False):
    """Load a parsl config using ThreadPoolExecutor."""
    executors = [ThreadPoolExecutor(max_threads=max_threads, label=label)
                 for label in labels]
    config_options = set_config_options(retries, monitoring, workflow_name,
                                        checkpoint, monitoring_debug)
    config = parsl.config.Config(executors=executors, **config_options)
    return parsl.load(config)


def workqueue_config(provider=None, monitoring=False, workflow_name=None,
                     checkpoint=False, retries=1, worker_options="",
                     wq_max_retries=1, port=None, monitoring_debug=False):
    """Load a parsl config for a WorkQueueExecutor and the supplied provider."""
    if provider is None:
        provider = local_provider()

    if port is None:
        port = get_free_port()

    executors = [WorkQueueExecutor(label='work_queue', port=port,
                                   shared_fs=True, provider=provider,
                                   worker_options=worker_options,
                                   autolabel=False,
                                   max_retries=wq_max_retries)]

    config_options = set_config_options(retries, monitoring, workflow_name,
                                        checkpoint, monitoring_debug)

    config = parsl.config.Config(strategy='simple',
                                 garbage_collect=False,
                                 app_cache=True,
                                 executors=executors,
                                 **config_options)
    return parsl.load(config)
