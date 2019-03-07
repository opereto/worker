This service creates, modifies and delete a stateful set of dedicated workers based on a pre-defined container images. 

#### Assumptions/Limitations
**Important** It is assumed that the worker container runs opereto agent as the main CMD directive. Unlike simple pod workers that are created and removed by Opereto standard workers on-demand, 
stateful set workers contain one or more replicas of pods with embedded agent. Any container can be converted into a stateful set worker adding the following to the container specification:

```console


```
