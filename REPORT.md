# Assignment 2 Report

*Delete this italic guidance as you fill in each section. You'll be asked to
defend any of this without your code in front of you. Write only what you
can actually explain.*

- **Name**: Julián Consuegra
- **Student ID**: 19376
- **Email**: jconsuegra.ieu2022@student.ie.edu
- **Group**: BBADBA 5A 

## Business problem, and the cost of being wrong

*The decision this model supports, who or what acts on it, and what happens
when it's wrong in each direction. Be concrete about the asymmetry: which
mistake is worse, roughly by how much, and why. Everything downstream (your
threshold, how much you send to a person, which metric you care about) has to trace
back to this section.*

I decided to focus my project on the manufacturing process  of circuit boards. Circuit boards are flat green boards located inside basically any electronic device. Their main purpose is to act as the "skeleton" of these devices, carrying wires, chips and overall small components that enable proper functionality. The business I will be focusing on is a factory that produces these boards and sells them to electronic manufacturers. Currently, the factory relies on inspectors who personally check the products before they are shipped. Defects are often tiny, and checking every board by eye is slow and tiring, so inspectors can miss them. I will create a model that is able to flag boards that are likely to have a defect, reshaping the human-in-the-loop and introducing human interaction only when the model is unsure. Defects will be treated as the positive class during the detection process. 

This seemed like an interesting opportunity since production lines in this industry must follow strict quality control measures as these boards will ultimately determine if the final product works or not. Also, the cost of a mistake is high compared to other industries such as food or clothing. Since electronic products are usually sold at high prices in the market, a false negative would lead to producing broken phones or computers that result in client dissatisfaction and refund requests. On the other hand, a false positive would not be as costly. A good board would be wasted and the costs incurred would be those of manufacturing it which are minimal or even just a couple of minutes of an inspector depending on the case. Considering this, a false negative could cost approximately 10x to 50x (or more depending on the final product) more than a false positive. To put it in perspective, a board can cost about €5 to make while a refund of a whole device could cost €200 at least (some could even reach €1,000+ depending on brand and device). It is important to know the factory is not in charge of the refund process as the electronic manufacturer is the one facing the client directly, but they will be responsible for a compensation. It is a significant difference that if not managed properly, profit margins of businesses could be directly affected in the long run. Since a missed defect is the worst outcome, a low threshold will be set to avoid false negatives even if there needs to be more human intervention at first involving inspections. The metric to focus on will specifically be recall on defects;lower precision will be accepted considering the ultimate goal. 

## Dataset

*Workspace / project / version on Roboflow Universe, and the link. What one
image represents, what the classes are, and why this dataset actually serves
the problem above rather than merely resembling it.*

Workspace: object-detection-dt-wzpc6
Project: pcb-dataset-defect
Version: 1
Link: universe.roboflow.com/object-detection-dt-wzpc6/pcb-dataset-defect/dataset/1
License: CC BY 4.0

In the chosen dataset, each image are plain circuit boards (with no chips attached yet) with different defects highlighted with boxes sorrounding them. They are very small details represented by these 6 different classes:

1. missing_hole: A hole that should have been drilled and isn't there
2. mouse_bite: Small indents out of the edge of a copper line, making it thinner and weaker
3. open_circuit: A copper line is broken, so electriicty can't pass.
4. short: Two copper lines are joined when they shouldn't be.
5. spur: A small spike of copper sticking out from a line
6. spurious_copper Residue of copper where there shouldn't be any.

The dataset serves the problem directly as the images used show the boards at the stage in which they are sent to electronic manufacturers before any component is added. They reflect real and common defects a board may have after production. However, there are some aspects that need to be considered when assessing how realistic the sample actually is. The dataset is defect-heavy (each image contains at least 1 defect) and in real factories, the majority of boards are fine. Also, there are only about 10 different board designs when in reality, factories are responsible for many more designs. Since the dataset only includes images of boards with defects, it is not certain how often this happens in production and a realistic share of defective boards will have to be assumed when calculating costs. Finally, since the board designs displayed are the same in training and testing, there might be inflated results that will differ when boards with different designs are introduced. Even though the dataset's limitations affect the generalization of results, the information fits the problem. It teaches the model what a defect looks like  and the assumptions made will handle the gaps to make the business impact clear.

## What the dataset's composition implies

*Instances per class, train/val/test sizes, typical object size relative to the
image. Then the interpretation: which per-class numbers will be too thin to
trust, whether the test split resembles the images you'd really see, and what
you therefore can't conclude from your results.*

