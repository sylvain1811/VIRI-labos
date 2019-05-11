import csv

file = "firewall-policies.csv"
global policies
with open(file, 'rb') as csvfile:
    policies = csv.DictReader(csvfile)

print policies