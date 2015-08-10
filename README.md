# Kaggle | 2015 ECML-PKDD
This repo contains the code I've implemented for the ECML-PKDD challenge, an extremely interesting and very challenging competition.
The work has been done for less than a week, in the meanwhile I was traveling among 3 different country and 2 continents (Barcelona/Spain, London/UK, Santiago/Chile) between August 2 and August 9 2015.


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

<!--  -->
### Parameters
Below the list of the parameters that can be set up when running the Framework. Some of them are extremely sensible and they might change significantly the quality of the final predictions.

<!--  -->
##### Parameters for tuning the framework
- `--max-airport-distance <float>` (MAX_AIRPORT_DIST) : **edge case threshold**, if the last available coordinate is closer than `MAX_AIRPORT_DIST` than the destination is set to be the airport —Porto's Airport Drop-off Area: ([41.237,-8.670](https://www.google.co.uk/maps/place/41%C2%B014'13.2%22N+8%C2%B040'12.0%22W/@41.237,-8.67,17z/data=!3m1!4b1!4m2!3m1!1s0x0:0x0)). Nb. This threshold is currently used also for the another _edge case_, the Porto Campanha Station (although I believe that these thresholds should be different).
- `--max-loop-distance <float>` (MAX_LOOP_DISTANCE) : **edge case threshold**, to face the cases in which the taxi driver *forget* to turn off the GPS signal after dropping off the passenger and it is driving back to the original position. This has been found to be quite common also by other participants (see [lebroschar](https://www.kaggle.com/c/pkdd-15-predict-taxi-service-trajectory-i/forums/t/15020/method-sharing) and [Rob0](https://www.kaggle.com/c/pkdd-15-predict-taxi-service-trajectory-i/forums/t/14994/how-to-get-top-10-with-a-non-ml-approach)'s approaches).
- `--last_cells <int>` (LAST_CELLS) : **edge case threshold**, this is an alternative approach quite time consuming that is currently used only for the cases in which there are not enough candidates ($<TOPN$). This threshold set the number of cells from which extract additional training routes.
- `--bbox-tolerance <float>` (BBOX_TOLERANCE) : **filtering offset**, this value extend the boundaries for the selection of training routes that will be compare with the test route.
- `--max-distance <float>` (MAX_DIST_TOLERATE) : **filtering threshold**, this threshold filter out the final candidates that have a location too far away from the last observation of the test trip.
- `--max-var <float>` (MAX_VARIANCE) : **matching threshold**, this is used in the `slopeDistanceSim` similarity approach, basically it is the maximum accepted error when measuring the distance of two trips.
- `--magnitude <int>` (MAGNITUDE) : **matching parameter**, number of last points to consider in order to compute the average distance between the test and the train trip.
- `--topn <int>` (TOPN) : **matching parameter**, number of top candidates to consider before applying the [MEDOID](https://en.wikipedia.org/wiki/Medoid) to select the final prediction.

Note that to choose the optimal values of the parameters describe before, multiple runs need to be tested. To make the multiple experiments quicker, all the parameters can read in input a list of possible values, such as: 
```
[..] --max-airport-distance 1.5,2,2.5 --magnitude 2,3 [..]
```
When a list is provided all the combinations among the values are tested. This trick allows to skip the initial (and time consuming) step of loading the training set—will be done only for the first setting.

<!--  -->
##### Input/Output Parameters:
- `--train <string>` : path of the train file (default: 'data/train.csv').
- `--test <string>` : path of the test file (default: 'data/test.csv').
- `--out <string>` : path of the output file respecting the format of the official submission ('TRIP_ID,LATITUDE,LONGITUDE'). Note that the file name will be modified adding the parameters that were used in the experiment. For example given a '--out data/test.pred.csv' the output file might be `test-pred.mt.mad2.0_mdt1.5_mld2.0_mv0.5_bbt0.05_lc0_topn4_m3.csv` in which the values of the parameters are stored.
- `--bbox <string>` : path of the bbox file, since this needs to be computed once, if the file is not present the bbox will be computed and store in `pickle format` (default: 'data/train.bbox.p').
- `--grid <string>` : path of the bbox file, same as the bbox, if the file is not found it is calculated otherwise it is loaded from the pickle file (default: 'data/train.grid.p'). 

<!--  -->
##### Extra Parameters:
- `-p` : run the Framework in parallel exploiting the 'joblib' and 'multiprocessing' packages. Note that the train, the bbox and the grid data are shared in memory, but then each tread needs to deal with the list of candidates that might be quite havy as well. 
- `--cpu <int>` : if the previous parameter is specified, this one set the number of CPU for the parallel computation. If this is unset by default the number of CPU is the total number of available CPUs minus 9 (to avoid memory issues).


<!--  -->
### Run Prediction within the Train Set
The framework embeds also a way to evaluate the results using only the training set, following the standard approach of splitting the data into training and testing set. However, since it is not known how the real test set has been created (how many GPS points are removed? how long are the trips? how many edge cases are included? etc.) the framework picks a random subset of the data and remove from each trip the last `N` GPS points, where `N` may vary between 30% and 10% of the total number of GPS points, and then it saves the destination as a ground truth. All the rest of the data (70%-90%) is considered as the final training set.

In order to evaluate the train set, the following parameter need to be specify when calling the framework:
- `-d` : specifies that the run mode is 'devel', splitting the data into training and testing set and increasing the information plotted in the standard output/error.
- `--split <float>` : defines the percentage of split for the training set. In general this value is aroung 75% (_i.e._, 75% of the routes will be part of the training set), however due to the huge amount of data, currently the test set is limited to a maximum of $500$ entries (to remove this limitation is extremely easy—just a couple of lines in the `runExperiment.py`).

###### Example of multiple execution
In order to execute everything on a single, and limited, machine such as a laptop, I recommend to take a sample of the train.csv. In the following example with 'train.1k.csv' I just toke the first $1000$ rows.

``` bash
python runExperiments.py --train data/train.1k.csv --bbox data/train.1k.bbox.p --out train.1k-pred.mt.csv --max-airport-distance 2 --max-distance 1.5 --max-loop-distance 2 --max-var .5 --bbox-tolerance 0.05 --last_cells 0 --topn 4 --magnitude 2,4,5 -p --cpu 5 -d --split 0.75
```

that will generate the following output files:
```
train.1k-pred.mt.mad2.0_mdt1.5_mld2.0_mv0.5_bbt0.05_lc0_topn4_m2.csv
train.1k-pred.mt.mad2.0_mdt1.5_mld2.0_mv0.5_bbt0.05_lc0_topn4_m4.csv
train.1k-pred.mt.mad2.0_mdt1.5_mld2.0_mv0.5_bbt0.05_lc0_topn4_m5.csv
```


### Run Test Set Prediction
To run the framework on the test set, the command is basically the same without the parameters `-d` and `--split`. 

###### Example of multiple execution

``` bash
python runExperiments.py --train data/train.csv --bbox data/train.bbox.p --out test-pred.mt.csv --max-airport-distance 2 --max-distance 1.5 --max-loop-distance 2 --max-var .5 --bbox-tolerance 0.05 --last_cells 0 --topn 4 --magnitude 2,4,5 -p --cpu 5
```

that will generate the following output files:
```
test-pred.mt.mad2.0_mdt1.5_mld2.0_mv0.5_bbt0.05_lc0_topn4_m2.csv
test-pred.mt.mad2.0_mdt1.5_mld2.0_mv0.5_bbt0.05_lc0_topn4_m4.csv
test-pred.mt.mad2.0_mdt1.5_mld2.0_mv0.5_bbt0.05_lc0_topn4_m5.csv
```


<!--  -->
## How did I Tackle the Problem 
I am going to explain in a simple manner how did I face the challenge. Apologize in advance if some of the steps are not well explained, without a whiteboard or a piece of paper this did not result to be an easy task. :)

### The Framework Explained in Few Words..
1. **Consider the edge cases**. First checking if the last point is close enough to the _Airport_ or to the _Campanha Station_ and in case set them as predicted destination. Second, checking if the driver forget to turn off the GPS and the taxi is going back to the startin point, and in case set the starting point as predicted destination.
2. **Select the candidate area/bbox**. The idea is to drastically reduce the number of train routes to consider for the comparison, by selecting only the route the end within the area in which the test route is going. To do so, I toke the last coordinates of the test route, I divide the map in four parts, I find which is the area where there are more GPS points and I select the opposite one as the more likely to contain the final destination. In order to consider the cases in which the taxi is perfectly driving toward one of the cardinal point (North, South, West, East), I enlarge the final area by the value specified with the parameter `--bbox-tolerance`. Selecting a large value significantly decrease the probability of missing the final destination but still reducing the number of training routes to consider.
3. **Get the subset of train routes**. Given the area (or bbox) I pick all the train routes that end in that area, and I start the comparison with the test route. 
4. **Compare the test route with all the train routes**. The idea here is to find a train route that is going in the same direction of the test one, but that is also getting spatially closer in time (_i.e._, the last points needs to be closer than the previous ones). So, given the test route and a train route, I do the following:
   1. First I need to find the point from which start the comparison. To do so I pick the first point of the test route and I find the closest one in the train route. Then I pick the second point of the test route and I find the closer one, then the third one, and so on. Finally I obtain a matched train route point for each of the test route point, with their distance (_e.g._, haversine)
   2. The previous step might be interrupted if some conditions are not satisfied. Given a mathing pair ($Pi \in TestRoute$ that matches with $Tj \in TrainRoute$) the following points of the test route (_e.g._, P_{i+1},P_{i+2},P_{i+3}..) need to be closer to points of the train route that are higher then the ones previously matched (_e.g._, T_{j+1} is fine, but T_{j-1} is not). If this doesn't happen it means that we are mathing the train route on the wrong direction. If this case happens more times then the train route is discarded. 
   3. Another condition that might interrupt the step (2), is when the distance is increasing in the meanwhile we are finding the pairs of points between the train and the test route. The idea is that the distance should decrease in time, however it might happen that the drivers are doing slightly different routes and in some points their distance increase even if the destination is the same. To avoid to lose this train route, we use the MAX_VAR threshold (passed with `--max-var`) to accept also the cases in which the distance might increase by no more than this threshold.

###### Why I didn't use a well known ML approach?



<!--  -->
## Next Delevopment
Below a list of developments/improvements that I had in mind but that I couldn't realize due to the limited time available (less than a week):

###### Higher Priority
- **Change the ranking function** : currently I am using the average distance of the last `m` common points between the test and the train trip. It has been showed to work nicely but there might be much better metric that can improve the final prediction.
- **Introduce a Machine Learning Approach** : I believe that the current framework is quite powerful (the best results are ranked #71 on the Private Leaderboard with less than a week of work), but it has some weakness points:
    - computational time: this might be a limitation especially when the parameters need to be tuned (although in the current challenge a validation set was not provided). The bottleneck was the huge amount of training data that is selected for the comparison, an issue that we tackled adding more filtering techniques that, however, might also remove some True Positive. 
    - the *direction* of the ...

###### Experimental
- **Applying alternative distance metric** : replacing _haversine distance_ with _google maps distance_. Since the latter one is significantly heavier computational speaking (it needs to perform a request through the google API) it can still replace the former one at least in the most sensible cases.

