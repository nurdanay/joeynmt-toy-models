# joeynmt-toy-models

This repo is just a collection of scripts showing how to install [JoeyNMT](https://github.com/joeynmt/joeynmt), preprocess
data, train and evaluate models.

# Requirements

- This only works on a Unix-like system, with bash.
- Python 3 must be installed on your system, i.e. the command `python3` must be available
- Make sure virtualenv is installed on your system. To install, e.g.

    `pip install virtualenv`

# Steps

Clone this repository in the desired place and check out the correct branch:

    git clone https://github.com/nurdanay/joeynmt-toy-models
    cd joeynmt-toy-models
    git checkout ex5

Create a new virtualenv that uses Python 3. Please make sure to run this command outside of any virtual Python environment:

    ./scripts/make_virtualenv.sh

**Important**: Then activate the env by executing the `source` command that is output by the shell script above.

Download and install required software:

    ./scripts/download_install_packages.sh

Download data:

    ./scripts/download_data.sh

Divide the training data into subsamples:

	mkdir -p proc_data

    shuf -n 100000 --random-source=data/train.de-en.de <(cat -n data/train.de-en.de) | sort -n | cut -f2- > proc_data/sub_sample.train.de-en.de

    shuf -n 100000 --random-source=data/train.de-en.de <(cat -n data/train.de-en.en) | sort -n | cut -f2- > proc_data/sub_sample.train.de-en.en

Preprocess data:

    # tokenize training data
	cat proc_data/sub_sample.train.de-en.de | tools/moses-scripts/scripts/tokenizer/tokenizer.perl > proc_data/tokenized.train.de-en.de

	cat proc_data/sub_sample.train.de-en.en | tools/moses-scripts/scripts/tokenizer/tokenizer.perl > proc_data/tokenized.train.de-en.en

	# tokenize dev data
	cat data/dev.de-en.de | tools/moses-scripts/scripts/tokenizer/tokenizer.perl > proc_data/tokenized.dev.de-en.de

	cat data/dev.de-en.en | tools/moses-scripts/scripts/tokenizer/tokenizer.perl > proc_data/tokenized.dev.de-en.en

	# tokenize test data
	cat data/test.de-en.de | tools/moses-scripts/scripts/tokenizer/tokenizer.perl > proc_data/tokenized.test.de-en.de

	cat data/test.de-en.en | tools/moses-scripts/scripts/tokenizer/tokenizer.perl > proc_data/tokenized.test.de-en.en


Train a word level model:

	mkdir models

	cd configs
	mv low_resource_example.yaml low_resource_word_level.yaml
	
	# change the settings in config file

	- src=de
	- trg=en
	- train="proc_data/tokenized.train.de-en"
    - dev="proc_data/tokenized.dev.de-en"
    - test="proc_data/tokenized.test.de-en"
    - level="word"
	- src_voc_limit: 2000
    - trg_voc_limit: 2000
	- beam=3
	- model_dir="models/low_resource_word_level.de-en"


	# train low_resource_word_level
    CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=10 python3 -m joeynmt train configs/low_resource_word_level.yaml

Train a bpe level model:

    # train and apply bpe

	mkdir -p vocab
	mkdir -p bpe

	subword-nmt learn-joint-bpe-and-vocab -i proc_data/tokenized.train.de-en.de proc_data/tokenized.train.de-en.en --write-vocabulary vocab/de_vocab_{vocab-size} vocab/en_vocab_{vocab_size} -s {vocab_size} --total-symbols -o bpe/bpe_{vocab_size}

	# apply bpe to training data
	subword-nmt apply-bpe -c bpe/bpe_{vocab_size} --vocabulary vocab/de_vocab_{vocab-size}  --vocabulary-threshold 10 < proc_data/tokenized.train.de-en.de > bpe/bpe_{vocab-size}.tokenized.train.de-en.de
	subword-nmt apply-bpe -c bpe/bpe_{vocab_size} --vocabulary vocab/en_vocab_{vocab-size}  --vocabulary-threshold 10 < proc_data/tokenized.train.de-en.en > bpe/bpe_{vocab-size}.tokenized.train.de-en.en

	# apply bpe to dev data
	subword-nmt apply-bpe -c bpe/bpe_{vocab_size} --vocabulary vocab/de_vocab_{vocab-size}  --vocabulary-threshold 10 < proc_data/tokenized.dev.de-en.de > bpe/bpe_{vocab-size}.tokenized.dev.de-en.de
	subword-nmt apply-bpe -c bpe/bpe_{vocab_size} --vocabulary vocab/en_vocab_{vocab-size}  --vocabulary-threshold 10 < proc_data/tokenized.dev.de-en.en > bpe/bpe_{vocab-size}.tokenized.dev.de-en.en

	# apply bpe to test data
	subword-nmt apply-bpe -c bpe/bpe_{vocab_size} --vocabulary vocab/de_vocab_{vocab-size}  --vocabulary-threshold 10 < proc_data/tokenized.test.de-en.de > bpe/bpe_{vocab-size}.tokenized.test.de-en.de
	subword-nmt apply-bpe -c bpe/bpe_{vocab_size} --vocabulary vocab/en_vocab_{vocab-size}  --vocabulary-threshold 10 < proc_data/tokenized.test.de-en.en > bpe/bpe_{vocab-size}.tokenized.test.de-en.en


	# build a joint vocabulary 
	python3 tools/joeynmt/scripts/build_vocab.py bpe/bpe_{vocab-size}.tokenized.train.de-en.de bpe/bpe_{vocab-size}.tokenized.train.de-en.en --output_path vocab/build_vocab_{vocab_size}.de-en



	# change the settings in config files
	cp low_resource_word_level.yaml low_resource_bpe_level_{vocab-size}.yaml


	- src=de
	- trg=en
	- train="proc_data/tokenized.train.de-en"
    - dev="proc_data/tokenized.dev.de-en"
    - test="proc_data/tokenized.test.de-en"
    - level="word"
	- src_vocab: "vocab/build_vocab_{vocab_size}.de-en"
    - trg_vocab: "vocab/build_vocab_{vocab_size}.de-en"
	- beam=3
	- model_dir="models/low_resource_bpe_level_{vocab-size}.de-en"

	
    #train the low_resource_bpe_model
	CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=12 python3 -m joeynmt train configs/low_resource_bpe_level_{vocab-size}.yaml


The training process can be interrupted at any time, and the best checkpoint will always be saved.


Evaluate models

	# evaluate low_resource_word_level

	# translate
	mkdir -p translations

	CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=10 python3 -m joeynmt translate configs/low_resource_word_level.yaml < proc_data/tokenized.test.de-en.de > translations/test.word.de-en.en

	# detokenize
	cat translations/test.word.de-en.en | tools/moses-scripts/scripts/tokenizer/detokenizer.perl -l en > translations/detok.test.de-en.en

	# compute BLEU score
	cat translations/detok.test.de-en.en | sacrebleu data/data/test.de-en.en



    # evaluate low_resource_bpe_level
	
	# translate
	CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=10 python3 -m joeynmt translate configs/low_resource_bpe_level_{vocab-size}.yaml < bpe/bpe_{vocab-size}.tokenized.test.de-en.de > translations/test_2000.de-en.en

	# detokenize
	cat translations/test_{vocab-size}.de-en.en | tools/moses-scripts/scripts/tokenizer/detokenizer.perl -l en > translations/detok.test_{vocab-size}.de-en.en

	# compute BLEU score
	cat translations/detok.test_{vocab-size}.de-en.en | sacrebleu data/test.de-en.en

## Findings

|        | use BPE    | vocabulary size    | BLEU   
| :------------- | :----------: | -----------: | -----------: |
|  a) | no   | 2000   | 10.4
| b)   | yes | 2000| 15.2
| c)   | yes | 3000| 11.1


