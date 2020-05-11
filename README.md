# joeynmt-toy-models

This repo is just a collection of scripts showing how to install joeynmt with source factors, preprocess data, train and evaluate models.

# Requirements

- This only works on a Unix-like system, with bash.
- Python 3 must be installed on your system, i.e. the command `python3` must be available
- Make sure virtualenv is installed on your system. To install, e.g.

	`pip install virtualenv`

# Steps

Clone this repository in the desired place and check out the correct branch:

	git clone https://github.com/nurdanay/joeynmt-toy-models
	cd joeynmt-toy-models
	checkout ex4

Create a new virtualenv that uses Python 3. Please make sure to run this command outside of any virtual Python environment:

	./scripts/make_virtualenv.sh

**Important**: Then activate the env by executing the `source` command that is output by the shell script above.

Download and install required software:

	./scripts/download_install_packages.sh

Download and split data:

	./scripts/download_split_data.sh

Preprocess data:

	./scripts/preprocess.sh

Then finally train a model:

	./scripts/train.sh

The training process can be interrupted at any time, and the best checkpoint will always be saved.

Evaluate a trained model with

	./scripts/evaluate.sh

# Findings

| Models   | Embedding size|  BLEU |
|----------|:-------------:|------:|
| rnn_wmt16_deen.yaml|  512 | 9.1 |
| rnn_wmt16_factors_concatenate_deen.yaml|    512  | 5.7   |
| rnn_wmt16_factors_add_deen.yaml | 512 |    5.7 |

The result is surprising. I was expecting higher Bleu scores after adding source factors to the model. But, Bleu scored dropped down. The reason might be the embedding size that I have used. A higher embedding size might give a better result. Because training lasts quite a long time, I could not test this.

The reason of me using the same embedding size as the base model is that i thought embedding size would not effect the reason that much. However it seems that it has an effect.