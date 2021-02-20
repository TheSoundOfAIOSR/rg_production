# rg_production
Research Group - Production

# Usage
In order to run the App run the following commands:

    git clone https://github.com/TheSoundOfAIOSR/rg_production
    cd App
    python Gui.py

The application was developed with **Python 3.7**, in order to run it make sure to have all dependencies installed.

# Installation

## Simplified installation

To set up the conda venv run the following commands:

    conda env create -f environment.yml
    conda activate osr


## Manual installation
### Setting Up virtual environment

#### Python venv module
To create your python venv run:

    python -m venv osr
    source osr/bin/activate   (Unix)
    osr\Scripts\activate.bat  (Windows)

#### Conda env
To create your env run
   
    conda create -n osr python=3.7

## Install with pip
Install dependencies with pip directly on your venv

    pip install -r requirements.txt


