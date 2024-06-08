import numpy as np
from PIL import Image
import tensorflow
from tensorflow import keras
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity

def initialize_model():
    vgg16 = VGG16(weights='imagenet', include_top=False, pooling='max', input_shape=(224, 224, 3))
    for model_layer in vgg16.layers:
        model_layer.trainable = False
    return vgg16

def load_image(image_path):
    input_image = Image.open(image_path)
    resized_image = input_image.resize((224, 224))
    return resized_image

def get_image_embeddings(model, object_image):
    image_array = np.expand_dims(image.img_to_array(object_image), axis=0)
    image_embedding = model.predict(image_array)
    return image_embedding

def get_similarity_score(model, first_image_path, second_image_path):
    first_image = load_image(first_image_path)
    second_image = load_image(second_image_path)
    
    first_image_vector = get_image_embeddings(model, first_image)
    second_image_vector = get_image_embeddings(model, second_image)
    
    similarity_score = cosine_similarity(first_image_vector, second_image_vector).reshape(1,)
    
    return similarity_score

def compare_images(image1, image2):
    model = initialize_model()
    similarity_score = get_similarity_score(model, image1, image2)
    similarity_score = similarity_score * 100
    if similarity_score[0] > 95:
        print("Similar")
    else:
        print("No Similarity")
    print(similarity_score[0])

# Example usage
image1 = 'sun.jpg'
image2 = 'nissan-gt-r.webp'

compare_images(image1, image2)

