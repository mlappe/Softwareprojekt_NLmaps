
#!/usr/bin/env python3

# This is a changed Version of 
#	https://github.com/tensorflow/tensorflow/blob/01c87f55ca7b64a2dc680aff8b2a60aa079746ec/tensorflow/models/rnn/translate/translate.py
#
# by the TenorFlow Authors.
# Changes were made by Stoyan Dimitrov and Max Lappé in July 2016
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#original Copyright notice:

# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Binary for training translation models and decoding from them.

Running this program without --decode will download the WMT corpus into
the directory specified as --data_dir and tokenize it in a very basic way,
and then start training a model saving checkpoints to --train_dir.

Running with --decode starts an interactive loop so you can see how
the current checkpoint translates English sentences into French.

See the following papers for more information on neural translation models.
 * http://arxiv.org/abs/1409.3215
 * http://arxiv.org/abs/1409.0473
 * http://arxiv.org/abs/1412.2007
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import math
import os
import random
import sys
import time
import random
import itertools


# Path hack.
import sys, os
sys.path.insert(0, os.path.abspath('..'))
from cfg import my_cfg_set as cfg
from oldLinearizer import MRL_Linearizer
from oldLinearizer import Delinearizer

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

from tensorflow.models.rnn.translate import data_utils
from tensorflow.models.rnn.translate import seq2seq_model