| Class           | Train | Valid | Test |
|-----------------|------:|------:|-----:|
| missing_hole    |   360 |    83 |   54 |
| mouse_bite      |   385 |    47 |   60 |
| open_circuit    |   409 |    28 |   45 |
| short           |   397 |    35 |   59 |
| spur            |   372 |    32 |   84 |
| spurious_copper |   380 |    48 |   75 |
| **Total defects** | **2,303** | **273** | **377** |
| **Images**      |   541 |    62 |   90 |

The distribution of instances reflects a good class balance in training. The model will properly learn and practice from the different defects. Any difference in performance between classes later on will come from how hard the defect is to spot, not from lack of examples. When looking at testing, the sample is smaller, with 45-84 defects per class and a total of 90 images. This is important when analyzing per-class results since getting only 2 or 3 right or wrong could alter final metrics more. For example, on 'open_circuits', getting just 2 more defects wrong out of 45 drops recall by about 4 points. This could be defined by chance so when interpreting the results, a small difference will not mean one class is better. Additionally, validation is even smaller, so the progress checks are roguh rather than precise. 

After computing the main statistics about the dataset, I identified that the median defect covers about 0.07% of the image. Even the largest defect is under 1% (0.825%) of the whole image. Evidently, it is a very small portion that could be difficult to spot. Before looking at images, YOLO shrinks the width of them (640 pixels by default) and defects would only be about 15-20 pixels after this. Due to this, during training and testing I will use larger image sizes to ensure proper learning and prevent the model from missing defects. This makes the process longer and it takes up more memory but it should help in performance.

Finally, the test set has the same type of images that the training has. This means that an actual factory scenario isn't fully represented. Every test image comes from the same board designs as training and each board has at least one defect. In a realistic scenario, every board wouldn't necessarily have a defect and many more than about 10 designs would be seen. This means that the scores will reflect how well the model spots defects on boards it has already seen designs of. The test cannot show how well the model deals with board designs that have not been seen or differentiate boards that have no defects at all. Due to this, in a real-world scenario I can expect the scores to be lower considering these limitations. 

## Finetuning and baselines

*Which model and task (detection or classification) and why. A results table on
the same test split: your finetuned model, the pretrained COCO model zero-shot,
and a trivial baseline. What changed, and whether the gap is as large as you
expected.*

## Per-class evaluation and failure modes

*Per-class AP50, or per-class precision/recall and the confusion matrix.
Which class carries the headline number, which one is dragging, and what the
model actually confuses with what. Show where it breaks, not just that it
works.*

## Cost matrix and operating point
Based on research on actual costs of PCB factories and Spanish salaries, I approximated euro cost for each kind of error.

- False Negative: **€100**. Once a defective board ships, the client assembles components onto it, and when it fails the board maker has to compensate the client for those components and the rework. A rule of thumb will be implemented in which the defect gets 10x more expensive at each stage it escapes. So for a €5 board problem, it becomes about €50-100+ once it reaches assembling stages.

- False Positive: **€5**. If a good board is wasted, the cost incurred would be production cost. This is the value of producing a multi-layered board on average based on PCB factory information.

- Inspection: **€0.33**. When inspection is needed due to uncertainty on a board, the cost is calculated based on how much time an inspector takes checking and the average cost incurred by employers for having inspectors in Spain. It takes about 1 minute at around €20/hour would result in a cost of approximately €0.33 per revision. 

- Correct Decisions: **€0**. A correctly discarded board was lost anyway, whatever the model does, so the model doesn't add a cost there. 

- Base rate: **5%**. In an industry survey towards PCB companies in which they asked what percent of bare boards passed inspection, the average was from 90-98%. I decided to use an average of 95% meaning that only 5% of the boards in a factory are defective. 

The most uncertain assumption here is the cost for False Negatives. It highly depends on whether the client catches it in initial testing before adding components (as low as 30 euros) or in the point where the defective board ends up in a finished phone that a customer returns (500 euros or more). Considering this, the threshold decision will be a trade-off between missing defects and paying more for inspections. If a miss is very expensive, the threshold for inspection will be low to make sure there are minimal misses. However, if a miss is cheap, fewer inspections are worth paying and a higher threshold can be set. To address this, I will rerun a cost sweep with €30 and €500 to see if thresholds differ or stay somewhat similar.  

*Your euro cost for each kind of error and where each figure came from. The
base rate you assumed. The cost-against-threshold sweep, and the operating
point you chose. State the assumption that would most change your answer if it
were wrong.*

## What a person still has to check

*Your two thresholds, and what share of cases they send to a person. How many
that is per day, how long one takes to check, and how many people that needs.
Is that realistic? Then your design priced against the three alternatives:
doing nothing, having a person check everything, and letting the model decide
on its own.*

## Limitations & next steps

*Real limitations you found, and concretely how you'd address each one with
more time or data. Not generic hedging.*

## Generative AI use disclosure

*Per the syllabus AI Policy: what you used and how, or "no AI content used."*
