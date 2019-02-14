import time
import argparse
import socket
import numpy as np
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


# Define argparser
parser = argparse.ArgumentParser(description="Avro Kafka Generator")
parser.add_argument('--schema_registry_host', default=None, help="schema registry host")
parser.add_argument('--schema', type=str, default=None, help="schema to produce under")
parser.add_argument('--topic', type=str, default=None, help="topic to publish to")
parser.add_argument('--carbon_host', type=str, default=None, help="carbon host")
parser.add_argument('--frequency', type=float, default=1.0, help="number of message per second")

args = parser.parse_args()


def send_grafana(timestamp, value, prefix, metric, carbon_host, carbon_port=2003):
    message = "{}.{} {} {}\n".format(prefix, metric, value, timestamp)
    fmtstr = "[ Sending message to Carbon | metric: {}.{} | time: {} | value: {} ]"
    print(fmtstr.format(prefix, metric, timestamp, value))
    try:
        sock = socket.socket()
        sock.connect((carbon_host, carbon_port))
        sock.sendall(message.encode('utf-8'))
        sock.close()
    except Exception as exc:
        print("Exception sending data to Carbon", exc)


class SpikySine(object):

    def __init__(self, freq, amp, noise_level, spike_chance, x_offset, y_offset):
        self.freq = freq
        self.amp = amp
        self.noise_level = noise_level
        self.spike_chance = spike_chance
        self.x_offset = x_offset
        self.y_offset = y_offset

    def generate(self, time):
        spike = (np.random.randint(self.spike_chance) == 0)  # spike probability = 1 / spike_chance
        signal = self.amp * np.sin(2.0 * np.pi * self.freq * (float(time) - self.x_offset))
        signal += self.y_offset
        return signal + (spike * (self.noise_level * (2 * np.random.normal(0, 1) - 1)))


class Messenger(object):

    def __init__(self):
        pass

    def get_message(self, timestamp):
        pass

    def send_dashboard(self, values, carbon_host):
        pass


class AttitudeMessenger(Messenger):

    def __init__(self):
        # SpikySine params: freq, amp, noise_level, spike_chance, x_offset, y_offset
        self.phi_gen = SpikySine(0.0026, 10.0, 18.0, 50, 10, -2.0)
        self.theta_gen = SpikySine(0.009, 15.0, 22.0, 40, -35, 3.0)
        self.psi_gen = SpikySine(0.0018, 7.8, 10.0, 90, 25, 0.0)

    def get_message(self, timestamp):
        # Generate
        phi = self.phi_gen.generate(timestamp)
        theta = self.theta_gen.generate(timestamp)
        psi = self.psi_gen.generate(timestamp)
        values = [phi, theta, psi]
        # Fill the blanks of the message skeleton
        message = {"header": {"sourceSystem": "python_generator",
                              "sourceModule": "fake_source_module",
                              "time": timestamp},
                   "phi": phi,
                   "theta": theta,
                   "psi": psi}
        print("Message: {}".format(message))
        return message, values

    def send_dashboard(self, timestamp, values, carbon_host):
        for value, field_name in zip(values, ["phi", "theta", "psi"]):
                send_grafana(timestamp=timestamp,
                             value=value,
                             prefix="gen",
                             metric=field_name,
                             carbon_host=carbon_host)


def run(args, messenger):
    """Produce messages according to the specified Avro schema"""
    assert args.schema_registry_host is not None and args.schema is not None

    value_schema = avro.load(args.schema)
    conf = {'bootstrap.servers': "{}:9092".format(args.schema_registry_host),
            'schema.registry.url': "http://{}:8081".format(args.schema_registry_host)}
    avro_producer = AvroProducer(conf, default_value_schema=value_schema)

    while True:

        # Get current timestamp
        timestamp = int(time.time())

        # Assemble avro-formatted message filled with generated data
        message, values = messenger.get_message(timestamp)

        # Publish the message under the specified topic on the message bus
        # avro_producer.produce(topic=args.topic, value=message)

        if args.carbon_host is not None:
            # If a Carbon host is provided, send to Grafana dashboard
            messenger.send_dashboard(timestamp, values, args.carbon_host)

        # Flush the buffer
        avro_producer.flush()

        # Wait a second
        time.sleep(1.0 / args.frequency)


if __name__ == "__main__":
    args_ = parser.parse_args()
    if args_.topic == "hmod_Attitude":
        messenger = AttitudeMessenger()
        run(args_, messenger)
    else:
        raise NotImplementedError(("only 'hmod_Attitude' is valid as is, "
                                   "extend the 'Messenger' abstract class "
                                   "to cover additional schemas and topics!"))
