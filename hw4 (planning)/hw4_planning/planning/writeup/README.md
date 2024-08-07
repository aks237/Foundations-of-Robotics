# Project 4: Planning [![tests](../../../badges/submit-proj4/pipeline.svg)](../../../pipelines/submit-proj4/latest)

For the heuristic function, I reused the cost_to_come function. It is non-negative because it computes the absolute distances, so there are no negative distances. It does not overestimate because if the distance is greater than 2pi, 2pi is subtracted so the most efficient distance is computed.
Figure for 1.2:
![Alt text](../1_2.png)
Figure for 2.1:
![Alt text](../2_1.png)