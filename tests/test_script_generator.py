"""
module docstring
"""

from scissorhands import script_generator
import os

N_TASKS = 3
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
COMMANDS_LOC = os.path.join(THIS_DIR, "commands.txt")


def test_SGEScript():
    """test setting attributes"""
    my_script = script_generator.SGEScript(name="test_script", user="test_user")
    assert my_script.name == "test_script"
    assert my_script.memory == "2G"
    assert my_script.runtime == "06:00:00"
    assert my_script.user == "test_user"
    assert isinstance(my_script.template, str)
    repr_str = (
        "SGEScript: name=test_script, memory=2G, runtime=06:00:00, user=test_user"
    )
    assert my_script.__repr__() == repr_str
    assert my_script.template
    my_script.template += "#$ -another_option"
    assert my_script.template.split("\n")[-1] == "#$ -another_option"
    # test that the __iadd__ method works as expected
    my_script += "python example.py"
    assert my_script.template.split("\n")[-1] == "python example.py"


def test_SGEScript_mock_cluster():
    """Test auto-detecting user if we're on the cluster."""
    # set $KEYNAME environment var to the same as Eddie's
    os.environ["KEYNAME"] = "id_alcescluster"
    my_script = script_generator.SGEScript(name="mock_cluster")
    assert my_script.user == os.environ["USER"]
    user = os.environ["USER"]
    expected_output_location = "/exports/eddie/scratch/{}/".format(user)
    assert my_script.output == expected_output_location


def test_AnalysisScript_loop_through_file():
    """test creating array job script"""
    script_tasks = script_generator.AnalysisScript(user="user", tasks="1-100")
    script_tasks.loop_through_file(input_file="commands.txt")
    output = script_tasks.template.split("\n")
    assert output[-4] == 'SEEDFILE="commands.txt"'
    assert output[-3] == 'SEED=$(awk "NR==$SGE_TASK_ID" "$SEEDFILE")'
    assert output[-2] == "$SEED"
    assert "#$ -t 1-100" in output
    assert script_tasks.array is True


def test_AnalysisScript_set_tasks():
    """check different methods of adding tasks work"""
    task_int = script_generator.AnalysisScript(user="user", tasks=42)
    assert "#$ -t 1-42" in task_int.template
    task_list = script_generator.AnalysisScript(user="user", tasks=[12, 32])
    assert "#$ -t 12-32" in task_list.template
    # check that tasks are inferred is tasks are missing set
    # if the input_file is readable
    task_infer = script_generator.AnalysisScript(user="user")
    task_infer.loop_through_file(COMMANDS_LOC)
    assert task_infer.array is True
    assert task_infer.tasks == "#$ -t 1-{}".format(N_TASKS)


def test_StagingScript():
    """docstring"""
    script = script_generator.StagingScript(user="user")
    assert "\n#$ -q staging\n" in script.template
    assert script.memory == "500M"


def test_DestagingScript():
    """docstring"""
    script = script_generator.DestagingScript(user="user")
    assert script.memory == "500M"
