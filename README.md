scissorhands
=============

A python module for generating Eddie3 (SunGridEngine) qsub scripts.

Installation
-------------

First download/clone the repo, and then in the top-level directory:

```bash
python setup.py install --user
```

Examples
--------

### Manually creating submission scripts

```python
from scissorhands.script_generator import AnalysisScript

my_script = AnalysisScript(name="example_job", memory="12G")

print(my_script)
```

The `user` argument is automatically detected if code is ran on the cluster.

```
#!/bin/bash

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

```
#!/bin/bash

#$ -N example_job
#$ -l h_vmem=2G
#$ -l h_rt=06:00:00
#$ -o /exports/eddie/scratch/s1027820/
#$ -j y

. /etc/profiles.d/modules.sh

module load R
Rscript my_R_code.R

```

```python
my_script.save("/home/user/save_location")
```

------------

### Submission script generator

To generate and save submission scripts in a loop *(though you should use an
array job for this sort of task)*:

```python
from scissorhands.script_generator import AnalysisScript

to_run = ["Rscript my_script_{}.R".format(i) for i in range(10)]

for index, code_snippet in enumerate(to_run):
    script = AnalysisScript(name="job_{}".format(index))
    script.template += code_snippet
    script.save("job_{}.sh".format(index))
```

--------

### Creating array jobs

If we have a text file of commands, with a command per line.

e.g `my_commands.txt`:

```
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
my_script.loop_through_file("my_commands.txt")
my_script.template += "module load python"
my_script.save("my_array_job.sh")
```

Which saves this file:

```bash

#!/bin/bash

#$ -N my_array_job
#$ -l h_vmem=2G
#$ -l h_rt=06:00:00
#$ -o /exports/eddie/scratch/s1027820/
#$ -j y
#$ -t 1-6

. /etc/profiles.d/modules.sh
module load python
SEEDFILE=my_commands.txt
SEED=$(awk "NR==$SGE_TASK_ID" "$SEEDFILE")
$SEED

```
