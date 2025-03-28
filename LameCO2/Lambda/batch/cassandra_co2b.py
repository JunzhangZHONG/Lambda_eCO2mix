from cassandra.cluster import Cluster

clstr=Cluster(['cassandra1'])
session=clstr.connect()

create_keyspace_query = """
    CREATE KEYSPACE IF NOT EXISTS my_keyspace
    WITH replication = {
      'class': 'SimpleStrategy',
      'replication_factor': 1
    };
    """
session.execute(create_keyspace_query)
print("Keyspace 'my_keyspace' created or already exists.")

# 3. 使用该 Keyspace
session.set_keyspace('my_keyspace')

# 4. 创建表 my_table
create_table_query = """
CREATE TABLE IF NOT EXISTS batch_table (
    record_id text,
    fioul float,
    charbon float,
    gaz float,
    nucleaire float,
    eolien float,
    solaire float,
    hydraulique float,
    bioenergies float,
    total_gen float,
    renewable_gen float,
    renewable_share float,
    PRIMARY KEY (record_id)
    );
"""
session.execute(create_table_query)