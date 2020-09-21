# Quantum-Chain
Repo related to the [2020 GS1 US Hackathon](https://gs1us-futureproofhack-platform.bemyapp.com) with
[YouTube video here.](https://www.youtube.com/watch?v=yD1zfmUj72k&feature=youtu.be) 

**Project name:** Quantum Chain

#### Short Project description:
COVID19 vaccine distribution and en-route monitoring using Quantum Computing, AI and ML tools

#### Motivation:
The current Corona-Virus pandemic has a significant impact on people's lives. To return to a “normal” people will need vaccines to minimize the risk of getting sick. How to distribute a finite and fragile resource like the COVID19 vaccine while maintaining its effectiveness and maximizing its impact and value to the whole community?

#### Our solution:
We look at the distribution of vaccine batches across the USA as an optimization problem on (1)  the impact of a particular distribution and (2) the delivery routes. Once the distribution of a batch is in progress, we monitor the environment and assess the state of the vaccine packages. Data is stored using GS1 formats & conventions to be used in our AI/ML decision making and re-routing algorithms.

#### Solution Steps:

Step 1: Identify the maximal impact distribution plan: Identify cities for vaccine distribution by solving an optimization problem with adjustable impact function; charting delivery routes from the main distribution hubs to the targeted hospitals/clinics.

Step 2: Start a continuously monitored  distribution process: Send viecles en route, monitor the microclimate, store data using GS1 standards; upon delivery evaluate the data collected and its limits. Are the states of  other packages within the expected bounds?

Step 3: Re-balance and re-route the distribution: If vaccine efficiency/product quality is affected then assess for alternative nearby delivery locations that will maintain maximum impact solution; proceed with the updated delivery schedule;

Step 4: Update Model Parameters and the Data Assessment: Update the input records for better assessments, AI/ML analyzes, forecasting of the vaccine states, and impact estimates relevant to the previous steps. Prepare for the distribution of the next batch.
