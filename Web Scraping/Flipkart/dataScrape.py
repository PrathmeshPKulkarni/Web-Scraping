import requests

# Making a GET request
r = requests.get('https://www.geeksforgeeks.org/python-programming-language/')

# print request object
print(r.url)

# print status code
print(r.status_code)
