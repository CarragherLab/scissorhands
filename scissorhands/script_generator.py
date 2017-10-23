"""
Automatically generate SGE submission scripts from a template.
"""

import os
import random
import subprocess
import textwrap

class SGEScript(object):
    """
    Base class for SGE submission scripts.
    Just the bare basics for an SGE submission without any actual code.

    Parameters:
    -----------
    name: string (default = randomly generated hex code)
        Name of the job.

    user: string (default = $USER from environment)
        Username on the cluster. This will be automatically detected if
        ran on the cluster. If ran locally then this will need to be supplied.

    memory: string (default = "2G")
        Memory allocation for the job, has to be a valid parameter for
        `-l h_vmem`.

    runtime: string (default = "06:00:00")
        Run time limit for the job, has to be a valid parameter for `-l h_rt`.

    output: string (default = /exports/eddie/scratch/$USER/)
        output location for stdout and stderr files, defaults to user's
        scratch space. This is just for the job output, i.e jobname.o1234568


    Methods:
    --------

    save:
        arguments = path: string
        Save script to location specified in `path`
    """

    def __init__(self, name=None, user=None, memory="2G", runtime="06:00:00",
                 output=None):
        name = generate_random_hex() if name is None else name
        self.name = name
        self.user = get_user(user)
        self.memory = memory
        self.runtime = runtime
        self.save_path = None

        if output is None:
            output = "/exports/eddie/scratch/{}/".format(self.user)
        self.output = output

        self.template = textwrap.dedent(
            """
            #!/bin/sh

            #$ -N {name}
            #$ -l h_vmem={memory}
            #$ -l h_rt={runtime}
            #$ -o {output}
            #$ -j y
            """.format(name=name, memory=memory, runtime=runtime, output=output))

    def __str__(self):
        return str(self.template)

    def __repr__(self):
        return "SGEScript: name={}, memory={}, runtime={}, user={}".format(
            self.name, self.memory, self.runtime, self.user)

    def save(self, path):
        """save script/template to path"""
        with open(path, "w") as out_file:
            out_file.write(self.template + "\n")
        self.save_path = path

    def submit(self):
        """submit script to the job queue (if on a login node)"""
        if on_login_node():
            if self.save_path is None:
                raise ValueError("Need to save script before submitting")
            subprocess.Popen(["qsub", os.path.abspath(self.save_path)])
        else:
            raise RuntimeError("Cannot submit job, not on a login node.")

    def run(self):
        """alias for submit()"""
        self.submit()


class AnalysisScript(SGEScript):
    """
    Analysis script, inherits SGEScript class.

    Parameters:
    -----------
    array: Boolean

    tasks: string, int or list of 2 ints

    hold_jid: string

    hold_jid_ad: string

    pe: string


    Methods:
    --------

    loop_through_file:
        Adds text to template to loop through `input_file`, running a
        task for each line of `input_file` as an array job.

        Parameters:
        ------------
        intput_file: string
            path to file containing commands

        Returns:
        --------
        Nothing, adds text to template script in place.
    """

    def __init__(self, tasks=None, hold_jid=False,
                 hold_jid_ad=False, pe=None, *args, **kwargs):
        SGEScript.__init__(self, *args, **kwargs)

        if tasks is not None:
            # if tasks is a list of two numbers, then we can take that as
            # [start, end] and parse that into a string "start-end"
            if isinstance(tasks, list) and all(isinstance(i, int) for i in tasks):
                if len(tasks) == 2:
                    tasks = "{}-{}".format(*tasks)
                else:
                    msg = "'tasks' has to be either a list of length 2 or a str"
                    raise ValueError(msg)
            # if tasks is a single integer then we can take that as 1-tasks
            if isinstance(tasks, int):
                tasks = "1-{}".format(tasks)
            self.array = True
            self.tasks = tasks
            self.template += "#$ -t {}\n".format(tasks)
        else:
            self.array = False


        if hold_jid is not False and hold_jid_ad is not False:
            raise ValueError("Cannot use both 'hold_jid' and 'hold_jid_ad'")
        if hold_jid is not False:
            self.template += "#$ -hold_jid {}\n".format(hold_jid)
        if hold_jid_ad is not False:
            self.template += "#$ -hold_jid_ad {}\n".format(hold_jid_ad)

        if pe is not None:
            self.template += "#$ -pe {}\n".format(pe)

        self.template += "\n. /etc/profile.d/modules.sh\n"


    def loop_through_file(self, input_file):
        """
        Add text to script template to loop through a file containing a
        command to be run on each line.

        This using an array job this will setup an awk command to run each
        line according to the SGE_TASK_ID

        Parameters:
        -----------
        input_file: path to a file
            This file should contain multiple lines of commands.
            Each line will be run separately in an array  job.

        Returns:
        --------
        Nothing, adds text to template script in place.
        """
        if self.array is False:
            raise AttributeError("Cannot use method `loop_through_files` "
                                 "without settings `tasks` argument")
        # one way of getting the line from `input_file` to match $SGE_TASK_ID
        text = """
               SEEDFILE="{input_file}"
               SEED=$(awk "NR==$SGE_TASK_ID" "$SEEDFILE")
               $SEED
               """.format(input_file=input_file)
        self.template += textwrap.dedent(text)




class StagingScript(SGEScript):
    """
    Staging script, inherits SGEScript class.

    Parameters:
    -----------

    Methods:
    --------
    """

    def __init__(self, *args, **kwargs):
        SGEScript.__init__(self, *args, **kwargs)
        self.template += "#$ -q staging\n"



class DestagingScript(SGEScript):
    """
    Destaging script, inherits SGEScript class.

    Parameters:
    -----------

    Methods:
    --------
    """

    def __init__(self, *args, **kwargs):
        SGEScript.__init__(self, *args, **kwargs)


def generate_random_hex():
    """
    Generate a random hex number.
    Lifted from stackoverflow
    """
    tmp = "0123456789abcdef"
    result = [random.choice('abcdef')] + [random.choice(tmp) for _ in range(4)]
    random.shuffle(result)
    result.insert(0, random.choice(tmp[10:]))
    return "".join(result)


def get_user(user):
    """
    - Return username. If passed a username then will simply return that.
    - If not given a user an an argument, then this will try and determine
      username from the environment variables (if running on the cluster).
    - Will raise a ValueError if not passed a user and not running on the
      cluster.
    """
    if user is not None:
        return user
    elif on_the_cluster():
        return os.environ["USER"]
    else:
        raise ValueError("No argument given for 'user' and not running on "
            "the cluster, therefore unable to automatically detect the username")


def on_the_cluster():
    """
    Determine if script is currently running on the cluster or not.

    NOTE: Currently this works by looking for environment variables.
    The only one I could find that was the same regardless of login, staging
    or compute nodes was $KEYNAME. Might be a better way of checking this as
    there is no guarantee that this will stay the same
        (I have no idea what $KEYNAME actually is/does).

    Returns: Boolean
    """
    try:
        keyname = os.environ["KEYNAME"]
    except KeyError:
        return False
    return keyname == "id_alcescluster"


def on_login_node():
    """
    Determine if we are on a login node, i.e not a compute or staging node, and
    capable of submitting jobs.

    Done my checking for $SGE_ROOT in the environment variables, this is not
    present on the compute nodes.
    """
    if on_the_cluster():
        return "SGE_ROOT" in os.environ
    else:
        return False
