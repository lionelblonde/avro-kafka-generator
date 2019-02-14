# Avro Kafka Generator

This repository proposes a solution to produce messages formatted
according to a specified [Avro](https://avro.apache.org/) schema,
publish those messages to a [Kafka](https://kafka.apache.org/) message bus,
and optionally visualize the generated content via
[Grafana](https://grafana.com) dashboards.

The user has the option to provide a
[Carbon](https://github.com/graphite-project/carbon) host
(backend for the
[Graphite](https://graphiteapp.org) metric storage solution).
If provided, the generated messages will be sent and be
available for visualisation via the associated
[Grafana](https://grafana.com) frontend.

*Disclaimer*: the repository only cover a single schema and topic, for simplicity.
The code is however extensible and expanding support to additional schemas and
topics is as easy as providing the `.avsc` file and extending the `Messenger` class.

## Notable dependency

The repository makes use of [Confluent](https://www.confluent.io)'s tool
[confluentinc/confluent-kafka-python](https://github.com/confluentinc/confluent-kafka-python).

To **install**, use `pip install confluent-kafka`.

Note that you might need to preliminarily install the `librdkafka-dev` package
with your prefered package manager associated with your distribution
(`sudo apt-get install` for Ubuntu,
`sudo brew install` for macOS,
`sudo yum install` for CentOS, etc.).

## How to

To **produce** messages following the avro schema depicted in `schemas/attitude.avsc`,
with the schema registry located and running at `127.0.0.1`,
and **publish** those messages on the message bus (Kafka) under the topic `hmod_Attitude`,
use:

```bash
python avro_producer.py --schema_registry_host=127.0.0.1 \
                        --schema=schemas/attitude.avsc \
                        --topic=hmod_Attitude \
                        --frequency=0.2
```

If you also want to visualize the generated data via a
[Grafana](https://grafana.com)
**dashboard**
underlying a [Graphite](https://graphiteapp.org) data source,
provide the
[Carbon](https://github.com/graphite-project/carbon)
host,
here colocated with Grafana and Graphite at `127.0.0.1`:

```bash
python avro_producer.py --schema_registry_host=127.0.0.1 \
                        --schema=schemas/attitude.avsc \
                        --topic=hmod_Attitude \
                        --carbon_host=127.0.0.1 \
                        --frequency=0.2
```
