# PrimeapeNLP

# Training Setup

**Note: Running the script to build the data for extractive summarization may take several hours. On my machine (Ryzen 1700x, 32GB 2933MHz RAM), it took just under  4 hours. The task is not currently multi-threaded, although it probably could be sped up if that were included.**

Make a `data/` folder in the root dir. This folder should contain `.story` files from the DeepMind Q&A Dataset built from CNN and DailyMail articles.

Install `nltk` for `python`.

Run `extractivePy/extract.py`. This will take some time, as it takes about `50ms` to process each file.

-----

**INCOMPLETE FEATURE**: Run `extract.py` with `some flag` to auto-merge lines. 

The base dataset is very messy and often has lines split arbitrarily. For example, the following sentence is split into 4 lines in the data set. This is a problem for extractive summarization models dependent on good sentence partitions.

```
'General
medical facilities throughout Sierra Leone are currently under severe
strain due to the Ebola outbreak, and unable to provide the same
standard of healthcare as in the UK.
```

By running with `some flag`, the parser will combine all lines in the input data into a single line of text, and then split using the built-in regex.

Note that this will cause some previously-correct sentences to be wrong, as not all sentences end with proper punctuation. Again, this is simply a limitation of the original abstractive summarization dataset that we are using to build our extractive summarization dataset.

For example, the following three sentences would be combined into a single sentence due to the lack of punctuation

```
Greens Upper House MP John Kaye, left,  will move to make the 'hidden' documents public during parliament next week
The NSW Government has decided to keep casino details public citing their disclosure would damage its license 
'Next week, the Greens will be moving to subpoena the missing documents, using the upper House call-for-papers process,' he said.
```

This is a tradeoff that we are not able to measure, so the default option is to respect line breaks in the original DailyMail & CNN dataset.

-----

You should now have a folder in the root at `extracted/`.

Extracted files have the following format:

`<#> <Sentence Text>`

For example,

`1 Two extremely rare elephant twins have been born on a game reserve in south-east South Africa.`

The numbers are as follows:

```
0 = Normal sentence in the article.
1 = Sentence in the article selected as a summarizing sentence.
2 = Original highlight from the CNN/DailyMail dataset.
```

A typical output file:

```
1 Two extremely rare elephant twins have been born on a game reserve in south-east South Africa.
0 The unnamed babies were spotted on the Pongola Game Reserve in Northern Kwa-Zulu Natal this week, watched over by their mother and the rest of the herd.
1 Less than one per cent of elephants born are twins, and the last reported set  in the area born in 2006, to a cow in Kruger National Park.
0 Scroll down for video
1 Baby joy: The two adorable twin baby elephants and their mother, 31-year-old Curve, in South Africa
1 The twins were born to Curve, a 31-year-old cow, and it is thought the father is Ingani, a 44-year-old elephant bull that died just over a year ago.
0 Although the twins’ father is no longer in the picture, Curve is getting plenty of help from the rest of the herd in caring for her young ones.
0 Pongola Game Reserve management have yet to establish the sex of the twins, as they are giving Curve space to nurse and feed her young ones to ensure they have the best start.
0 ‘Mortality of one of the twins usually occurs as the increasing demand for milk by two calves cannot be met by the mother and the less dominant of the two calves usually cannot gain access to its share, so this is the best start,’ Elephant specialist, Dr.
0 Ian Whyte, formerly of the National Parks Board at Kruger National Park said.
0 Helping hands: Curve takes her young twins to drink alongside another elephant cow and her young
0 Camera shy: The twins hide behind their mother on the Pongola Game Reserve, South Africa
0 Time to go: The twins and Curve are being left alone by reserve staff so the three can bond in peace
2 Rare twin elephants born on South African game reserve
2 Less than one per cent of elephants born are sets of twins
2 Mother of twins are a 31-year-old cow named Curve
```

Note: In some files in the original dataset, the highlights introduce new information. An example of this is file `008fc24ca9f4c48a54623bef423a3f2f8db8451a.story`, in which all four highlights introduce information entirely absent from the article. Generated output for `008fc24ca9f4c48a54623bef423a3f2f8db8451a.story`:

```
1 (CNN) -- Michael Jackson, the show-stopping singer whose best-selling albums -- including "Off the Wall," "Thriller" and "Bad" -- and electrifying stage presence made him one of the most popular artists of all time, died Thursday, CNN has confirmed.
1 He was 50.
1 He collapsed at his residence in the Holmby Hills section of Los Angeles, California, about noon Pacific time, suffering cardiac arrest, according to brother Randy Jackson.
0 He died at UCLA Medical Center.
0 As news of his death spread, stunned fans began to react and remember one of the most remarkable careers in music.
2 Video shows ambulance rushing the pop star to the hospital
2 Crowds gather at the hospital where Jackson was rushed
2 A.J. Hammer: This "is big as it gets"; Rev. Al Sharpton: He was "a trailblazer"
2 Motown founder Berry Gordy Jr. says he's "numbed and shocked" at the news
```

