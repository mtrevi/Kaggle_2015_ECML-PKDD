# Kaggle | 2015 ECML-PKDD
This repo contains the code I've implemented for the ECML-PKDD challenge, an extremely interesting and quite complicated competition.
The work has been done for less than a week, in the meanwhile I was traveling among 3 different country and 2 continents (Spain, UK, Chile) between August 2 and August 9 2015.


<!--  -->
## Taxi Service Trajectory
This Kaggle competition has been proposed for the ECML-PKDD (European Conference on Machine Learning and Principles and Practice of Knowledge Discovery in Databases) edition of 2015.

* Website: https://www.kaggle.com/c/pkdd-15-predict-taxi-service-trajectory-i
* No. Participant Teams: 381
* Official Time Range: 20 April - 1 July


<!--  -->
## Structure of the Framework
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


<!--  -->
## How to Run the Framework

### Parameters
Below the list of the parameters that can be set up when running the Framework. Some of them are extremely sensible, and they might change significantly the quality of the final predictions.

- `(mad) MAX_AIRPORT_DIST` : **edge case threshold**, if the last available coordinate is closer than `mad` than the destination is set to be the airport —Porto's Airport Drop-off Area: ([41.237,-8.670](https://www.google.co.uk/maps/place/41%C2%B014'13.2%22N+8%C2%B040'12.0%22W/@41.237,-8.67,17z/data=!3m1!4b1!4m2!3m1!1s0x0:0x0)). Nb. This threshold is currently used also for the another _edge case_, the Porto Campanha Station (although we believe that these thresholds should be different).
- `(mld) MAX_LOOP_DISTANCE` : **edge case threshold**, to face the cases in which the taxi driver *forget* to turn off the GPS signal after dropping off the passenger and it is driving back to the original position. This has been found to be quite common also by other participants (see [lebroschar](https://www.kaggle.com/c/pkdd-15-predict-taxi-service-trajectory-i/forums/t/15020/method-sharing) and [Rob0](https://www.kaggle.com/c/pkdd-15-predict-taxi-service-trajectory-i/forums/t/14994/how-to-get-top-10-with-a-non-ml-approach)'s approaches).
- `(mdt) MAX_DIST_TOLERATE` : **filtering threshold**, this threshold filter out the final candidates that have a location too far away from the last observation of the test trip.
- `(mv) MAX_VARIANCE` : **matching threshold**, this is used in the `slopeDistanceSim` similarity approach, basically it is the maximum accepted error when measuring the distance of two trips.
- `(m) MAGNITUDE` : **matching parameter**, number of last points to consider in order to compute the average distance between the test and the train trip.
- `(topn) TOPN` : **matching parameter**, number of top candidates to consider before applying the [MEDOID](https://en.wikipedia.org/wiki/Medoid) to select the final prediction.

### Run Prediction within the Train Set

### Run Test Set Prediction


<!--  -->
## How did we Tackle the Problem (The Framework Explained in Few Words..)


<!--  -->
## Next Delevopment
Below a list of development that we had in mind but that we couldn't realize due to the limit time available (less than one week):

###### Higher Priority
- **Change the ranking function** : currently we are using the average distance of the last `m` common points between the test and the train trip. It has been showed to work nicely but there might be much better metric that can improve the final prediction.

###### Experimental
- **Applying alternative distance metric** : replacing _haversine distance_ with _google maps distance_. Since the latter one is significantly heavier computational speaking (it needs to perform a request through the google API) it can still replace the former one at least in the most sensible cases.

