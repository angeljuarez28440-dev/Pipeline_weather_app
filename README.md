# Pipeline_weather_app
Used to build understanding on pipelines.
Indigetion:
As of right now, my understanding is this: the codebase will build a connection to the desired API and will set limits for the codebase, or script, to wait 10 seconds per request and make only three attempts. It has limited attempts to access information from the API and a limited time for each request, along with a location of data/raw/. Using preset parameters from the API, I will call those parameters by using the latitude and longitude of each city, thus asking for parameters based on the cities’ coordinates. Then the codebase will request said parameters and will run through a try block. This block will try three times before raising an error. A logging method will make sure to record all errors, attempts of the request, and outcomes. Finally, it stores all information in a JSON file in the desired preset location. In addition each run will save one file per city ,per run.

Local set up Kafka :
To begin with, a file named docker-compose.yml will contain the information on what service will be pulled by later actions. In this case, it will be Kafka. Docker will pull/download an image of the Kafka service, which will then be used to starts a container and for further use. Then a topic named weather-raw will be made by the user that aligns with the newly developed Kafka service. This topic will be intentionally located in the running container.Some commands to help setup: 
# Start Kafka
docker compose up -d

# Create the topic (once)
docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --topic weather-raw --bootstrap-server localhost:9092

# List topics to confirm it exists (should print: weather-raw)
docker exec kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

To stop Kafka, run `docker compose stop`. Running `docker compose down` removes the container, and the topic along with it, so it has to be created again the next time.