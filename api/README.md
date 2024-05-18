# API

## Technology used
- FastAPI

## Available endpoints
- `matches`: Returns a count of frames within the match or match period, returned with the index number of the first frame of that period.
- `loose_block`: Returns a list of key frames for timeline navigation in the application. Currently the key frames are for build-up moments, but the 'loose block' is a reference to a previous idea iteration that was never updated.
- `frames`: Takes a start and end frame number and returns a list of frame data.

## Brief note on choices

The API largely developed as I realised (and developed) the needs of the front-end application. I chose FastAPI because I haven't used it before and was interested in using something new (having worked with Django Rest Framework in my day job).

I decided that it might not be ideal to send the full match's data to the front-end, so added the filter for the specific segment that can be played as an animation in the application. That does, however, mean that each time the user wants to change the viewing window, a new request is made for a selection of frames (which might overlap heavily with the previously requested selection).
 
The quality of the API engineering suffered a bit from the time taken up by the data processing and front-end development: the former gave less space for the rest of the project's needs, and the needs of the latter (being a near-completely new area for me) pushed the API into being a 'just good enough to service the whole' component.
