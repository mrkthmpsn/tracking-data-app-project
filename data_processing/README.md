# Data processing

## Summary

The data processing is split into a series of processing 'scripts', which can be thought of as stages in a factory line.  
- `data_loader.py` converts the raw tracking data into a basic list of dicts/JSON objects (in the code as is, they're dictionaries that get inserted into a MongoDB Atlas collection where they implicitly become a JSON).
- `data_processing.py` adds a series of basic features (as described in the file's docstring), to the data produced in `data_loader.py`, including some features drawing on the event data.
- `data_post_processing.py` adds series that are slightly more advanced and/or 'opinionated' (as described in the file's docstring), like defensive block boundaries.
- `pitch_control_processing.py` features code to add pitch control model data, but was not eventually included in the end project (see 'Pitch Control' section below)
- `test_arena.py` is simply an area to use visualisation utils to see how the data looks. It was primarily used during development of `pitch_control_processing.py` and `data_post_processing`.

## Database connection

Each of the 'data processing scripts' files begins by fetching the data from a MongoDB database collection and ends by uploading it to a new collection (after having deleted what was already in that collection for storage purposes). 

The collections are named in the files. If you want to change the collection or database names, or use a different data storage method entirely (e.g. local files), make sure to make the necessary changes to these files. 

## Detail

### Processing choices overview
I decided to process every fifth frame at first, turning the 25fps data into 5fps. This seemed both a convenient division and still unlikely to miss important information between frames. I later changed this to every twelfth frame - essentially 2fps - when I was struggling with storage space in the free MongoDB tier while trying to maintain four different steps of saved data (raw, initial process, pitch control, and extra post-processing).

The division between 'processing' and 'post-processing' was partly just a way of splitting the task up, but also, in hindsight, seems sensible. The 'processing' features are all subjective in the sense that their importance - whether to process them at all - was a choice taken, but their definitions are very basic. In hindsight, I should have better processed data around team direction. 'Post processing' features involve much more subjective or domain-specific decision-making. 

The four features processed in `data_post_processing.py` are:
- 'Passing opportunity', or whether a player was 'on the ball' in that frame (the idea being that the amount of space a player is in doesn't matter much when the ball is in mid-flight with no-one in control of it)
- Defensive block boundaries - the edges of the out-of-possession team's 'block'
- Whether attacking players are inside this defensive block
- The distance to the closest opponent of each player (arguably a feature that could belong in the `data_processing.py` file).
Some of the decisions around these definitions are discussed in `project_writeup.md`.

The split between the steps _was_ very useful in practice. As well as saving time, it helped to stay more organised. 

### Pitch Control
An initial idea for a metric was to flag moments when a team reached a threshold of [pitch control](https://www.getgoalsideanalytics.com/everything-you-need-to-know-about-pitch-control/) within the opponent's defensive shape. The idea was that this would represent a great passing opportunity - useful to know for both attacking and defending teams - which would also give interesting information whether the team made it or not.

I wanted to try and create a pitch control model from scratch based on my understanding of the theory and work I'd previously read, and using ChatGPT as a tool. This probably wasn't the wisest choice, but it was interesting, at least.

However, the processing required in the approach I took (or the way I coded it) took far too much time to be worth it. It also added extra time to the tool itself on the front-end, because I ended up sending the pitch control field information in a compressed format on the API, which then needed decompressing by the FE.

I'm not unaware that there'll be better ways of doing this, but the use of pitch control wasn't a central part of the project, so I decided to avoid the further R&D time and remove it from the processing pipeline and end application.