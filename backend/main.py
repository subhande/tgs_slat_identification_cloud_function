
model = None
graph = None
config = None
session = None

def echo(request):
    import os
    import numpy as np

    from PIL import Image
    import io
    import base64
    # from google.cloud import storage

    from keras.models import load_model
    import cv2
    import tensorflow as tf
    from keras import backend as K
    import keras
    from flask import jsonify

    global model
    global graph
    global session
    global config
    
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    # Define IoU metric
    def mean_iou(y_true, y_pred):
        prec = []
        for t in np.arange(0.5, 1.0, 0.05):
            y_pred_ = tf.to_int32(y_pred > t)
            score, up_opt = tf.metrics.mean_iou(y_true, y_pred_, 2)
            K.get_session().run(tf.local_variables_initializer())
            with tf.control_dependencies([up_opt]):
                score = tf.identity(score)
            prec.append(score)
        return K.mean(K.stack(prec), axis=0)

    if not model:
        config = tf.ConfigProto(
                device_count = {'GPU': 0}
            )
        session = tf.Session(config=config)
        graph = tf.get_default_graph()
        keras.backend.set_session(session)
        model = load_model('./models/model_tgs_salt_1.h5', custom_objects={"mean_iou": mean_iou})
    
    
    params = request.get_json()
    image = base64.b64decode(str(params['image']).split(",")[1])
    np_img = np.frombuffer(image, np.uint8)
    X_test = []
    img = np.float32(cv2.resize(cv2.imdecode(np_img, 1), (128, 128))) / 255.0
    X_test.append(img)
    X_test =  np.asarray(X_test)
    
    
    
    with session.as_default():
        with session.graph.as_default():
            preds_test = model.predict(X_test)
            preds_test_t = (preds_test > 0.5).astype(np.uint8)
            preds = cv2.resize(preds_test_t[0] * 255, (101, 101))

    img = Image.fromarray(preds.astype('uint8'))

    rawBytes = io.BytesIO()
    img.save(rawBytes, "PNG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read())

    return (jsonify({'image':str(img_base64)}) , 200, headers)