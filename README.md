# How to Contribute Datasets to AutoDL Challenge
This repo provides instructions and examples to contribute datasets to a repository we are building, in conjuction with the preparation of the [AutoDL challenge](http://autodl.chalearn.org).

## Table of Contents
- [Quick start](#quick-start)
- [What is needed?](#what-is-needed)
- [Formats](#formats)
	- [File Format](#file-format)
	- [TFRecord Format](#tfrecord-format)
- [Credits](#credits)

## Quick start

To run the example type the following commands:

```
git clone http://github.com/zhengying-liu/autodl-contrib
cd autodl-contrib
python3 check_n_format.py /file_format/monkeys
```

## What is needed?

* **multi-label (or multi-class) classification tasks.** 
* **Video, image, text, speech or time series datasets.**
* **No size limit** but if your dataset exceed 10 GB, please [Contact us](mailto:autodl@chalearn.org).


## Where to submit

[Email us](mailto:autodl@chalearn.org) a URL to an on-line storage place (e.g. dropbox or Google drive) when we can pull your data from.


## Formats

* Each example is an independent file.
* Labels are contained in a separate CSV file.
* Meta-data in `private.info`.

Examples are provided in [file_format](https://github.com/zhengying-liu/autodl-contrib/tree/master/file_format) folder.


### Understanding check_n_format.py

This script does the following:

* Read the meta-data in `private.info`.
* Compute simple statistics about the data (file number, etc.) and check consistency with the CSV file containing the labels.
* Train/test split data.
* Format the data to TFRecord format.
* Run baseline.
* Ask the user to check a few samples manually.

 
TFRecord format is the final format of the AutoDL challenge, following [SequenceExample](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/example/example.proto#L92) proto (see [Protocol Buffers](https://developers.google.com/protocol-buffers/docs/overview)).

More details and [an example dataset](https://github.com/zhengying-liu/autodl-contrib/tree/master/tfrecord_format/mini-mnist) in TFRecord format can be found in the sub-directory [`tfrecord_format`](https://github.com/zhengying-liu/autodl-contrib/tree/master/tfrecord_format).


## Credits
AutoDL is a project in collaboration with Google, ChaLearn and Inria

Please contact us via email: autodl@chalearn.org.
