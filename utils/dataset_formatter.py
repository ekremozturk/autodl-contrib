# Author: Zhengying LIU
# Creation date: 30 Sep 2018
# Description: API for formatting AutoDL datasets

import tensorflow as tf
import os
import numpy as np
from pprint import pprint

verbose = True

def _int64_feature(value):
  # Here `value` is a list of integers
  return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

def _bytes_feature(value):
  # Here `value` is a list of bytes
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))

def _float_feature(value):
  # Here `value` is a list of floats
  return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def _feature_list(feature):
  # Here `feature` is a list of tf.train.Feature
  return tf.train.FeatureList(feature=feature)

def label_sparse_to_dense(li_label_nums, output_dim):
  dense_label = np.zeros(output_dim)
  for label_num in li_label_nums:
    dense_label[label_num] = 1
  return dense_label

def feature_sparse_to_dense(features): # TODO
  return features

def avg_length_times_two(li):
  """To be used as callable for `sequence_size_func` in
  `UniMediaDatasetFormatter`.
  """
  li = np.array(li)
  return int(li.mean() * 2)

def percentile_95(li):
  """To be used as callable for `sequence_size_func` in
  `UniMediaDatasetFormatter`.
  """
  li = np.array(li)
  return int(np.percentile(li, 95))

class UniMediaDatasetFormatter():
  def __init__(self,
               dataset_name,
               output_dir,
               features_labels_pairs_train,
               features_labels_pairs_test,
               output_dim,
               col_count,
               row_count,
               sequence_size=None,
               num_examples_train=None,
               num_examples_test=None,
               is_sequence_col='false',
               is_sequence_row='false',
               has_locality_col='true',
               has_locality_row='true',
               format='DENSE',
               is_sequence='false',
               sequence_size_func=percentile_95,
               new_dataset_name=None):
    # Dataset basename, e.g. `adult`
    self.dataset_name = dataset_name
    if new_dataset_name:
      self.new_dataset_name = new_dataset_name
    else:
      self.new_dataset_name = dataset_name
    # Output directory, absolute path
    self.output_dir = os.path.abspath(output_dir)
    # Iterables containing (features, labels) pairs, where `features` is a list
    # of vectors in float. `labels` is a list of integers.
    self.features_labels_pairs_train = features_labels_pairs_train
    self.features_labels_pairs_test = features_labels_pairs_test
    # Some metadata on the dataset
    self.output_dim = output_dim
    self.col_count = col_count
    self.row_count = row_count
    if isinstance(sequence_size, int):
      self.sequence_size = sequence_size
    else:
      self.sequence_size = self.get_sequence_size(func=sequence_size_func) # can be slow!
    self.is_sequence_col = is_sequence_col
    self.is_sequence_row = is_sequence_row
    self.has_locality_col = has_locality_col
    self.has_locality_row = has_locality_row
    self.format = format
    self.is_sequence = is_sequence
    if num_examples_train:
      self.num_examples_train = num_examples_train
    if num_examples_test:
      self.num_examples_test = num_examples_test

    # Some computed properties
    self.dataset_dir = self.get_dataset_dir()
    self.dataset_data_dir = self.get_dataset_data_dir()


  def get_dataset_dir(self):
    dataset_dir = os.path.join(self.output_dir, self.new_dataset_name)
    return dataset_dir

  def get_dataset_data_dir(self):
    dataset_data_dir = os.path.join(self.dataset_dir,
                                    self.new_dataset_name + '.data')
    return dataset_data_dir

  def get_num_examples(self, subset='train'):
    if subset == 'train':
      data = self.features_labels_pairs_train()
    elif subset == 'test':
      data = self.features_labels_pairs_test()
    else:
      raise ValueError("Wrong key `subset`! Should be 'train' or 'test'.")
    if hasattr(data, '__len__'):
      return len(data)
    else:
      count = sum([1 for x in data])
      return count # WARNING: this step could be slow.

  def get_metadata_filename(self, subset='train'):
    filename = 'metadata.textproto'
    path = os.path.join(self.dataset_data_dir, subset, filename)
    return path

  def get_data_filename(self, subset='train'):
    filename = 'sample-' + self.new_dataset_name + '.tfrecord'
    path = os.path.join(self.dataset_data_dir, subset, filename)
    return path

  def get_solution_filename(self): # solution file only for solution
    output_dir = self.output_dir
    dataset_name = self.new_dataset_name
    path = os.path.join(output_dir, dataset_name, dataset_name + '.solution')
    return path

  def get_sequence_size(self, func=max):
    length_train = [len(x) for x, _ in self.features_labels_pairs_train()]
    length_test = [len(x) for x, _ in self.features_labels_pairs_test()]
    length_all = length_train + length_test
    return func(length_all)

  def get_metadata(self, subset='train'):
    metadata = """is_sequence: <is_sequence>
sample_count: <sample_count>
sequence_size: <sequence_size>
output_dim: <output_dim>
matrix_spec {
  col_count: <col_count>
  row_count: <row_count>
  is_sequence_col: <is_sequence_col>
  is_sequence_row: <is_sequence_row>
  has_locality_col: <has_locality_col>
  has_locality_row: <has_locality_row>
  format: <format>
}
"""
    if subset == 'train':
      sample_count = self.num_examples_train
    else:
      sample_count = self.num_examples_test
    metadata = metadata.replace('<sample_count>', str(sample_count))
    metadata = metadata.replace('<is_sequence>', str(self.is_sequence))
    metadata = metadata.replace('<sequence_size>', str(self.sequence_size))
    metadata = metadata.replace('<output_dim>', str(self.output_dim))
    metadata = metadata.replace('<col_count>', str(self.col_count))
    metadata = metadata.replace('<row_count>', str(self.row_count))
    metadata = metadata.replace('<is_sequence_col>', str(self.is_sequence_col))
    metadata = metadata.replace('<is_sequence_row>', str(self.is_sequence_row))
    metadata = metadata.replace('<has_locality_col>',str(self.has_locality_col))
    metadata = metadata.replace('<has_locality_row>',str(self.has_locality_row))
    metadata = metadata.replace('<format>', str(self.format))
    return metadata

  def write_tfrecord_and_metadata(self, subset='train'):
    # Make directories if necessary
    if not os.path.isdir(self.output_dir):
      os.mkdir(self.output_dir)
    if not os.path.isdir(self.dataset_dir):
      os.mkdir(self.dataset_dir)
    if not os.path.isdir(self.dataset_data_dir):
      os.mkdir(self.dataset_data_dir)
    subset_dir = os.path.join(self.dataset_data_dir, subset)
    if not os.path.isdir(subset_dir):
      os.mkdir(subset_dir)

    # Write metadata
    path_to_metadata = self.get_metadata_filename(subset=subset)
    metadata = self.get_metadata(subset=subset)
    with open(path_to_metadata, 'w') as f:
      f.write(metadata)

    # Write TFRecords
    path_to_tfrecord = self.get_data_filename(subset=subset)
    is_test_set = (subset == 'test')
    if is_test_set:
      id_translation = 0
      data = self.features_labels_pairs_test()
      num_examples = self.num_examples_test
    else:
      id_translation = self.num_examples_test
      data = self.features_labels_pairs_train()
      num_examples = self.num_examples_train

    if is_test_set:
      self.num_examples_test = 0
    else:
      self.num_examples_train = 0
    counter = 0
    labels_array = np.zeros((num_examples, self.output_dim))
    with tf.python_io.TFRecordWriter(path_to_tfrecord) as writer:
      for features, labels in data:
        if verbose and counter % 100 == 0:
          print(f"Formatting dataset: {self.dataset_name}, subset: {subset}, index: {counter + id_translation}, example {counter} of {num_examples}...")
        if is_test_set:
          label_index = _int64_feature([])
          label_score = _float_feature([])
          labels_array[counter] = label_sparse_to_dense(labels, self.output_dim)
        else:
          label_index = _int64_feature(labels)
          label_score = _float_feature([1]*len(labels))
        context_dict = {
            'id': _int64_feature([counter + id_translation]),
            'label_index': label_index,
            'label_score': label_score
        }

        if self.format == 'SPARSE':
          sparse_col_index, sparse_row_index, sparse_value =\
              feature_sparse_to_dense(features) # TODO
          feature_list_dict = {
            '0_sparse_col_index': _feature_list([_int64_feature(sparse_col_index)]),
            '0_sparse_row_index': _feature_list([_int64_feature(sparse_row_index)]),
            '0_sparse_value': _feature_list([_float_feature(sparse_value)])
          }
        elif self.format == 'DENSE':
          feature_list = [_float_feature(x) for x in features]
          feature_list_dict={
            '0_dense_input': _feature_list(feature_list)
          }
        else:
          raise ValueError(f"Wrong format key: {self.format}")

        context = tf.train.Features(feature=context_dict)
        feature_lists = tf.train.FeatureLists(feature_list=feature_list_dict)
        sequence_example = tf.train.SequenceExample(
            context=context,
            feature_lists=feature_lists)
        writer.write(sequence_example.SerializeToString())
        counter += 1
        if is_test_set:
          self.num_examples_test += 1
        else:
          self.num_examples_train += 1

    # Write solution file
    if is_test_set:
      path_to_solution = self.get_solution_filename()
      np.savetxt(path_to_solution, labels_array, fmt='%.0f')

  def press_a_button_and_give_me_an_AutoDL_dataset(self):
    print(f"Begin formatting dataset: {self.dataset_name}.")
    self.write_tfrecord_and_metadata(subset='test')
    self.write_tfrecord_and_metadata(subset='train')
    dataset_info = self.__dict__.copy()
    dataset_info.pop('features_labels_pairs_train', None)
    dataset_info.pop('features_labels_pairs_test', None)
    print("Basic dataset info:")
    pprint(dataset_info)
