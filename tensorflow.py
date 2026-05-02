# #to install tensorflow
# #pip install tensorflow

# #for version
# import tensorflow as tf
# print("TensorFlow version:", tf.__version__)




# mnist = tf.keras.datasets.mnist

# (x_train, y_train), (x_test, y_test) = mnist.load_data()
# x_train, x_test = x_train / 255.0, x_test / 255.0


# model = tf.keras.models.Sequential([
#   tf.keras.layers.Flatten(input_shape=(28, 28)),
#   tf.keras.layers.Dense(128, activation='relu'),
#   tf.keras.layers.Dropout(0.2),
#   tf.keras.layers.Dense(10)
# ])


# #softmax is used for probability
# predection=model(x_train[:1])
# predection
# tf.nn.softmax(predection).numpy()



'''
#import libraries
import pandas as pd
import string
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
#📝 Why?
#We need pandas for data, string/re for text, stopwords to remove common words.
df = pd.read_csv("Tweets.csv")
print(df[['text']].head())
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ''.join([i for i in text if not i.isdigit()])
    words = text.split()
    words = [w for w in words if w not in stopwords.words('english')]
    return ' '.join(words)

#Why? Lowercase = uniform text ,Remove URL = not useful
#Remove punctuation/numbers = noise ,Remove stopwords = no meaning for ML

#apply cleaning 
df['cleaned_text'] = df['text'].apply(clean_text)
print(df[['text', 'cleaned_text']].head())

df.to_csv("cleaned_tweets.csv", index=False)
#So that we can use the cleaned data for feature extraction and modeling later.
'''