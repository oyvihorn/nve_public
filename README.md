DESCRIPTION:
Display timeseries for selected stations and parameters for nve maalestasjoner graphically.

DETAILS:
Populate database with stations and parameters
This part will be in a cron job that updates stations and parameter db daily.
Not to be run for every app instance. Only observations needs to be pulled from api every time.
Stations and parameters are fetched from db for every select in front end pull down menus as it
needs to filter parameters based on stations selected and vice versa.

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