tf.app.flags.DEFINE_float("learning_rate", 0.5, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,
                          "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 64,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 256, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", 3, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("en_vocab_size", 40000, "English vocabulary size.")
tf.app.flags.DEFINE_integer("fr_vocab_size", 40000, "MRL vocabulary size.")
tf.app.flags.DEFINE_string("data_dir", "./tmp", "Data directory")
tf.app.flags.DEFINE_string("train_dir", "./tmp", "Training directory.")
tf.app.flags.DEFINE_integer("max_train_data_size", 0,
                            "Limit on the size of training data (0: no limit).")
tf.app.flags.DEFINE_integer("steps_per_checkpoint", 200,
                            "How many training steps to do per checkpoint.")
tf.app.flags.DEFINE_boolean("decode", False,
                            "Set to True for decoding.")
tf.app.flags.DEFINE_boolean("self_test", False,
                            "Run a self-test if this is set to True.")
tf.app.flags.DEFINE_integer("beam", 100,
                            "Find the [beam]-best translations.")
tf.app.flags.DEFINE_integer("maxSteps", 1600,
                            "Number of Training Steps")
tf.app.flags.DEFINE_boolean("demo", False,
                            "Set to True for interactive decoding.")

FLAGS = tf.app.flags.FLAGS

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
_buckets = [(5, 15), (10, 20), (20, 30), (40, 50)]


def read_data(source_path, target_path, max_size=None):
  """Read data from source and target files and put into buckets.

  Args:
    source_path: path to the files with token-ids for the source language.
    target_path: path to the file with token-ids for the target language;
      it must be aligned with the source file: n-th line contains the desired
      output for n-th line from the source_path.
    max_size: maximum number of lines to read, all other will be ignored;
      if 0 or None, data files will be read completely (no limit).

  Returns:
    data_set: a list of length len(_buckets); data_set[n] contains a list of
      (source, target) pairs read from the provided data files that fit
      into the n-th bucket, i.e., such that len(source) < _buckets[n][0] and
      len(target) < _buckets[n][1]; source and target are lists of token-ids.
  """
  data_set = [[] for _ in _buckets]
  with tf.gfile.GFile(source_path, mode="r") as source_file:
    with tf.gfile.GFile(target_path, mode="r") as target_file:
      source, target = source_file.readline(), target_file.readline()
      counter = 0
      while source and target and (not max_size or counter < max_size):
        counter += 1
        if counter % 100000 == 0:
          print("  reading data line %d" % counter)
          sys.stdout.flush()
        source_ids = [int(x) for x in source.split()]
        target_ids = [int(x) for x in target.split()]
        target_ids.append(data_utils.EOS_ID)
        for bucket_id, (source_size, target_size) in enumerate(_buckets):
          if len(source_ids) < source_size and len(target_ids) < target_size:
            data_set[bucket_id].append([source_ids, target_ids])
            break
        source, target = source_file.readline(), target_file.readline()
  return data_set


def create_model(session, forward_only):
  """Create translation model and initialize or load parameters in session."""
  model = seq2seq_model.Seq2SeqModel(
      FLAGS.en_vocab_size, FLAGS.fr_vocab_size, _buckets,
      FLAGS.size, FLAGS.num_layers, FLAGS.max_gradient_norm, FLAGS.batch_size,
      FLAGS.learning_rate, FLAGS.learning_rate_decay_factor,
      forward_only=forward_only)
  ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
  if ckpt and tf.gfile.Exists(ckpt.model_checkpoint_path):
    print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    model.saver.restore(session, ckpt.model_checkpoint_path)
  else:
    print("Created model with fresh parameters.")
    session.run(tf.initialize_all_variables())
  return model

def prepare_wmt_data(data_dir, en_vocabulary_size, fr_vocabulary_size, tokenizer=None):
  """Get WMT data into data_dir, create vocabularies and tokenize data.

  Args:
    data_dir: directory in which the data sets will be stored.
    en_vocabulary_size: size of the English vocabulary to create and use.
    fr_vocabulary_size: size of the MRL vocabulary to create and use.
    tokenizer: a function to use to tokenize each data sentence;
      if None, basic_tokenizer will be used.

  Returns:
    A tuple of 6 elements:
      (1) path to the token-ids for English training data-set,
      (2) path to the token-ids for MRL training data-set,
      (3) path to the token-ids for English development data-set,
      (4) path to the token-ids for MRL development data-set,
      (5) path to the English vocabulary file,
      (6) path to the MRL vocabulary file.
  """
  # Get wmt data to the specified directory.
  train_path = get_nlmaptrain(data_dir)
  dev_path = get_nlmapdev(data_dir)

  # Create vocabularies of the appropriate sizes.
  fr_vocab_path = os.path.join(data_dir, "vocab%d.fr" % fr_vocabulary_size)
  en_vocab_path = os.path.join(data_dir, "vocab%d.en" % en_vocabulary_size)
  data_utils.create_vocabulary(fr_vocab_path, train_path + ".fr", fr_vocabulary_size, tokenizer,normalize_digits=False)
  data_utils.create_vocabulary(en_vocab_path, train_path + ".en", en_vocabulary_size, tokenizer,normalize_digits=False)

  # Create token ids for the training data.
  fr_train_ids_path = train_path + (".ids%d.fr" % fr_vocabulary_size)
  en_train_ids_path = train_path + (".ids%d.en" % en_vocabulary_size)
  data_utils.data_to_token_ids(train_path + ".fr", fr_train_ids_path, fr_vocab_path, tokenizer, normalize_digits=False)
  data_utils.data_to_token_ids(train_path + ".en", en_train_ids_path, en_vocab_path, tokenizer, normalize_digits=False)

  # Create token ids for the development data.
  fr_dev_ids_path = dev_path + (".ids%d.fr" % fr_vocabulary_size)
  en_dev_ids_path = dev_path + (".ids%d.en" % en_vocabulary_size)
  data_utils.data_to_token_ids(dev_path + ".fr", fr_dev_ids_path, fr_vocab_path, tokenizer, normalize_digits=False)
  data_utils.data_to_token_ids(dev_path + ".en", en_dev_ids_path, en_vocab_path, tokenizer, normalize_digits=False)

  return (en_train_ids_path, fr_train_ids_path,
          en_dev_ids_path, fr_dev_ids_path,
          en_vocab_path, fr_vocab_path)


def train():
  """Train a en->mrl translation model using WMT data."""
  # Prepare WMT data.
  print("Preparing WMT data in %s" % FLAGS.data_dir)
  en_train, fr_train, en_dev, fr_dev, _, _ = prepare_wmt_data(
      FLAGS.data_dir, FLAGS.en_vocab_size, FLAGS.fr_vocab_size)

  with tf.Session() as sess:
    # Create model.
    print("Creating %d layers of %d units." % (FLAGS.num_layers, FLAGS.size))
    model = create_model(sess, False)

    # Read data into buckets and compute their sizes.
    print ("Reading development and training data (limit: %d)."
           % FLAGS.max_train_data_size)
    dev_set = read_data(en_dev, fr_dev)
    train_set = read_data(en_train, fr_train, FLAGS.max_train_data_size)
    train_bucket_sizes = [len(train_set[b]) for b in xrange(len(_buckets))]
    train_total_size = float(sum(train_bucket_sizes))

    # A bucket scale is a list of increasing numbers from 0 to 1 that we'll use
    # to select a bucket. Length of [scale[i], scale[i+1]] is proportional to
    # the size if i-th training bucket, as used later.
    train_buckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
                           for i in xrange(len(train_bucket_sizes))]

    # This is the training loop.
    step_time, loss = 0.0, 0.0
    current_step = 0
    previous_losses = []
    while current_step < FLAGS.maxSteps+1:
      # Choose a bucket according to data distribution. We pick a random number
      # in [0, 1] and use the corresponding interval in train_buckets_scale.
      random_number_01 = np.random.random_sample()
      bucket_id = min([i for i in xrange(len(train_buckets_scale))
                       if train_buckets_scale[i] > random_number_01])

      # Get a batch and make a step.
      start_time = time.time()
      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          train_set, bucket_id)
      _, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                   target_weights, bucket_id, False)
      step_time += (time.time() - start_time) / FLAGS.steps_per_checkpoint
      loss += step_loss / FLAGS.steps_per_checkpoint
      current_step += 1

      # Once in a while, we save checkpoint, print statistics, and run evals.
      if current_step % FLAGS.steps_per_checkpoint == 0:
        # Print statistics for the previous epoch.
        perplexity = math.exp(loss) if loss < 300 else float('inf')
        print ("global step %d learning rate %.4f step-time %.2f perplexity "
               "%.2f" % (model.global_step.eval(), model.learning_rate.eval(),
                         step_time, perplexity))
        # Decrease learning rate if no improvement was seen over last 3 times.
        if len(previous_losses) > 2 and loss > max(previous_losses[-3:]):
          sess.run(model.learning_rate_decay_op)
        previous_losses.append(loss)
        # Save checkpoint and zero timer and loss.
        checkpoint_path = os.path.join(FLAGS.train_dir, "translate.ckpt")
        model.saver.save(sess, checkpoint_path, global_step=model.global_step)
        step_time, loss = 0.0, 0.0
        # Run evals on development set and print their perplexity.
        for bucket_id in xrange(len(_buckets)):
          if len(dev_set[bucket_id]) == 0:
            print("  eval: empty bucket %d" % (bucket_id))
            continue
          encoder_inputs, decoder_inputs, target_weights = model.get_batch(
              dev_set, bucket_id)
          _, eval_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                       target_weights, bucket_id, True)
          eval_ppx = math.exp(eval_loss) if eval_loss < 300 else float('inf')
          print("  eval: bucket %d perplexity %.2f" % (bucket_id, eval_ppx))
        sys.stdout.flush()

