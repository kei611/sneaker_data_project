import numpy as np
import os
import pickle
import pandas as pd

from keras.models import load_model
# from tensorflow.keras.models import load_model
# from keras.utils import CustomObjectScope
# from keras.initializers import glorot_uniform

from keras.preprocessing.image import load_img, img_to_array, array_to_img
from keras.preprocessing.sequence import pad_sequences


cur_dir = os.path.dirname(__file__)
img_cnn = load_model(os.path.join(cur_dir, 'objects', 'img_cnn.h5'))

# with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
#         img_cnn = load_model(os.path.join(cur_dir, 'objects', 'img_cnn.h5'))

pca = pickle.load(open(os.path.join(cur_dir, 'objects', 'pca.pkl'), 'rb'))
text_cnn = load_model(os.path.join(cur_dir, 'objects', 'text_cnn.h5'))
tokenizer = pickle.load(open(os.path.join(cur_dir, 'objects', 'tokenizer.pkl'), 'rb'))


def img_processing(img_name):
    hw = {'height': 128, 'width': 128}
    img = load_img(img_name, target_size = (hw['height'], hw['width']))
    array = img_to_array(img) / 255
    array = array[np.newaxis, :, :, :]
    img_features = img_cnn.predict(array)
    features_reduced = pca.transform(img_features)
    img_xception_256_df = pd.DataFrame(features_reduced)
    img_xception_256_df.columns = list('img' + str(i) for i in range(len(img_xception_256_df.columns)))
    return img_xception_256_df


def text_processing(text):
    text = text.lower().strip()
    text = pd.Series(text)
    text_tokenized = tokenizer.texts_to_sequences(text)
    maxlen = 80
    text_padded = pad_sequences(text_tokenized, maxlen=maxlen)
    text_features = text_cnn.predict(text_padded)
    text_df_256 = pd.DataFrame(text_features)
    text_df_256.columns = list('text' + str(i) for i in range(len(text_df_256.columns)))
    return text_df_256


def concat_features(retail_price, img_name, text):
    retail_price = pd.Series(retail_price)
    img_df = img_processing(img_name)
    text_df = text_processing(text)
    X = pd.concat([retail_price, img_df, text_df], axis=1)
    X = X.rename(columns={0: 'retail_price'})
    return X