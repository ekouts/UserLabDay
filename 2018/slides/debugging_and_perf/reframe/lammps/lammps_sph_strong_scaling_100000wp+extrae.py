import os

import reframe.utility.sanity as sn
from reframe.core.launchers import LauncherWrapper
from reframe.core.pipeline import RunOnlyRegressionTest


class LAMMPSPerfHackathon(RunOnlyRegressionTest):
    def __init__(self, name, **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)

        self.valid_prog_environs = ['PrgEnv-gnu']
        self.modules = ['LAMMPS/16Jul2018-CrayGNU-18.07-cuda-9.1',
                        'Extrae/3.5.4-CrayGNU-18.07']
        self.sourcesdir = 'src/sph/water_collapse/100000wp'

        self.sanity_patterns = sn.assert_found(r'Total wall time:',
                                               self.stdout)

        self.perf_patterns = {
            'perf': sn.extractsingle(r'\s+(?P<perf>\S+) timesteps/s',
                                     self.stdout, 'perf', float),
        }

        self.maintainers = ['JG', 'MKr']
        self.strict_check = False
        self.tags = {'scs'}
        self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.descr = 'LAMMPS PerfHackathon benchmark'
        self.executable = './extrae/extrae_daint.sh'
        self.num_tasks_per_node = 12
        self.num_cpus_per_task = 1
        self.time_limit = (0, 20, 0)
        self.pre_run = ['gunzip data.initial.gz && module swap gcc/7.3.0 && ']
        self.pre_run += ['ldd `which lmp_mpi` && which lmp_mpi ']
        #self.report_file = 'lmp_mpi.prv'
        self.post_run = [
            'module list -t && ls -la ',
        ]
        self.variables = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task),
                }

    def setup(self, system, environ, **job_opts):
        super().setup(system, environ, **job_opts)

        self.job.launcher = LauncherWrapper(self.job.launcher, '/usr/bin/time',
                                            ['-p'])
        self.job.launcher.options = ['--unbuffered']


class LAMMPSStrongScaling(LAMMPSPerfHackathon):
    def __init__(self, num_tasks, **kwargs):
        super().__init__('LAMMPS_%s_100000wp_strong+extrae' % (str(num_tasks)), **kwargs)

        #input_name = '-in water_collapse.lmp'
        #self.executable_opts = [input_name]
        self.num_tasks = num_tasks


def _get_checks(**kwargs):
    ret = []
    #for num_tasks in [12, 24, 48, 96, 192]:
    for num_tasks in [12, 24, 48]:
    #for num_tasks in [24]:
        ret.append(LAMMPSStrongScaling(num_tasks, **kwargs))

    return ret
