# 1: Import libraries
try:
  # %tensorflow_version only exists in Colab.
  !pip install tf-nightly
except Exception:
  pass
import tensorflow as tf
import pandas as pd
from tensorflow import keras
!pip install tensorflow-datasets
import tensorflow_datasets as tfds
import numpy as np
import matplotlib.pyplot as plt

print(tf.__version__)

# 2: Get data files
!wget https://cdn.freecodecamp.org/project-data/sms/train-data.tsv
!wget https://cdn.freecodecamp.org/project-data/sms/valid-data.tsv

train_file_path = "train-data.tsv"
test_file_path = "valid-data.tsv"

# 3: Load the training and testing datasets
train_df = pd.read_csv(train_file_path, sep='\t', names=["label", "text"])
test_df = pd.read_csv(test_file_path, sep='\t', names=["label", "text"])

train_data = train_df["text"]
train_labels = train_df["label"]

test_data = test_df["text"]
test_labels = test_df["label"]

# 4: Create a Tokenizer
tokenizer = keras.preprocessing.text.Tokenizer()
tokenizer.fit_on_texts(train_data)

# 5: Convert the texts to sequences
X_train = tokenizer.texts_to_sequences(train_data)
X_test = tokenizer.texts_to_sequences(test_data)

# 6: Preprocesing: Padding the sequences to ensure uniform input size
max_length = max([len(x) for x in X_train])  # Max length of text message
X_train_pad = keras.preprocessing.sequence.pad_sequences(X_train, maxlen=max_length)
X_test_pad = keras.preprocessing.sequence.pad_sequences(X_test, maxlen=max_length)

# 7: Convert labels to numerical format: ham -> 0, spam -> 1
y_train = train_df['label'].map({'ham': 0, 'spam': 1}).values
y_test = test_df['label'].map({'ham': 0, 'spam': 1}).values

# 8: Create the neural network model
VOCAB_SIZE = 88584
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(VOCAB_SIZE, 32),
    tf.keras.layers.LSTM(32, dropout=0.3, recurrent_dropout=0.3),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(loss="binary_crossentropy",optimizer="rmsprop",metrics=['acc'])

# 9: Train model (with weights to avoid bias)
history = model.fit(X_train_pad, y_train, epochs=5, validation_split=0.2, class_weight={0: 1.0, 1: 6.5})

# 10: Test model performance
results = model.evaluate(X_test_pad, y_test)
print(results)

# 11: Function to predict messages based on model
def predict_message(pred_text):
    # Preprocess the input text
    seq = tokenizer.texts_to_sequences([pred_text])
    padded = keras.preprocessing.sequence.pad_sequences(seq, maxlen=max_length)

    # Make prediction
    prediction = model.predict(padded)[0][0]

    # Return probability and label
    label = 'ham' if prediction < 0.5 else 'spam'
    return [prediction, label]

# 12: Test predictions
def test_predictions():
  test_messages = ["how are you doing today",
                   "sale today! to stop texts call 98912460324",
                   "i dont want to go. can we try it a different day? available sat",
                   "our new mobile video service is live. just install on your phone to start watching.",
                   "you have won £1000 cash! call to claim your prize.",
                   "i'll bring it tomorrow. don't forget the milk.",
                   "wow, is your arm alright. that happened to me one time too"
                  ]

  test_answers = ["ham", "spam", "ham", "spam", "spam", "ham", "ham"]
  passed = True

  for msg, ans in zip(test_messages, test_answers):
    prediction = predict_message(msg)
    if prediction[1] != ans:
      passed = False

  if passed:
    print("You passed the challenge. Great job!")
  else:
    print("You haven't passed yet. Keep trying.")

test_predictions()
