# rg_production
Research Group - Production

# Usage
In order to run the App simply run:

    python main.py

The application was developed with **Python 3.7/8**, but should work with other 3.x versions of Python.

# Installation

## CSound Installation

The sampler runs using the CSound library which needs to be installed here:

    https://csound.com/download.html
    
Note: Do not install python 2.x bindings. This will cause a crash when calling librosa/numba. https://github.com/numba/numba/issues/6862


## Simplified Python installation

To set up the conda venv run the following commands:

    conda env create -f environment.yml
    conda activate osr
    garden install knob


## Manual Python installation
### Setting Up virtual environment

#### Python venv module
To create your python venv run:

    python -m venv venv
    source venv/bin/activate   (Unix)
    venv\Scripts\activate.bat  (Windows)

#### Conda env
To create your env run
   
    conda create -n venv python=3.7

## Install with pip
Install dependencies with pip directly on your venv

    pip install -r requirements.txt
    garden install knob


