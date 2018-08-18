# NEARM 
Natural Language Enhanced Association Rules Mining(NEARM) produces rules that  contain  natural  language  patterns and/or triple facts  in antecedent, and triple facts in consequent. In this way, NEARM can infer triple facts directly from plain text. At last, experiment
results demonstrate the effectiveness of the NEARM on relation classification  and  triple  facts  reasoning.

# Details
## Data
The  8 relations  used  in  experiments  are  manually  collected from Wikidata, and the Wikipedia pages of these entities are crawled as the source of plain text.
## Compared Methods
### Triple  facts  Reasoning.
Given  an  unseen  mention m， we  use  the  four  methods  to  reason  triple facts: BoD*(C)->f(e1,e2)(NEARM), Beta(c)->f(e1,e2), BoW(c)->f(e1,e2), and using multi-label classification([magpie](https://github.com/inspirehep/magpie)).
### Relation Classification
Since NEARM groups mentions in clusters and clusters are represented as BoD*, a new mention can  be  easily  transformed  into  a  vector  by  concatenating  the fitness  of  its  words  w.r.t  the  BoD*  words. However,  BoD*  only  uses  the  information  from  texts.  Instead,  BoD*  +  Rules  converts  the triple facts in the consequent of rules into binary features and injects it into the previous vector. For each rule, three binary values  (true,  false  and  unknown)  are  added.  True  means  the mention matches both antecedent and consequent. False means the mention matches only antecedent and unknown means uncertainty due to absent property. Lastly, relation classification can be transformed into multi-classification problems.



