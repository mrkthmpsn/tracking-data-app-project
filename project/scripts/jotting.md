# Steps
- Load raw data to db [X]
- Smooth data [X]
- Convert to normal coordinate system [X]
- Add metrics
  - Speed [X]
  - Team in possession [X]
  - Team of player record! [X]
  - Passing lane opportunities (or should this be added elsewhere?)
    - Pitch control vector [X]
    - Out of possession team block [X]
    - Out of possession team units
    - And passing lane opportunity can be signified by average value of X within Y area inside opp block, but only when ball is near a possession-team player [X]

## Further metric/analysis thoughts
- The passing opportunities need to be able to be tracked through space and time so that they can be marked as discrete 'opportunities' rather than a collection of grids
  - Associating the opportunity with the player (like, the player as a dict key) might be a way of doing this
- Can then count up opportunities and which were taken
  - If you were doing it sophisticatedly, you'd also want to account for the fact that if you have multiple options open at the same time, you can't take both of them
- Analysis of open passing entries achieved within the block, into the block from the back-line, from the wings into the block
- Compactness of the block can be measured, although I feel like that needs a more nuanced handling than the basic 'count the number' approach it usually gets
- Analysis of time spent out of possession when passing opportunities into the block _didn't_ arise

# Running line profile
TODO[***] Write-up the profiling process
`$env:PYTHONPATH="C:\Users\Mrkth\Documents\GitHub\stupidfunprobablyfail;$env:PYTHONPATH"` in terminal to set the Python interpreter
`kernprof -l -v project/scripts/data_science_processing.py` or similar