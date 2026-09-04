from os.path import join, dirname, realpath
from setuptools import setup
import sys

assert sys.version_info.major == 3 and sys.version_info.minor >= 8, \
    "The Spinning Up repo is designed to work with Python 3.8 and greater." \
    + "Please install it before proceeding."

with open(join("spinup", "version.py")) as version_file:
    exec(version_file.read())

setup(
    name='spinup',
    py_modules=['spinup'],
    version=__version__,#'0.1',
    install_requires=[
        'cloudpickle',
        'gymnasium[classic-control,box2d]',
        'ipython',
        'joblib',
        'matplotlib',
        'mpi4py',
        'numpy',
        'pandas',
        'pytest',
        'psutil',
        'scipy',
        'seaborn',
        'torch>=2.0',
        'tqdm'
    ],
    extras_require={
        # The tf1 algorithm implementations (spinup/algos/tf1) are legacy
        # code kept for reference; they require TensorFlow 1.x, which has
        # no wheels for modern Python. All 6 algorithms are also available
        # under the pytorch backend, which is the default and does not
        # need this extra.
        'tf1': ['tensorflow>=1.8.0,<2.0'],
        # MuJoCo environments are optional; see the "Installing MuJoCo"
        # section of the docs.
        'mujoco': ['gymnasium[mujoco]'],
    },
    description="Teaching tools for introducing people to deep RL.",
    author="Joshua Achiam",
)
