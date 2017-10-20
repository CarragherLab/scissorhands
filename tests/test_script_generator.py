"""
module docstring
"""

from cptools2 import script_generator
import os

def test_SGEScript():
    """docstring"""
    my_script = script_generator.SGEScript(name="test_script", user="test_user")
    assert my_script.name == "test_script"
    assert my_script.memory == "2G"
    assert my_script.runtime == "06:00:00"
    assert my_script.user == "test_user"
    assert isinstance(my_script.template, str)
    repr_str = "SGEScript: name=test_script, memory=2G, runtime=06:00:00, user=test_user" 
    assert my_script.__repr__() == repr_str
    assert my_script.template
    my_script.template += "#$ -another_option"
    assert my_script.template.split("\n")[-2] == "#$ -another_option"


def test_SGEScript_mock_cluster():
    """
    Test auto-detecting user if we're on the cluster.
    """
    # set $KEYNAME environment var to the same as Eddie's
    os.environ["KEYNAME"] = "id_alcescluster"
    my_script = script_generator.SGEScript(name="mock_cluster")
    assert my_script.user == os.environ["USER"]
    assert my_script.output == "/exports/eddie/scratch/{}/".format(os.environ["USER"])


def test_AnalysisScript():
    """docstring"""
    pass


def test_StagingScript():
    """docstring"""
    pass


def test_DestagingScript():
    """docstring"""
    pass
