# SVR_Fantasy_Football_Predictions
NMSU REU PROJECT: Predict the fantasy scores for a given quarterback for each game in a season

This project is expanding on work provided by https://github.com/romanlutz/fantasy-football-prediction.

An API is used in this project to retrieve and read NFL Game Center JSON data.
This API can be found at https://github.com/BurntSushi/nflgame

Basic setup: This project uses python 2.7. Download and instructions for python can be found at https://www.python.org/ .

Installing dependencies:

$ sudo apt-get install pip
$ pip install --upgrade python
$ sudo pip install numpy
$ sudo pip install pybrain
$ sudo pip install scipy
$ sudo pip install sklearn
$ sudo pip install matplotlib
$ pip install nflgame
$ pip install jupyter

The following commands update the datasets used for machine learning from nflgame:
$ sudo nflgame-update-players
$ python get_data.py
$ python create_datasets.py

The following commands can be used to generate predictions for the data. Models is the SVM/Linear Regression Model:
$ python neural_net.py
$ python models.py
