#這是監控的
from kafka import KafkaProducer, KafkaConsumer
# 建立消費者
consumer = KafkaConsumer('0523', bootstrap_servers='localhost:9092', group_id='my_group')

# 消費訊息
for message in consumer:
    print(f"Received message: {message.value.decode('utf-8')}")

# 關閉消费者
consumer.close()