Word level:
In word level, translation, we see a lot of unk in the sentences. An example :

    I want to <unk> with a <unk> <unk>, which was a <unk> <unk> called a <unk> <unk> <unk> <unk> in the <unk> century, and the <unk> says, "The God says," <unk>, "<unk>," <unk>, "<unk>," <unk>, "<unk>," <unk>, "<unk>," <unk>, <unk>, <unk>, <unk>, "<unk>, <unk>, <unk>, <unk>, <unk>, <unk>," <unk>, who's <unk>, "<unk>, <unk>, he says," <unk>, <unk>

The translation quality is unfortunately not good with word level model. But still, there are few sentences where the translation is good. AN example :

    The teachers didn't know that something was changed.

Bpe_2000 level:
The translation seems okay. We do not see any unk in the sentences. An example:
 
    If you have a game about this square, we can create a new economic and new data.

However there are some sentences where some words stays untranslated. An example:

    And this is happened, WEIL I have something with my ban and not TROTTT of these experience.

Also, there are some sentences where a word is repeated multiple times. An example:

	But if we're doing it, the human mind is going to be able to protect, and other people to be able to be able to figure out to be able to be able to be able to be able to be able to be able to be able to be able to be able to be able to be able to be able to be able to be able to be able to be able to be able.


Bpe_3000 level:	 
The translation seems a bit messy here. We do not see any unk , but the sentences are sometimes meaningless. An example:
 
    But if we make it, the human mind is to make it, and other people to find it very much more, more people to find the cost and phenomena to be the cost.


# Impact of beam size on translation quality

As the best model is the one with 2000 vocabulary size, we are going to use it for investigating the effect of different beam sizes.

Change the beam size from configs/low_resource_bpe_level_2000.yaml

-translate

    CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=10 python3 -m joeynmt translate configs/low_resource_bpe_level_2000.yaml < bpe/bpe_2000.tokenized.test.de-en.de > translations/beam_2000_test.de-en.en

-detokenize

    cat translations/beam_2000_test.de-en.en | tools/moses-scripts/scripts/tokenizer/detokenizer.perl -l en > translations/beam_2000_undo.tok.test.de-en.en 

-compute the BLEU score

    cat translations/beam_2000_undo.tok.test.de-en.en | sacrebleu data/test.de-en.en 


-get the plot of beam size and BLEU score

    ./scripts/graph_beam.py

![alt text](beam_size_plot.png)

![alt text](beam_size_bar_chart.png)