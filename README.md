# scissorhands

A python module for generating Eddie3 (SunGridEngine) qsub scripts.

## Installation

1. Download/clone this repository.
2. Install using the `setup.py` file, or with pip.

```bash
git clone https://github.com/carragherlab/scissorhands
cd scissorhands
python setup.py install --user # or pip install .
```

## Examples

### Manually creating submission scripts

```python
from scissorhands.script_generator import AnalysisScript

my_script = AnalysisScript(name="example_job", memory="12G")

print(my_script)
```

The `user` argument is automatically detected if code is ran on the cluster, and if an output location `-o` is not given, then this defaults to the user's scratch space.

```sh
#!/bin/sh

#$ -N example_job
#$ -l h_vmem=12G
#$ -l h_rt=06:00:00
#$ -o /exports/eddie/scratch/s1027820/
#$ -j y

. /etc/profiles.d/modules.sh
```

Code can be added to the job template.

```python

to_run = """
         module load R
         Rscript my_R_code.R
         """

my_script.template += to_run

print(my_script)
```

```shell
#!/bin/sh

#$ -N example_job
#$ -l h_vmem=2G
#$ -l h_rt=06:00:00
#$ -o /exports/eddie/scratch/s1027820/
#$ -j y

. /etc/profiles.d/modules.sh

module load R
Rscript my_R_code.R

```

After saving, scripts can be submitted to the queue if the session
is on a cluster login node.

```python
my_script.save("my_script.sh").submit()
```

------------

### Submission script generator

To generate, save and submit submission scripts in a loop *(though you should use an
array job for this sort of task)*:

```python
from scissorhands.script_generator import AnalysisScript

to_run = ["Rscript my_script_{}.R".format(i) for i in range(10)]

for index, code_snippet in enumerate(to_run):
    script = AnalysisScript(name="job_{}".format(index))
    script.template += code_snippet
    script.save("job_{}.sh".format(index))
    script.submit()
```

------------

### Creating array jobs

If we have a text file of commands, with a command per line.

e.g `my_commands.txt`:

```shell
python script.py --arg1 10 --arg2 1
python script.py --arg1 20 --arg2 1
python script.py --arg1 30 --arg2 1
python script.py --arg1 10 --arg2 2
python script.py --arg1 20 --arg2 2
python script.py --arg2 30 --arg2 2
```

We want to run this as an array job.

```python
from scissorhands.script_generator import AnalysisScript

# Get the number of lines/commands in the file (should be 6 in this example)
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f, 1):
            pass
    return i

n_commands = file_len("my_commands.txt")

# make submission script
my_script = AnalysisScript(name="my_array_job", tasks=n_commands)
my_script.template += "module load python\n"
my_script.loop_through_file("my_commands.txt")
my_script.save("my_array_job.sh")
```

Which saves this file:

```shell

#!/bin/sh

#$ -N my_array_job
#$ -l h_vmem=2G
#$ -l h_rt=06:00:00
#$ -o /exports/eddie/scratch/s1027820/
#$ -j y
#$ -t 1-6

. /etc/profiles.d/modules.sh
module load python

SEEDFILE="my_commands.txt"
SEED=$(awk "NR==$SGE_TASK_ID" "$SEEDFILE")
$SEED

```

This uses awk to run each line of code in `commands.txt` corresponding to each `$SGE_TASK_ID`, which in this case is 1 to 6.

------------

## Checking running jobs

We can also use scissorhands to parse `qacct` output into more sensible python structures.

This is mainly useful for checking memory useage, and if any tasks have failed.

A typical `qacct -j "my_job"` output for an array job looks like:

```
==============================================================
qname        eddie               
hostname     node2c02.ecdf.ed.ac.uk
department   defaultdepartment   
jobname      analysis_c92ea5     
jobnumber    9882080             
taskid       417                 
qsub_time    Thu Oct 26 18:13:35 2017
start_time   Fri Oct 27 13:06:18 2017
end_time     Fri Oct 27 16:55:57 2017
...
failed       0    
exit_status  0                   
ru_wallclock 13779        
cpu          13705.066    
mem          81258.707         
io           7.150             
iow          0.000             
maxvmem      11.965G
arid         undefined
==============================================================
qname        eddie               
hostname     node1f05.ecdf.ed.ac.uk
department   defaultdepartment   
jobname      analysis_c92ea5     
jobnumber    9882080             
taskid       362                 
account      sge                 
qsub_time    Thu Oct 26 18:13:35 2017
start_time   Fri Oct 27 09:14:28 2017
end_time     Fri Oct 27 16:57:52 2017
...
failed       0    
exit_status  0                   
ru_wallclock 27804        
cpu          24030.533    
mem          156907.828        
io           14.693            
iow          0.000             
maxvmem      11.527G

...

```


Which is human readable, but not very useful for larger jobs. From scissorhands we can import `check_output`.
Given a job name or ID number, this returns the qacct output in the form of a dictionary, with keys as task_IDs and a sub-dictionary of parameters and their values.

```python
from scissorhands.check_output import Qacct

job_accnt = Qacct("my_job")

print(job_accnt)
```

```python
 '98': {'account': 'sge',
        'cpu': '17176.678',
        'end_time': 'Fri Oct 27 01:17:00 2017',
        'exit_status': '0',
        'failed': '0',
        'hostname': 'node2b23.ecdf.ed.ac.uk',
        'io': '16.493',
        'iow': '0.000',
        'jobname': 'analysis_c92ea5',
        'jobnumber': '9882080',
        'maxvmem': '8.326G',
        ...
        'mem': '113002.519',
        'qname': 'eddie',
        'qsub_time': 'Thu Oct 26 18:13:35 2017',
        'ru_wallclock': '17170',
        'start_time': 'Thu Oct 26 20:30:50 2017',
        'taskid': '98'},
 '99': {'account': 'sge',
        'cpu': '19008.199',
        'end_time': 'Fri Oct 27 02:53:58 2017',
        'exit_status': '0',
        'failed': '0',
        'hostname': 'node2c09.ecdf.ed.ac.uk',
        'io': '17.989',
        'iow': '0.000',
        'jobname': 'analysis_c92ea5',
        'jobnumber': '9882080',
        'maxvmem': '8.469G',
        'mem': '129994.168',
        ...
        'qname': 'eddie',
        'qsub_time': 'Thu Oct 26 18:13:35 2017',
        'ru_wallclock': '21140',
        'start_time': 'Thu Oct 26 20:31:22 2017',
        'taskid': '99'}}
```

Which if you wanted could be transformed into a table with `pandas`.

```python
import pandas as pd

my_dict = job_accnt.qacct_dict
my_df = pd.DataFrame.from_dict(my_dict, orient="index")
```

```
   account       arid        cpu         department                  end_time ...
98     sge  undefined  17176.678  defaultdepartment  Fri Oct 27 01:17:00 2017 ...
99     sge  undefined  19008.199  defaultdepartment  Fri Oct 27 02:53:58 2017 ...
...
```