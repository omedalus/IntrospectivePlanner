# IntrospectivePlanner
A conventional planning AI with a few twists.

## Conventional Planner Architecture

This "conventional planner" will have a bit of a twist. Its architecture will be as follows:

1. An "evaluator" neural network.
    1. Input (size: 2s+a nodes, where s is # nodes in input vector and a is # nodes in action vector)
        1. Current world state
            1. Including a "pleasure" receptor.
        1. Proposed action
        1. Subsequent world state after action
    1. Output (size: 1 node)
        1. MANIFESTATION CERTAINTY: +1 if this action will cause this output, -1 if not.
    1. Training
        1. Every time the NN takes an action / turn advances
            1. The actual observed subsequent world state is trained with +1.
            1. Other proposed subsequent world states are trained with -1 / (proximity to actual observed state).
                1. Proposed states that were similar to the observed one get lightly penalized.
                1. Proposed states that were very different from the observed one get heavily penalized.
1. A "worldstate generator" GA: Evolves proposed world states
    1. Uses the evaluator NN as a fitness function.
        1. Current world state and an action (see below) are held fixed.
        1. Populations of different world states are proposed by the GA.
        1. Evaluator NN's output neuron value attempted to be maximized.
    1. Final population of proposed world states is retained for training the evaluator NN.
1. An "action generator" GA: Evolves proposed actions.
    1. Fitness function is a recursive planner!
        1. For each proposed action...
            1. Run the worldstate generator GA.
            1. Sum the manifestation certainties of all of the worldstate planner GA's final population members.
            1. EXPECTED VALUE: Sum the predicted level of the "pleasure" receptor of all expected worldstates, weighted by each worldstate's manifestation certainty fraction of the total.
            1. If expected value is neither clearly positive nor clearly negative (beyond set thresholds)...
                1. For each proposed worldstate, derive an effective subsequent expected pleasure receptor activation level...
                    1. RECURSE! Using the NN, feed the proposed worldstate as if it was the CURRENT worldstate and evolve the best action for it!
                    1. That action's expected value is this worldstate's expected pleasure receptor activation level.
            1. GA to maximize expected value



OPTIONAL: 
1. Curiosity
    1. Actions whose subsequent worldstates are largely unknown (sum of worldstate generator predictions is low, or difference between final winners is high) are given an implicit desirability 
        1. Compute prediction ambiguity: Magnitude of the vector sum of each predicted worldstate vector, weighted by its manifestation certainty

