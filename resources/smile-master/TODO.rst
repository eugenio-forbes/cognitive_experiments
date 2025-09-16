================
Smile To Do List
================


Approximately in order of importance:

- (DONE) Subject processing (i.e., put the log files from a subj in
  their own directory.)

- (DONE) Logging
  - Each State is responsible for creating a dictionary to log the
    most important aspect of that state and write that to a YAML file
    for each experiment.
  - Create a Log state that can pick and choose from other state logs
    to make custom event logs.

- (DONE) Variables
  - For custom tracking of stuff throughout the experiment
    (e.g., counting up the num correct for a block)
  - Implemented as Set and Get states

- Keyboard input
  - (DONE) Add event hooks
  - (DONE) Tracking individual keys
  - Track extended text input

- Mouse input
  - (DONE) Button presses (what, when, and where [not yet where])
  - Movement (A list of dicts for each movement during an active
    state)

- (DONE) Conditional state to allow branching

- (DONE) Loop state (to allow looping without unraveling into a big sequence)

- (IN PROGRESS) Tests (especially to verify timing)

- (DONE) Plot the DAG with pydot

- Audio 
  - (DONE/In PROGRESS) Playback
  - Recording

- Movie playback 
  - (DONE) without audio 
  - sync with audio

- (DONE) EEG sync pulsing

- Animations (i.e., complex/dynamic visual stimuli)

- Better comments

- Docs (in code and with Sphinx)

- (In Progress) Example experiments

- (DONE) Upload to github

- Find good smile logo/icon



