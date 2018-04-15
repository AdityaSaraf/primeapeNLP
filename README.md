# PrimeapeNLP

# Training Setup

Make a `data/` folder in the root dir. This folder should contain `.story` files from the DeepMind Q&A Dataset built from CNN and DailyMail articles.

Install `nltk` for `python`.

Run `extractivePy/extract.py`. This will take some time, as it takes about `50ms` to process each file.

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

Note: In some files in the original dataset, the highlights introduce new information. An example of this is file `008fc24ca9f4c48a54623bef423a3f2f8db8451a.story`, in which all four highlights introduce information entirely absent from the article. 

Generated output for `008fc24ca9f4c48a54623bef423a3f2f8db8451a.story`:


```
1 (CNN) -- Michael Jackson, the show-stopping singer whose best-selling albums -- including "Off the Wall," "Thriller" and "Bad" -- and electrifying stage presence made him one of the most popular artists of all time, died Thursday, CNN has confirmed.
1 He was 50.
1 He collapsed at his residence in the Holmby Hills section of Los Angeles, California, about noon Pacific time, suffering cardiac arrest, according to brother Randy Jackson.
0 He died at UCLA Medical Center.
1 As news of his death spread, stunned fans began to react and remember one of the most remarkable careers in music.
2 Video shows ambulance rushing the pop star to the hospital
2 Crowds gather at the hospital where Jackson was rushed
2 A.J. Hammer: This "is big as it gets"; Rev. Al Sharpton: He was "a trailblazer"
2 Motown founder Berry Gordy Jr. says he's "numbed and shocked" at the news
```

