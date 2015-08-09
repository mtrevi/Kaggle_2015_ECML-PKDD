# Kaggle | 2015 ECML-PKDD
This repo contains the code I've implemented for the ECML-PKDD challenge, an extremely interesting and quite complicated competition.
The work has been done for less than a week, between August 2 and August 9 2015.


## Taxi Service Trajectory
This Kaggle competition has been proposed for the ECML-PKDD (European Conference on Machine Learning and Principles and Practice of Knowledge Discovery in Databases) edition of 2015.

* Website: https://www.kaggle.com/c/pkdd-15-predict-taxi-service-trajectory-i
* No. Participant Teams: 381
* Official Time Range: 20 April - 1 July


## Structure of the code
Below a brief description of each module of the framework:

- `runExperiments.py` : main file that takes care of running the entire framework.
- `src/objects` : contains the object classes used in the framework.
    - `CandidateObj.py` : the candidate class with the predicted destination that is returned within the framework.
    - `GPSPoint.py` : the object that contains the coordinates and additional customizable related functions.
    - `TripObj.py` : the object that contains all the information of an individual trip.
- `src/bbox` : contains the object classes that deals with (sub-)spacial geographical areas.
    - `BBoxObj.py` : takes care of collecting the train routes coordinates to make them quickly accessible when looking for destination within a specific bounding box (defined by a given latitude and longitude pair) — the main function of this class is to reduce the number of possible candidates (and therefore further comparisons) picked from the training set.
    - `GridObj.py` : takes care of splitting the training coordinates into a grid with different cells of about ~$1km^2$.
- `src/matching` : 
    - `DistanceMetrics.py` : contains a collection of metrics to compute the distance between given points.
    - `TripSimilarity.py` : contains a collection of similarity approaches with the aim to measure the similarity between two given trips.


## How to run

### Run Prediction within the Train Set

### Run Test Set Prediction

### Parameters


## Code Structure

## Next Delevopment


