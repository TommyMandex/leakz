#! /usr/bin/env python

import sys
import pymongo
import hashlib


def connect_database():
    secret = get_secret()
    client = pymongo.MongoClient('mongodb://localhost:27017/',
                                 username='pymongo',
                                 password=secret,
                                 authSource='hashes',
                                 authMechanism='SCRAM-SHA-1')

    return client.hashes


def get_secret():
    return load_document('../.secret')[0].strip()


def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def insert_one(collection, password_string, hash_string):
    try:
        inserted_id = collection.insert_one(
            {'password': password_string, 'hash': hash_string}).inserted_id
        print u'[I] Added {} with id: {}'.format(password_string, inserted_id)
    except (pymongo.errors.DuplicateKeyError, pymongo.errors.WriteError) as e:
        print u'[E] {}'.format(e)


def hash_password(password):
    hash_md5 = hashlib.md5(password).hexdigest()
    hash_sha1 = hashlib.sha1(password).hexdigest()
    hash_sha224 = hashlib.sha224(password).hexdigest()
    hash_sha256 = hashlib.sha256(password).hexdigest()
    hash_sha384 = hashlib.sha384(password).hexdigest()
    hash_sha512 = hashlib.sha512(password).hexdigest()
    return {'md5': hash_md5,
            'sha1': hash_sha1,
            'sha224': hash_sha224,
            'sha256': hash_sha256,
            'sha384': hash_sha384,
            'sha512': hash_sha512}


def simple_leetspeak(text):
    pattern = {'a': '4', 'A': '4', 'b': '8', 'B': '8', 'e': '3', 'E': '3', 'g': '6',
               'G': '6', 'i': '1', 'I': '1', 'o': '0', 'O': '0', 's': '5', 'S': '5',
               't': '7', 'T': '7'}

    for key, value in pattern.iteritems():
        text = text.replace(key, value)

    return text


def find_all_documents(collection):
    return collection.find({}).sort([('$natural', -1)]).batch_size(30)


def main():
    db = connect_database()
    collection = db.password

    try:
        collection.create_index("password", unique=True)
        collection.create_index("hash.md5", unique=True)
        collection.create_index("hash.sha1", unique=True)
        collection.create_index("hash.sha224", unique=True)
        collection.create_index("hash.sha256", unique=True)
        collection.create_index("hash.sha384", unique=True)
        collection.create_index("hash.sha512", unique=True)
    except pymongo.errors.OperationFailure as e:
        print e
        sys.exit(1)

    documents = find_all_documents(collection)

    for document in documents:
        password = document['password'].encode('utf-8')
        leetspeak = simple_leetspeak(password)

        if leetspeak != password:
            hash_string = hash_password(leetspeak)
            insert_one(collection, leetspeak, hash_string)


if __name__ == '__main__':
    main()