# FantasyFootballPrediction

We are investigating methods for improving fantasy football prediction models.

This project is expanding on work provided by https://github.com/romanlutz/fantasy-football-prediction.

An API is used in this project to retrieve and read NFL Game Center JSON data.<br/> 
This API can be found at https://github.com/BurntSushi/nflgame


**Basic setup:**
This project uses python 2.7. Download and instructions for python can be found at https://www.python.org/ .

Installing dependencies:<br/>
$ sudo apt-get install pip<br/>
$ pip install --upgrade python<br/>
$ sudo pip install numpy<br/>
$ sudo pip install pybrain<br/>
$ sudo pip install scipy<br/>
$ sudo pip install sklearn<br/>
$ sudo pip install matplotlib<br/>
$ pip install nflgame<br/>
$ pip install jupyter<br/>

**The following commands update the datasets used for machine learning from nflgame:<br/>**
$ sudo nflgame-update-players<br/>
$ python get_data.py<br/>
$ python create_datasets.py<br/>

**The following commands can be used to generate predictions for the data. Models is the SVM/Linear Regression Model:<br/>**
$ python neural_net.py<br/>
$ python models.py<br/>
  
  