outmrlfilename = "out.txt"
def decode():
  with tf.Session() as sess:
    # Create model and load parameters.
    model = create_model(sess, True)
    model.batch_size = 1  # We decode one sentence at a time.
    mrlf = open(outmrlfilename,"w+")


    # Load vocabularies.
    en_vocab_path = os.path.join(FLAGS.data_dir,
                                 "vocab%d.en" % FLAGS.en_vocab_size)
    fr_vocab_path = os.path.join(FLAGS.data_dir,
                                 "vocab%d.fr" % FLAGS.fr_vocab_size)
    en_vocab, _ = data_utils.initialize_vocabulary(en_vocab_path)
    _, rev_fr_vocab = data_utils.initialize_vocabulary(fr_vocab_path)

    # Decode from standard input.
    #sys.stdout.write("> ")
    #sys.stdout.flush()
    #sentence = sys.stdin.readline()
    #sentence = MRL_Linearizer.stemNL(sentence)
    

    def single_sentence_decoding(sentence):
    
      # Get token-ids for the input sentence.
      token_ids = data_utils.sentence_to_token_ids(tf.compat.as_bytes(sentence), en_vocab)
      # Which bucket does it belong to?
      bucket_id = min([b for b in xrange(len(_buckets))
                       if _buckets[b][0] > len(token_ids)])
      # Get a 1-element batch to feed the sentence to the model.
      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          {bucket_id: [(token_ids, [])]}, bucket_id)
      # Get output logits for the sentence.
      _, _, output_logits = model.step(sess, encoder_inputs, decoder_inputs,
                                       target_weights, bucket_id, True)
      
      return decode_once(output_logits,rev_fr_vocab)
      

    if FLAGS.demo==False:  
      for mrl, sentence in testdataiterator():
    
      #decoding the whole test corpus

        print("translating:" +str(sentence))
        sentence = MRL_Linearizer.stemNL(sentence)
        value, counter=single_sentence_decoding(sentence)
        print ('Found at iteration: '+str(counter))
        print (value)
        #writing the translations on a file
        mrlf.write(str(counter)+"|||"+value+"|||"+Delinearizer.delinearizer(value)+"\n")
        mrlf.flush()
    else:
      sys.stdout.write("> ")
      sys.stdout.flush()
      sentence = sys.stdin.readline()
      print("translating:" +str(sentence))
      sentence = MRL_Linearizer.stemNL(sentence)
      value, counter=single_sentence_decoding(sentence)
      print ('Found at iteration: '+str(counter))
      print (value)
      print("> ", end="")
      sys.stdout.flush()
      sentence = sys.stdin.readline()

  with open("out.txt") as f:
    with open("nmtout.mrl","w+") as out:
      for line in f:
        tokens = line.split("|||")
        out.write(tokens[2].replace("$",""))
      
    
    
    
    
