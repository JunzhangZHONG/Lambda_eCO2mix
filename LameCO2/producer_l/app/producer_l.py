import json
import time
import urllib.request
import json
from datetime import datetime
from kafka import KafkaProducer, KafkaClient 
from kafka.admin import KafkaAdminClient, NewTopic

def parse_value(val):
    """
    Turn value to float
    """
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def main():
    """_summary_
    
    Returns:
        _type_: _description_
    """    
    url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?limit=20&refine=nature%3A%22Donn%C3%A9es%20temps%20r%C3%A9el%22"

    # topic = sys.argv[1]
    topic = 'eCO2mix'
    
    kafka_bootstrap = 'kafka:29092'
    
    kafka_client = KafkaClient(bootstrap_servers=kafka_bootstrap)
    
    admin = KafkaAdminClient(bootstrap_servers=kafka_bootstrap)
    
    if topic not in admin.list_topics():
        try:
            admin.create_topics([NewTopic(name=topic, num_partitions=1, replication_factor=1)])
            print("Topic created:", topic)
        except Exception as e:
            print("Error creating topic:", e)
            
    producer = KafkaProducer(bootstrap_servers=kafka_bootstrap)
    
    while True:
        try:
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())

            # 重点：拿到 "results" 数组
            results = data.get("results", [])
            print(f"Fetched {len(results)} items")

            for item in results:
                # 过滤后仅提取所需8个参数
                filtered_item = {
                    "fioul": parse_value(item.get("fioul")),
                    "charbon": parse_value(item.get("charbon")),
                    "gaz": parse_value(item.get("gaz")),
                    "nucleaire": parse_value(item.get("nucleaire")),
                    "eolien": parse_value(item.get("eolien")),
                    "solaire": parse_value(item.get("solaire")),
                    "hydraulique": parse_value(item.get("hydraulique")),
                    "bioenergies": parse_value(item.get("bioenergies"))
                }
                # 将过滤后的数据发送到 Kafka
                producer.send(topic, json.dumps(filtered_item).encode())

            print(f"{datetime.now()} Produced {len(filtered_item)} filtered records")
            print(filtered_item)
        except Exception as e:
            print("Error:", e)

        time.sleep(900)
        

if __name__ == "__main__":
    main()
