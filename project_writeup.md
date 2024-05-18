# Project write-up

For people who wanted a project write-up

_May 2024_

General outline:
- Project origins
- Processing choices
- Metric choices
- FE design choices
- Anticipated differences for a 'live product' 

### Project origins

Data insight accessibility* has been a theme through a lot of my work (e.g. [this previous project](https://mrkthmpsn.github.io/create-own-metric)), and it subconsciously influenced this one. 

*_see note at end of page._

The idea for the project actually came from a slow evolution of a thought I've had while watching Formula One: whenever a driver hits a bump or feels like something isn't right with their tyres, their race engineer says "ok, we'll look at the data". 

Originally, I phrased this as being like a 'debugging' application for a football team's play, but 'pitwall' (as a nod to the F1 influence) or 'in-game telemetry tool' is probably a better phrasing for it.

To keep the project manageable, I decided to focus on an area of build-up. This was because it's quite repeatable, an area where tracking data will clearly be useful, and, to be frank, a hype-y area of the game that would catch peoples' attentions. 

The key frames are based on 'passing opportunity' moments (described below), between 50-80 metres from opponent's goal and further from goal than the defending team's defensive block, with the phase of play more than 3.5 seconds old. This was arrived at through a mixture of intuition and testing the application. 

### Processing choices

I knew that there were a couple of options for tracking data online, the ones I've worked with previously being [Metrica Sport's](https://github.com/metrica-sports/sample-data) and [Skillcorner's](https://github.com/mrkthmpsn/SkillcornerOpenDataProject). The Metrica data is full-pitch whereas the Skillcorner data was broadcast tracking-based, so Metrica it was. I'm also intrigued by the FIFA standard format which Metrica's third game uses.

Most of the data processing choices in the `data_processing.py` file are quite standard, but the ones in `data_post_processing.py` might be worth talking about.

#### 'Passing opportunity'
Each frame is marked with a 'passing opportunity', a simplified marker of the ball being within a player's reach for a period of time. The ball has to be within two metres for a duration of a second, and if it is then all frames within that period will be marked (i.e. not just the ones after the second threshold has passed). 

This has some clear flaws. The largest is probably that it doesn't account for first-time passes. However, this marker is a foundation for other metrics, and I decided that it was more important to avoid false positives than it was to avoid false negatives.

#### Defensive block

The defensive block is defined as the midpoint between the two furthest outfielders on each side of the rectangle. 

I've long had misgivings about defining a block based on the furthest points of a team, so wanted to try something different here. In practice, everything probably averages out fine if using the furthest points of a team's outfielders, but in individual moments I feel that pressing players enlarge these 'blocks' in ways that don't feel like they fit the concept.

To be a bit theoretical, I think that you could say pressing players sometimes 'detach' themselves from their team's block in order to go and press. While that could be worth measuring in its own right, I think it makes it clear that a team's 'block' is a concept that shouldn't simply be defined as the furthest point of all outfielders.

The midpoint of the furthest two points in each direction (up, down, left, right) isn't a _dramatic_ change in definition, but I think it is close enough to the concept I'm after and simple enough to implement and explain.

### Metric choices

The metrics displayed on the app are:
- Closest opponent to ball
- Defensive block width
- Defensive block height
- Most space in-block attacker
- 2nd most space in-block attacker
- Near-side block-to-sideline gap
- Far-side block-to-sideline gap

Like most of the features, these were arrived at through a mix of intuition and testing. The arrangement represents a series of plausible checks a coach may want to do:
- Did the player have time on the ball? (if not, analysis on what was happening around the defensive block probably isn't relevant)
- Was there space within the out-of-possession team's defensive structure?
- Was there usable space around the outside of the defensive shape?

The figures change colour when certain thresholds are met. For the defensive block size, these are loosely based on [figures from FIFA about mid-blocks during the men's 2022 World Cup](https://www.fifatrainingcentre.com/en/fwc2022/technical-and-tactical-analysis/controlling-the-game-without-the-ball--the-mid-block-and-compactness.php), but altered by eye due to different approaches to defining a the block.

I initially thought about making the 'alerts' highlight in colours associated with 'good/bad', but decided to steer away from that for three reasons. One, the least important, was a sense of brand cohesiveness. More important was so that it's easier to imagine the app being used from both the defensive and attacking points of view (good from an attacking point of view will be bad from the defensive). 

Lastly, it became clear (or clear-_er_) to me during the project that the point of the app should be to make it easy for a coach to access information, but that theirs is the analysis to apply to it. Using a good/bad highlighting style for metrics implied a stronger 'opinion' of the application, which I don't think should be the aim.

### Front-end design choices

The essence of the design never changed from the original: a pitch for the tracking data animation with a timeline-type navigation feature and room for metrics (assuming a desktop/tablet screen size and shape).

Unlike the original inspiration, Formula One, football is very spatial, and the imagined users - coaches - less familiar with data, so the space prioritised was for the pitch animation. The navigation and stats would be to help highlight moments rather than the stats being the primary point of analysis.

However, I found that a line chart visualisation for defensive block area was a valuable addition when I tried it out. As a basic metric for 'valuable space available', it helped to give context to a sequence of play before even watching it.

The defensive block width and height area stats are also highlighted on the _area_ figure, rather than their own width/height figures. The theory is that the area is the key metric, rather than height or weight on their own, but that the area figure isn't easy to interpret. 

Inter-player distance and block-width statistics have been used more and more in recent years, so I think coaches would be far more familiar with figures in the range of 30-40m than a defensive block area figure in the region of 800-1000m squared.

### Anticipated differences for a true 'live product'

#### Engineering and data processing

An obvious one: the processing would need to be done live, which would affect various parts of the set-up. For a start, the data would be accessed from an external API of some sort rather than static files. 

The processing itself may need to be optimised further. This was on my mind while developing, but I didn't attempt to replicate a 'live processing' situation with it.

#### Interface design

In my opinion, the main area of the application that would change would be the navigation. 

For one, during a live match it might be desirable to have easy navigation for the past ~5 minutes specifically, updating live in real-time. 

The interface of clicking (or tapping) on key frame points could also be made easier - especially during a live match where mis-clicking could lose important seconds under pressure and be frustrating for everyone involved. 

One way of improving this could be for the 'match timeline' to be filterable by multiples of ten minutes or something. Perhaps the 'frames' timeline could be moved to beneath the pitch animation, with the double-decker timeline at the top of the screen being the whole match/half with a sliding ten-minute window to offer the key frames to select. 

#### Application responsive layout

I don't have a lot of front-end development experience so while the application is hopefully broadly suitable for tablet and computer landscape screens, there are probably screen size-related issues. 

#### User preferences

In a perfect world, this type of 'pitwall' would be available across all phases of the game. The main changes that this would cause, for _this_ design of application, would be in key frames and statistics. 

I think that key frames for different phases could be defined by the application developers, as it's probably a task that requires familiarity with data. However, it could also be user-defined. 

The user-defined path could also line up nicely with the game models of coaching teams, and their own internal definitions. For example, if a coach or coaching staff believes that the division between the initial and second (and even third) phases of set-pieces is crucially important, these could be constructed as different 'phases' with their own key frames and statistics. If this user definition was going to be a feature, then the metric-creation flow would also need to be well-designed.

As well as the key frames, the statistics and 'alert thresholds' could also be user-defined. Despite my initial expectation, I like the permanent presence of a line chart for a specific metric, but my initial idea was that line charts would be available by hovering over the statistics in the left-hand panel. Something similar could possibly be implemented in a full version (maybe a changeable selection of pinned charts).

##### 'Data insight accessibility' and metric creation addendum

I used the phrase 'data insight accessibility' rather than 'data accessibility' deliberately, although partly just to try it out. 

I think that a push for 'data accessibility' sometimes just means putting numbers in front of people that they don't necessarily understand. It might be a case of [Goodhart's law](https://en.wikipedia.org/wiki/Goodhart%27s_law) - making data available for people became a signal of forward-thinking organisations, but when putting data in front of people became the goal it stops being a good marker.

I do strongly believe that people being more data, or numerically, literate is a good thing. However, I think that takes time - time which people don't always have available in order to progress quickly - and there's no good reason why gaining insights from data needs to rely on high levels of domain-specific data literacy.    

However, this _does_ affect how you should treat user-defined metrics. Defining something is a different skill to recognising it. This probably has some similarities to business dashboarding - the required level of numerical understanding is lower for using the dashboard than creating it (partly _because_ users of the dashboard may not have high numerical literacy levels). 