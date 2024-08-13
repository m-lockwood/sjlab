# Flexible Navigation Task

## Package contents

### MATLAB

#### Data wrangling 
For a specified Animal ID:
* Creates intermediate variables summarising trial- and session-level information.
* Plots an overvie of behaviour across trials within each session, including accuracy, bias and number of aborted trials.
* Plots an overview of performance over sessions, annotated by the availability of ephys data (if it exists).

#### exploratory analysis
* Plots spatial bias (tendency to choose port 0 versus port 1 dependent on dot location).

### Python
Pre-processing of ephys data, including:
* spike sorting (spikeinterface)
* Ephys data quality metrics (spikeinterface)
* Alignment of ephys and harp timestamps (harp, Open-Ephys)

### Installation

For easy installation, download the code using the link above or type the following into a terminal window:
```
git clone https://github.com/m-lockwood/sjlab.git
```
