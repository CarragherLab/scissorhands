"""
Scissorhands: Generate Eddie3 submission scripts from python.

A python module for generating Eddie3 (SunGridEngine) qsub scripts.
"""

from scissorhands import script_generator
from scissorhands.script_generator import *

__version__ = "0.3.0"
__all__ = [
    "SGEScript",
    "AnalysisScript", 
    "StagingScript",
    "DestagingScript",
    "SubmissionError",
    "ScriptError",
]
