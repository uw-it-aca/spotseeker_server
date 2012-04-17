import hashlib
import time
import random
from oauth_provider.models import Consumer

consumer_name = raw_input('Enter consumer name: ')

key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)

print "Key: ", key
print "Secret: ", secret

