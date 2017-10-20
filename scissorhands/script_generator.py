"""
Automatically generate SGE submission scripts from a template.
"""

import textwrap
import random
import os


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

        if output is None:
            output = "/exports/eddie/scratch/{}/".format(self.user)
        self.output = output

        self.template = textwrap.dedent(
            """
            #!/bin/bash

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

    def __add__(self, command):
        return self.template + textwrap.dedent(command + "\n")

    def save(self, path):
        """save script/template to path"""
        with open(path, "w") as out_file:
            out_file.write(self.template + "\n")



class AnalysisScript(SGEScript):
    """
    Analysis script, inherits SGEScript class.

    Parameters:
    -----------
    array: Boolean

    tasks: string

    hold_jid: string

    hold_jid_ad: string

    pe: string


    Methods:
    --------
    """

    def __init__(self, array=False, tasks=None, hold_jid=False,
                 hold_jid_ad=False, pe=None, *args, **kwargs):
        SGEScript.__init__(self, *args, **kwargs)

        if array is True and tasks is not None:
            self.template += "#$ -t {}\n".format(tasks)
        if array is True and tasks is None:
            raise ValueError("No argument for tasks given, yet array is True")
        if array is False and tasks is not None:
            raise ValueError("tasks only work with array jobs")

        if hold_jid is not False and hold_jid_ad is not False:
            raise ValueError("Cannot use both 'hold_jid' and 'hold_jid_ad'")
        if hold_jid is not False:
            self.template += "#$ -hold_jid {}\n".format(hold_jid)
        if hold_jid_ad is not False:
            self.template += "#$ -hold_jid_ad {}\n".format(hold_jid_ad)

        if pe is not None:
            self.template += "#$ -pe {}\n".format(pe)

        self.template += "\n. /etc/profiles.d/modules.sh\n"



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
    result.insert(0, random.choice(tmp[1:]))
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
