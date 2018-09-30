# scissorhands

[![Build Status](https://travis-ci.org/CarragherLab/scissorhands.svg?branch=master)](https://travis-ci.org/CarragherLab/scissorhands)

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
import scissorhands as eddie

my_script = eddie.AnalysisScript(name="example_job", memory="12G")

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

my_script += to_run

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
from scissorhands import AnalysisScript

to_run = [f"Rscript my_script_{i}.R" for i in range(10)]

for index, code_snippet in enumerate(to_run):
    script = AnalysisScript(name=f"job_{index}")
    script += code_snippet
    script.save(f"job_{index}.sh")
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
from scissorhands import AnalysisScript

my_script = AnalysisScript(name="my_array_job")
my_script += "module load python"
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

`scissorhands` automatically detects the number of commands in `commands.txt`,
though this can be overridden by setting a `task` argument within
`AnalysisScript`.

------------
