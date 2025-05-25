import os

secret = os.environ.get('DMS_CERT')
key = os.environ.get('DMS_KEY')

f = open("dms.crt", "w")
f.write(str(secret))
f.close()

f = open("dms.key", "w")
f.write(str(key))
f.close()

print(f'secret: {secret}')
print(f'key: {key}')