"""
Parsing qacct output
"""

import subprocess
from collections import OrderedDict


class Qacct(object):

    """
    Class docstring


    Parameters:
    -----------


    Attributes:
    -----------


    Methods:
    --------
    """

    def __init__(self, job_name=None, qacct_str=None):
        self.job_name = job_name
        # if given a qacct string, then use that as job info
        if qacct_str is None and job_name is not None:
            self.qacct_str = subprocess.check_output(["qacct", "-j", job_name])
        # if given a job name, then call qacct on that name to get the job info
        elif qacct_str is not None and job_name is None:
            self.qacct_str = qacct_str
        else:
            err_msg = "need an argument for either job_name or qacct_str"
            raise ValueError(err_msg)
        self.qacct_list = self.parse_account_list()
        self.qacct_dict = self.parse_account_dict()
        self.failed_tasks = self.find_failed()

    def __repr__(self):
        return "qacct: {}".format(self.job_name)

    def parse_account_list(self):
        """
        Parse wall-of-text from `get_account` into a nested list.

        Returns:
        ---------
        nested list
        """
        # is it always this size? does it depend on the terminal size?
        task_sep = "="*62 + "\n"
        split_by_task = self.qacct_str.split(task_sep)[1:]
        split_by_task = [task.split("\n") for task in split_by_task]
        tidy_list = []
        for task in split_by_task:
            task_list = []
            for line in task:
                # strip trailing whitespace
                line = line.strip()
                # replace multiple spaces with single space
                line = " ".join(line.split())
                task_list.append(line)
            tidy_list.append(task_list[:-1]) # last entry is just a space
        return tidy_list

    def parse_account_dict(self):
        """
        Parse wall-of-text from `get_account` into a nested list.

        Returns:
        --------
        Dictionary.
        {
            task_id: {
                param: str,
                param: str,
                param: str
            },
            task_id: {
                param: str,
                param: str,
                param: str
            }
        }

        """
        output_dict = OrderedDict()
        # parse self.qacct_list into a dictionary
        for task_params in self.qacct_list:
            for param in task_params:
                if param.startswith("taskid"):
                    task_id = param.split(" ")[1]
                    break
            task_dict = {}
            for param in task_params:
                param_split = param.split(" ")
                key = param_split[0]
                value = " ".join(param_split[1:])
                task_dict[key] = value
            output_dict[task_id] = task_dict
        return output_dict

    def find_failed(self):
        """
        Return list of failed task ids
        """
        failed_tasks = []
        for task_id, task_dict in self.qacct_dict.items():
            if task_dict["exit_status"] != "0":
                failed_tasks.append(int(task_id))
        failed_tasks.sort()
        return failed_tasks

    def get_failed_commands(self, commands_file):
        """
        Returns commands from failed tasks

        Parameters:
        ----------
        commands_files: string
            path to file containing commands, command per line

        Returns:
        --------
        list of commands that correspond to failed tasks
        """
        with open(commands_file, "r") as f:
            commands = [line.strip() for line in f.readlines()]
        # subtract 1 as $SGE_TASK_ID's are 1-indexed, whereas
        # python list is 0-indexed
        return [commands[i-1] for i in self.find_failed()]

    def make_failed_commands(self, commands_file, output_file):
        """
        Writes commands from failed tasks to a file

        Parameters:
        ----------
        commands_files: string
            path to file containing commands, command per line

        output_file: string
            location where to save the commands

        Returns:
        --------
        Nothing, writes file to disk
        """
        with open(output_file, "w") as f:
            for command in self.get_failed_commands(commands_file):
                f.write(command + "\n")

