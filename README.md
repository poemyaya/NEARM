# NEARM in python
Natural Language Enhanced Association Rules Mining(NEARM) produces rules that  contain  natural  language  patterns and/or triple facts  in antecedent, and triple facts in consequent. In this way, NEARM can infer triple facts directly from plain text. At last, experiment
results demonstrate the effectiveness of the NEARM on relation classification  and  triple  facts  reasoning.

# Details
## Data
The  8 relations  used  in  experiments  are  manually  collected from Wikidata, and the Wikipedia pages of these entities are crawled as the source of plain text.
## Compared Methods
Given  an  unseen  mention m， we  use  the  four  methods  to  reason  triple facts: BoD*(C)->f(e1,e2)(NEARM), Beta(c)->f(e1,e2), BoW(c)->f(e1,e2), and using multi-label classification([magpie](https://github.com/inspirehep/magpie))

