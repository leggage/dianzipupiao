import functools
import os
import numpy as np
import tensorflow as tf
import tensorflowjs as tfjs
import tensorflow_datasets as tfds

my_file_path = r'C:\Users\leggage\Desktop\DATA\accl_data1.csv'
#CSV_COLUMNS = ['acc_data', 'res']
column_names = ['X_LOW', 'X_HIGH', 'Y_LOW', 'Y_HIGH', 'Z_LOW', 'Z_HIGH']
LABEL_COLUMN = 'res'
tf_target_folder = r'C:\Users\leggage\Desktop\tfjs_model\model1'
os.makedirs(tf_target_folder, exist_ok=True)


def get_dataset(file_path):
    dataset = tf.data.experimental.make_csv_dataset(
        file_path,
        batch_size=20,  # 为了示例更容易展示，手动设置较小的值
        # column_names=CSV_COLUMNS,
        label_name=LABEL_COLUMN,
        na_value="?",
        num_epochs=1,
        ignore_errors=True)
    return dataset


my_data = get_dataset(my_file_path)
examples, labels = next(iter(my_data))  # 第一个批次
print("EXAMPLES: \n", examples, "\n")
print("LABELS: \n", labels)
print(my_data)


def process_continuous_data(data):
    mean = 128
    # 标准化数据
    data = tf.cast(data, tf.float32) * 1 / (2 * mean)
    return tf.reshape(data, [-1, 1])


numerical_columns = [tf.feature_column.numeric_column(col, normalizer_fn=process_continuous_data) for col in column_names]
preprocessing_layer = tf.keras.layers.DenseFeatures(numerical_columns)

print("jjh")
for column in numerical_columns:
    print(column)
print("ddd")

model = tf.keras.Sequential([
    preprocessing_layer,
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid'),
])

model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy'])

model.fit(my_data, epochs=1000)

test_loss, test_accuracy = model.evaluate(my_data)

print('\n\nTest Loss {}, Test Accuracy {}'.format(test_loss, test_accuracy))
# test_data = {'acc_data': np.array([20435, 1002, 0.11])}  # 使用字典包装测试数据
# predictions = model.predict(test_data)
# print(predictions)
# 假设 model_input 是你的输入数据


#tfjs.converters.save_keras_model(model, tf_target_folder)
#model.save(tf_target_folder)