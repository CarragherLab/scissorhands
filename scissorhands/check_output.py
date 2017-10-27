"""
Parsing qacct output
"""

import subprocess


class Qacct(object):

    """
    Class docstring
    """

    def __init__(self, job_name):
        self.job_name = job_name
        self.qacct_str = self.get_account()
        self.qacct_list = self.parse_account_list()
        self.qacct_dict = self.parse_account_dict()

    def __repr__(self):
        return "qacct: {}".format(self.job_name)

    def __str__(self):
        return str(self.qacct_dict)

    def get_account(self):
        """
        Return output of `qacct -j $JOB_NAME`.

        Parameters:
        ----------
        job_name: string
            name of submitted analysis job

        Returns:
        --------
        Wall-of-text from qacct output
        """
        return subprocess.check_output(["qacct", "-j", self.job_name])

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
        output_dict = {}
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


