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

```
TODO
```