def process_decoding(outputs,rev_fr_vocab):
	# If there is an EOS symbol in outputs, cut them at that point.
	if data_utils.EOS_ID in outputs:
		
		outputs = outputs[:outputs.index(data_utils.EOS_ID)]
		
		
	# Get out French sentence/mrl corresponding to outputs.
	outstr = " ".join([tf.compat.as_str(rev_fr_vocab[output]) for output in outputs])
	 
	
	#check whether output is a wellformed mrl
	iswellformed = is_wellformed(outstr)
	return outstr,iswellformed
	
def decode_once(output_logits,rev_fr_vocab):
	"""
	decode one sentence until a wellformed translation is found or all nbest translations were tried
	"""
						
	f_iter = decoding_iter(output_logits)
	outputs = f_iter.__next__()
	
	
	best_outputs=[]
	for out in outputs:
	  best_outputs.append(out.tolist())
	  
	#to backtrack hypothesis we need:  
	symb=best_outputs[:int(len(best_outputs))//2] #the symbols 
	par=best_outputs[int(len(best_outputs))//2:] #and which hypothesis they came from 
	
	
	#reconstructing a single hypothesis
	def one_hyp(rank_hyp):			
	  hyp=[]
	  hyp.append(symb[-1][rank_hyp])    #appending the symbol to the right hypothesis, starting backwards
	  meta=par[-1][rank_hyp]
	  for i in range(2,len(symb)+1):
	    i=-i
	    hyp.insert(0, symb[i][meta])
	    meta=par[i][meta] 
	  return hyp
	
	iswellformed = False
	counter = 0
	#process the decoding with a single beam-search hypothesis at a time
	# in order to find a wellformed one 
	while (not iswellformed) and counter < FLAGS.beam:				
	  outstr, iswellformed = process_decoding(one_hyp(counter),rev_fr_vocab)     	
	  counter += 1
	 
	  sys.stdout.flush()
	if counter == FLAGS.beam: 
	  return "No wellformed MRL found", counter
	else:
	  return outstr , counter
#	for i in range(FLAGS.beam):
#	  #print (one_hyp(i))
#	  outstr, iswellformed = process_decoding(one_hyp(i),rev_fr_vocab)
	  
	 
#	  print(outstr)
#	  print("this mrl is wellformed: "+ str(iswellformed))
	 
#	  print("> ", end="")
#	  sys.stdout.flush()
	 # elif count==len(best_outputs):
	  #  print ("I don't know")
	    
	  #print (outstr, iswellformed)
	  
	
def decoding_iter(output_logits):
	# This is a beam-search decoder - 
	
	
	with tf.Graph().as_default():
	  beam_size = FLAGS.beam # Number of hypotheses in beam.
	  num_symbols = FLAGS.fr_vocab_size  # Output vocabulary size
	  num_steps = len(output_logits)
	  log_beam_probs, beam_symbols, beam_path = [], [], []
	  prob=[]
	  def beam_search(logit,i):
	    
	    probs=logit		#applying beam-search on the ommited sentence logits 
	    
	    if i>1:
	      probs = tf.reshape(probs + log_beam_probs[-1],[-1, beam_size * num_symbols])
	      prob.append(tf.shape(probs))
	     
	    best_probs, indices = tf.nn.top_k(probs, beam_size)
	    indices = tf.stop_gradient(tf.squeeze(tf.reshape(indices, [-1, 1])))
	    best_probs = tf.stop_gradient(tf.reshape(best_probs, [-1, 1]))
	    symbols = indices % num_symbols # Which word in vocabulary.
	    
	    beam_parent = indices // num_symbols # Which hypothesis it cames from.
	    beam_symbols.append(symbols)
	    log_beam_probs.append(best_probs)
	    beam_path.append(beam_parent)
	   
	  
	  
	  inputs = [tf.placeholder(tf.float32, shape=[None, num_symbols]) for i in range(num_steps)]
	  for i in range(len(output_logits)):
	    beam_search(inputs[i],i+1)
	  #beam_search(inputs[1], 0)
	  
	  
	  input_feed = {inputs[i]: output_logits[i][:beam_size] for i in xrange(num_steps)}
	  output_feed = beam_symbols + beam_path	#to backtrack hypothesis we need the k-best symbols and their parent hypothesis
	  session = tf.InteractiveSession()
	  outputs = session.run(output_feed, feed_dict=input_feed)
	  
	yield outputs

	
	
	
	
		



	
	
	

def self_test():
  """Test the translation model."""
  with tf.Session() as sess:
    print("Self-test for neural translation model.")
    # Create model with vocabularies of 10, 2 small buckets, 2 layers of 32.
    model = seq2seq_model.Seq2SeqModel(10, 10, [(3, 3), (6, 6)], 32, 2,
                                       5.0, 32, 0.3, 0.99, num_samples=8)
    sess.run(tf.initialize_all_variables())

    # Fake data set for both the (3, 3) and (6, 6) bucket.
    data_set = ([([1, 1], [2, 2]), ([3, 3], [4]), ([5], [6])],
                [([1, 1, 1, 1, 1], [2, 2, 2, 2, 2]), ([3, 3, 3], [5, 6])])
    for _ in xrange(5):  # Train the fake model for 5 steps.
      bucket_id = random.choice([0, 1])
      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          data_set, bucket_id)
      model.step(sess, encoder_inputs, decoder_inputs, target_weights,
                 bucket_id, False)


          


# data paths
		
mrlfilename = "../Endcorpus/train.mrl"
nlfilename = "../Endcorpus/train.nl"

tunemrlfilename = "../Endcorpus/tune.mrl"
tunenlfilename = "../Endcorpus/tune.nl"


testmrlfilename = "../Endcorpus/test.mrl"
testnlfilename = "../Endcorpus/test.nl"

#data is always fetched with these three iterators


def traindataiterator():
	"""
	iterates over traindata, yields mrl, nl
	"""
	with open(mrlfilename) as mrlfile:
		with open(nlfilename) as nlfile:
			for index,mrl in enumerate(mrlfile):
				nl = nlfile.readline()
				mrl = MRL_Linearizer.linearizeMRL(mrl)
				nl = MRL_Linearizer.stemNL(nl)
				print (nl)
				yield mrl,nl
def devdataiterator():
	"""
	iterates over devdata, yields mrl, nl
	"""
	with open(tunemrlfilename) as mrlfile:
		with open(tunenlfilename) as nlfile:
			for index,mrl in enumerate(mrlfile):
				nl = nlfile.readline()
				mrl = MRL_Linearizer.linearizeMRL(mrl)
				nl = MRL_Linearizer.stemNL(nl)
				print (nl)
				yield mrl,nl

def testdataiterator():
	"""
	iterates over testdata, yields mrl, nl
	"""
	with open(testmrlfilename) as mrlfile:
		with open(testnlfilename) as nlfile:
			for index,mrl in enumerate(mrlfile):
				nl = nlfile.readline()
				mrl = MRL_Linearizer.linearizeMRL(mrl)
				nl = MRL_Linearizer.stemNL(nl)
				print (nl)
				yield mrl,nl

def get_nlmaptrain(data_dir):
	"""
	gets training data for prepare_wmt_data 
	if you want to change the data, change traindataiterator()
	"""
	trainpath = os.path.join(data_dir, "traindata")
	os.makedirs(trainpath)
	#files have to end with .fr and .en
	with open(trainpath+".fr","w+") as mrlfile:
		with open(trainpath+ ".en","w+") as nlfile:
			for mrl,nl in traindataiterator():
				mrlfile.write(mrl+"\n")
				nlfile.write(nl+"\n")
			
	return trainpath

def get_nlmapdev(data_dir):
	"""
	gets dev data for prepare_wmt_data 
	if you want to change the data, change devdataiterator()
	"""
	devpath = os.path.join(data_dir, "devdata")
	os.makedirs(devpath)
	with open(devpath+".fr","w+") as mrlfile:
		with open(devpath+ ".en","w+") as nlfile:
			for mrl,nl in devdataiterator():
				mrlfile.write(mrl)
				nlfile.write(nl)
	return devpath

"""init cfg"""
parser = cfg.EarleyParser()
grammar_file = "../cfg/cfg.txt"
gr = cfg.Grammar(grammar_file)
parser.set_grammar(gr)


def is_wellformed(mrl):
	"""
	calls cfg checks on the given linearized mrl
	see directory ../cfg 
	"""
	#mrl = "".join(mrllist)
	print (mrl)
	try:
	  delin = Delinearizer.delinearizer(mrl)
	except IndexError:
	  print("Delinearizer failed")
	  delin = ""
	output = parser.parse_mrl(delin)
	return output
	
def main(_):
  if FLAGS.self_test:
    self_test()
  elif FLAGS.decode:
    decode()
  else:
    train()

if __name__ == "__main__":
  tf.app.run()
  print (1)
