# 'Debug your build-up' project

## tl; dr
This is the Python repository for a prototype application to help analyse football situations using tracking data, which can be found here: https://react-test-ufcwqzajfa-uc.a.run.app 

This repo includes the processing of raw tracking data, and storage into a MongoDB database cluster; and the surfacing of the processed data in various API endpoints for the application front-end.

For a project write-up that covers the back-end and front-end, see `project_writeup.md`.

## Notable technologies
- **FastAPI** for API
- **MongoDB Atlas** & `pymongo` for database
- `mplsoccer` for visualisation during development 
- **ChatGPT 4** for a lot of coding & general development help
- `tqdm` as an indispensable 'progress bar during processing' sanity-maintenance tool

## Other documentation

Documentation for the data processing process can be found in the `data_processing/scripts/` folder, and documentation for the API can be found in the `api/` folder.

## Data

The data inside the `data/` folder is the `Sample_Game_3` data from [Metrica Sport's open sample data](https://github.com/metrica-sports/sample-data/tree/master).  

## Running

### Dependencies etc

Run `pip install -r requirements.txt` to install dependencies locally or in a virtual environment. You can run the Dockerfile, which is used in the actual deployment, if you want, but idk that seems excessive.

### Database set-up
Running the app on an external database isn't strictly necessary. If running locally, the processing in `data_processing/scripts/` could save to local files, which the API endpoints could also draw from.

If wanting to use the same MongoDB Atlas approach as the original, you will need to create an `.env` file and create a MongoDB Atlas cluster.

A free [MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-database) tier is (at time of writing, May 2024) is (more than) large enough to store the data produced by the processing steps from the following order:
- `data_loader.py`
- `data_processing.py`
- `data_post_processing.py`

As a NoSQL database, it's easy to get up and started with, without having to define (or, if you wanted to experiment with this code, change) schemas as in a SQL-based database.

After setting up your MongoDB Atlas cluster, you'll need to find the [connection string](https://www.mongodb.com/docs/manual/reference/connection-string/) and paste it in the `.env` file as the value for `MONGO_URI`. Set up a database called `metrica_tracking`, or choose a name of your own and make sure that you change the references in the code to database name. 

Splitting the different stages of data processing into different collections isn't strictly necessary, although separating the 'data loading' stage (processing the raw `.txt` file) is probably preferable to avoid having to redo it.

### API 

Add the localhost port that your front-end is running on to the `.env` file with the key `FE_URL`. From a terminal in the location of the project folder, run `uvicorn api.endpoints:app --reload` to run the API.

## General structural choices & comments

Both the `tests/` and `documentation/` folders represent processes that I wanted to follow but didn't stick with, though may return to to fill out. 

The `data_processing/visualisation/` folder is intended as a way of checking what the processed data looks like; the front-end application has a separate way of making pitch visualisations.

## Known (BE) issues

### Data processing
No currently known data processing issues.

### API

#### Minor
- Structure of returned data could be improved for future compatability/changes.
- `loose_blocks` endpoint name is based on an old idea of the key frames that would be used in the application.
- `frames` endpoint features a bit of a hack in order to fetch the right frames of data, based on a bit of a mismatch between types of frame identifier.

### Other utils

#### Minor
- The `plot_frame` visualisation function implicitly expects a pitch control field as part of the input data, without this being an optional parameter. It would need refactoring to be more flexible to account for a lack of pitch control field.

## TODO note

To help manage TODOs throughout the project, I use a three-star system, where *** is the most important category to address and * the least important.

---

## ChatGPT 4 aside

At the time of the project, the ChatGPT options were GPT3.5 on the free model and GPT4 for paid customers, which I used as part of the project. An observation I had (for all that a single anecdote is worth) is that the GPT4 model handled previous conversation history much better than previous models, although there seemed to be a point when the exchange had become _very_ lengthy where performance started deteriorating.

When using GPT3.5 in the past on a difficult problem, there have been times where its gone into a loop - suggesting code that I have then asked to be checked or tweaked, and its gone back to its last-but-one version of the code instead of making a true change. This could even happened if I explicitly asked it to start from scratch. 

The GPT4 version of ChatGPT that I used for this project didn't fall into this 'oblivious self-repetition' loop while I was using it. Now, this might be because the problems were easier to deal with, or because I was able to recognise signs that the loop _might_ happen and take a different tack to avoid it. However, I can sort of see how a change to its context mechanism/volume might improve a model in this respect, which is interesting. 

The GPT4 version of ChatGPT also seemed to be able to deal with talking about pitch control as a concept and the movement of players fairly well. Whether this is to do with more pitch control-related data in the model's training set or other improvements in the model's ability to predict relevant words and attentions between them, I'm not sure.