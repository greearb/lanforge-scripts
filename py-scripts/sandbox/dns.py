#!/usr/bin/env python3
import random
import string
import sys
from sys import exe

# List of fake website name components
prefixes = ["alpha", "beta", "omega", "nebula", "cosmo", "stellar"]
suffixes = ["web", "site", "hub", "net", "link", "zone"]


# Generate a random website name
def generate_fake_website_name():
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    random_string = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 7)))
    return f"www.{prefix}{suffix}-{random_string}.com"


# Number of website names to generate
num_names = 1000

# Generate and print random fake website names
for _ in range(num_names):
    website_name = generate_fake_website_name()
    print(website_name)
