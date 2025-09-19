# cognitive_experiments
**Code for data collection in performance of cognitive tasks written for Texas Computational Memory Lab.**

## Overview:
This project provides Python-based tools for collecting cognitive task performance data, developed for use in electrophysiological studies of episodic memory. It is tailored for cognitive electrophysiologists working with deep brain stimulation research. This project integrates Blackrock Neurotech hardware through client-server communication and works seamlessly with the University of Pennsylvania's [Elemem](https://github.com/pennmem/elemem) software.


## Features:
- **Trial Randomization**: Ensures that the trial list of every experiment session is uniquely randomized to avoid confounds.
- **Checkpoint System**: Necessary interruptions for provision of patient care are a frequent obstacle in performing research in a hospital setting. Code provides the flexibility of exiting a session and resuming from last completed trial. 
- **Client-Server Communication**: Allows for integration with Blackrock Neurotech hardware and Elemem software.
- **Data Alignment**: Introduces client-server communication timing and new protocol for delivery of sync pulses to improve reliability, accuracy, and reliability of automated alignment of behavioral data to EEG data.


## Tech Stack:
- **Platform**: macOS (required for PennSyncBox compatibility).
- **Languages**: Python, and MATLAB (for Blackrock Neurotech API).
- **Key Package**: Experiments are coded using [SMILE](https://github.com/compmem/smile). Read [documentation](https://smile-docs.readthedocs.io/en/latest/) for more information.


## Installation:
1) Install [Anaconda](https://anaconda.org/).

2) Import Anaconda environment ("smile") from provided .yml file:
<pre>conda env create -f /path/to/cognitive_experiments/resources/smile-conda-environment.yml</pre>

3) Install Homebrew:
<pre>/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"</pre>

4) Use Homebrew to install libusb:
<pre>brew install libusb</pre>

5) Navigate to /cognitive_experiments/resources/smile-master/ and complete SMILE installation:
<pre>cd /cognitive_experiments/resources/smile-master/</pre>
<pre>python -m pip install .</pre>

6) Copy pennsyncbox source code file to your environment's site-packages:
<pre>cp /cognitive_experiments/resources/pennsyncbox/_pennsyncbox.cpython-36m-darwin.so /opt/anaconda3/envs/smile/lib/python3.6/site-packages/</pre>

7) Update default shell configuration. Edit .bashrc or .zshrc to include the following line:
<pre>export PYTHONPATH="/path/to/cognitive_experiments/resources/smile-master/:$PYTHONPATH"
</pre>


## Usage:
1) Navigate to desired experiment folder:
<pre>cd /cognitive_experiments/desired_experiment_folder/</pre>

2) Source your shell configuration if necessary:
<pre>source ~/.zshrc</pre>

3) Activate "smile" Anaconda environment:
<pre>conda activate smile</pre>

4) Launch experiment:
<pre>python3 desired_experiment.py</pre>


## Optional:
- Edit configurations in confuration.py to adjust experiment controls to keyboard/controller used.


## Future Improvements:
- Add logging for every response attempt.
- Expand and curate word pools and image sets.
- Currently "theta burst" stimulation is delivered using a for loop. Blackrock's Matlab API allows for programming of complex stimulation patterns without the need of a loop. Using this would enable early termination of trial once subject response is submitted.
