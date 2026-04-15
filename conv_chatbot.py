import json
import nltk
import random
import pickle
import tflearn
import numpy as np 
import tensorflow as tf
import os
from nltk.stem.lancaster import LancasterStemmer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

#Initializing Lancaster Stemmer
stemmer = LancasterStemmer()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

#Loading dataset
dataset_path = os.path.join(script_dir, 'dataset', 'dataset.json')
with open(dataset_path) as file:
	data = json.load(file)

pickle_path = os.path.join(script_dir, 'data.pickle')
with open(pickle_path, 'rb') as f:
    words, labels, train,  output = pickle.load(f)


#Building network
net = tflearn.input_data(shape = [None, len(train[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation = 'softmax')
net = tflearn.regression(net)

model = tflearn.DNN(net)

#Loading Model
model_path = os.path.join(script_dir, 'models', 'chatbot-model.tflearn')
model.load(model_path)


def bag_of_words(s, words):

	bag = [0 for _ in range(len(words))]

	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]

	for se in s_words:
		for i, w in enumerate(words):
			if(w == se):
				bag[i] = 1

	return np.array(bag)


def chat(inputText):

	print('[INFO] Start talking...(type quit to exit)')
	
	while True:

		inp = inputText

		#Type quit to exit
		if inp.lower() == 'quit':
			break

		#Predicting input sentence tag
		predict = model.predict([bag_of_words(inp, words)])
		predictions = np.argmax(predict)
		
		tag = labels[predictions]
		#Printing response
		for t in data['intents']:
			#print(t['tag'])
			if t['tag'] == tag:
				responses = t['responses']
				
		outputText = random.choice(responses)		
		return outputText
