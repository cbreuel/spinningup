============
Installation
============


.. contents:: Table of Contents

Spinning Up requires Python3, OpenAI Gym, and OpenMPI. 

Spinning Up is currently only supported on Linux and OSX. It may be possible to install on Windows, though this hasn't been extensively tested. [#]_ 

.. admonition:: You Should Know

    Many examples and benchmarks in Spinning Up refer to RL environments that use the `MuJoCo`_ physics engine. MuJoCo is a proprietary software that requires a license, which is free to trial and free for students, but otherwise is not free. As a result, installing it is optional, but because of its importance to the research community---it is the de facto standard for benchmarking deep RL algorithms in continuous control---it is preferred. 

    Don't worry if you decide not to install MuJoCo, though. You can definitely get started in RL by running RL algorithms on the `Classic Control`_ and `Box2d`_ environments in Gym, which are totally free to use.

.. [#] It looks like at least one person has figured out `a workaround for running on Windows`_. If you try another way and succeed, please let us know how you did it!

.. _`Classic Control`: https://gym.openai.com/envs/#classic_control
.. _`Box2d`: https://gym.openai.com/envs/#box2d
.. _`MuJoCo`: http://www.mujoco.org/index.html
.. _`a workaround for running on Windows`: https://github.com/openai/spinningup/issues/23

Installing Python
=================

We recommend installing Python through `uv`_, a fast, modern package and environment manager for Python. uv replaces the need for Anaconda: it installs Python versions for you and manages isolated virtual environments without a separate conda toolchain.

Install uv itself with the official installer:

.. parsed-literal::

    curl -LsSf https://astral.sh/uv/install.sh | sh

Then create a Python 3.10 virtual environment for Spinning Up:

.. parsed-literal::

    uv venv --python 3.10 spinningup-env

To use Python from the environment you just created, activate it with:

.. parsed-literal::

    source spinningup-env/bin/activate

.. admonition:: You Should Know

    If you're new to python environments and package management, this stuff can quickly get confusing or overwhelming, and you'll probably hit some snags along the way. (Especially, you should expect problems like, "I just installed this thing, but it says it's not found when I try to use it!") You may want to read through some clean explanations about what package management is, why it's a good idea, and what commands you'll typically have to execute to correctly use it.

    The `uv documentation`_ is a good place to start, and covers environments, Python version management, and dependency installation in one place.

.. _`uv`: https://docs.astral.sh/uv/
.. _`uv documentation`: https://docs.astral.sh/uv/


Installing OpenMPI
==================

Ubuntu 
------

.. parsed-literal::

    sudo apt-get update && sudo apt-get install libopenmpi-dev


Mac OS X
--------
Installation of system packages on Mac requires Homebrew_. With Homebrew installed, run the follwing:

.. parsed-literal::

    brew install openmpi

.. _Homebrew: https://brew.sh

Installing Spinning Up
======================

.. parsed-literal::

    git clone https://github.com/openai/spinningup.git
    cd spinningup
    uv pip install -e .

.. admonition:: You Should Know

    Spinning Up defaults to installing everything in Gymnasium **except** the MuJoCo environments. In case you run into any trouble with the Gymnasium installation, check out the `Gymnasium`_ github page for help. If you want the MuJoCo environments, see the optional installation section below.

    All 6 core algorithms (VPG, TRPO, PPO, DDPG, TD3, SAC) are implemented in PyTorch, which is the default backend. Older TensorFlow 1.x implementations of 5 of the 6 algorithms still exist in the repo for reference, but TensorFlow is no longer installed by default — TF1 has no wheels for modern Python. If you need them, install the ``tf1`` extra (``uv pip install -e ".[tf1]"``) into a separate Python 3.7-or-earlier environment.

.. _`Gymnasium`: https://github.com/Farama-Foundation/Gymnasium

Check Your Install
==================

To see if you've successfully installed Spinning Up, try running PPO in the LunarLander-v3 environment with

.. parsed-literal::

    python -m spinup.run ppo --hid "[32,32]" --env LunarLander-v3 --exp_name installtest --gamma 0.999

This might run for around 10 minutes, and you can leave it going in the background while you continue reading through documentation. This won't train the agent to completion, but will run it for long enough that you can see *some* learning progress when the results come in.

After it finishes training, watch a video of the trained policy with

.. parsed-literal::

    python -m spinup.run test_policy data/installtest/installtest_s0

And plot the results with

.. parsed-literal::

    python -m spinup.run plot data/installtest/installtest_s0


Installing MuJoCo (Optional)
============================

MuJoCo used to be proprietary software requiring a paid (or free trial/student) license. In 2021, DeepMind acquired MuJoCo and open-sourced it, and it's now available as a regular pip package with no license step at all.

Install the ``mujoco`` extra, which pulls in both the ``mujoco`` physics engine and its Gymnasium environments:

.. parsed-literal::

    uv pip install -e ".[mujoco]"

.. admonition:: You Should Know

    The MuJoCo environments you'll see referenced elsewhere as ``HalfCheetah-v2``, ``Walker2d-v2``, etc. no longer work directly: those old IDs were built on the deprecated ``mujoco-py`` bindings and have been moved out to the separate `gymnasium-robotics`_ project. The versions built on the modern ``mujoco`` bindings are ``-v4`` and ``-v5`` (``-v5`` is current; ``-v4`` still works but is deprecated in favor of it). Use those instead, e.g. ``Walker2d-v5``.

And then check that things are working by running PPO in the Walker2d-v5 environment with

.. parsed-literal::

    python -m spinup.run ppo --hid "[32,32]" --env Walker2d-v5 --exp_name mujocotest

.. _`gymnasium-robotics`: https://github.com/Farama-Foundation/Gymnasium-Robotics
