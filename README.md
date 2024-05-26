DESCRIPTION:
Display statistics for selected stations and parameters for nve maalestasjoner graphically.
A parameter might be vannstand, vannføring, vanntemperatur.

DETAILS:
Populate database with stations and parameters.
This part will be in a cron job that updates the stations and parameter database daily.
The observations/timeseries will be pulled from the nve API for every request based on the stations and parameter selected in the frontend. The app supports different plots. Timeseries for a station and all of its parameters. Compare 2 station and 1 parameter. Create jointplot to see how two parameters relate to each other. Or matrix plot to see how all parameters for 1 station relate to each other.

OPERATIONS:
For development we are running a docker-compose container with both front and backend pointing to 
a local database. For production, running a cron job updating a redis or database with stations.
 There will be kubernetes services for frontend and backend connected to the station database. This setup is 
 minikube compliant.

TODO:
Implement asynchronous call. So far not much added value considering few users, but extensive db calls. 
Improve tests. 
Implement authorisation and authentication. 
Refactor frontend. 
Explore docker run with db docker-compose with redis/mem cach. 
Web hooks - could trigger update of database. 
New/deleted stations, probably not, possible collisions - Mixing responsibility. 
HTTPExceptions handling in frontend - so far they are bypassed. Explore similar setup as timeseries exceptions. 
Finalize pvc or similar for daily update. 
Sort list of stations.
