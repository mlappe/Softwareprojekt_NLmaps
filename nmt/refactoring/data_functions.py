mrlfilename = "../MRL_EN_TEST_linearized.txt"
nlfilename = "../NL_EN_TEST_stem.txt"


def prepare_wmt_data(data_dir, en_vocabulary_size, fr_vocabulary_size, tokenizer=None):
  """Get WMT data into data_dir, create vocabularies and tokenize data.

  Args:
    data_dir: directory in which the data sets will be stored.
    en_vocabulary_size: size of the English vocabulary to create and use.
    fr_vocabulary_size: size of the French vocabulary to create and use.
    tokenizer: a function to use to tokenize each data sentence;
      if None, basic_tokenizer will be used.

  Returns:
    A tuple of 6 elements:
      (1) path to the token-ids for English training data-set,
      (2) path to the token-ids for French training data-set,
      (3) path to the token-ids for English development data-set,
      (4) path to the token-ids for French development data-set,
      (5) path to the English vocabulary file,
      (6) path to the French vocabulary file.
  """
  # Get wmt data to the specified directory.
  train_path = get_nlmaptrain(data_dir)
  dev_path = get_nlmapdev(data_dir)

  # Create vocabularies of the appropriate sizes.
  fr_vocab_path = os.path.join(data_dir, "vocab%d.fr" % fr_vocabulary_size)
  en_vocab_path = os.path.join(data_dir, "vocab%d.en" % en_vocabulary_size)
  create_vocabulary(fr_vocab_path, train_path + ".fr", fr_vocabulary_size, tokenizer,normalize_digits=False)
  create_vocabulary(en_vocab_path, train_path + ".en", en_vocabulary_size, tokenizer,normalize_digits=False)

  # Create token ids for the training data.
  fr_train_ids_path = train_path + (".ids%d.fr" % fr_vocabulary_size)
  en_train_ids_path = train_path + (".ids%d.en" % en_vocabulary_size)
  data_to_token_ids(train_path + ".fr", fr_train_ids_path, fr_vocab_path, tokenizer, normalize_digits=False)
  data_to_token_ids(train_path + ".en", en_train_ids_path, en_vocab_path, tokenizer, normalize_digits=False)

  # Create token ids for the development data.
  fr_dev_ids_path = dev_path + (".ids%d.fr" % fr_vocabulary_size)
  en_dev_ids_path = dev_path + (".ids%d.en" % en_vocabulary_size)
  data_to_token_ids(dev_path + ".fr", fr_dev_ids_path, fr_vocab_path, tokenizer, normalize_digits=False)
  data_to_token_ids(dev_path + ".en", en_dev_ids_path, en_vocab_path, tokenizer, normalize_digits=False)

  return (en_train_ids_path, fr_train_ids_path,
          en_dev_ids_path, fr_dev_ids_path,
          en_vocab_path, fr_vocab_path)


def get_nlmaptrain(data_dir):
	trainpath = os.path.join(data_dir, "traindata")
	#os.makedirs(trainpath)
	#files have to end with .fr and .en
	with open(trainpath+".fr","w+") as mrlfile:
		with open(trainpath+ ".en","w+") as nlfile:
			for mrl,nl in traindataiterator():
				mrlfile.write(mrl)
				nlfile.write(nl)
			
	return trainpath

def get_nlmapdev(data_dir):
	devpath = os.path.join(data_dir, "devdata")
	#os.makedirs(devpath)
	with open(devpath+".fr","w+") as mrlfile:
		with open(devpath+ ".en","w+") as nlfile:
			for mrl,nl in devdataiterator():
				mrlfile.write(mrl)
				nlfile.write(nl)
	return devpath




def traindataiterator():
	with open(mrlfilename) as mrlfile:
		with open(nlfilename) as nlfile:
			for index,mrl in enumerate(mrlfile):
				nl = nlfile.readline()
				yield mrl,nl

def devdataiterator():
	with open(mrlfilename) as mrlfile:
		with open(nlfilename) as nlfile:
			for index,mrl in enumerate(mrlfile):
				nl = nlfile.readline()
				if index < 20:
					continue
				if index == 30:
					continue
				if isdevinstance(index):	
					yield mrl,nl
