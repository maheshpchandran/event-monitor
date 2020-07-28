#!/usr/bin/env python

import boto
import codecs
import json
import sys
from time import sleep
kinesis = boto.connect_kinesis()

def main(kinesis_stream_name, json_filename, repeats):
    for i in range (repeats):
      with open(json_filename) as f:
        data = json.load(f)
        string_payload = json.dumps(data)
        sleep(1)
        print("Payload to kinesis: {0}".format(string_payload))
        print("Response from kinesis: {0}".format(
            str(kinesis.put_record(kinesis_stream_name, string_payload, '0'))))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Missing arguments"
        print __doc__
        sys.exit(-1)
    if len(sys.argv) > 4:
        print "Extra arguments"
        print __doc__
        sys.exit(-1)
    try:
        json_filename = sys.argv[1]
        kinesis_stream_name = sys.argv[2]
        if len(sys.argv) == 4:
            repeats = int(sys.argv[3])
        else:
            repeats = 10
        main(kinesis_stream_name, json_filename, repeats)

    except Exception as e:
        print __doc__
        raise e
