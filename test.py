from requests import get, put, post

print(get('http://127.0.0.1:8080/api/categories', json={}).json())
# new = get('http://127.0.0.1:8080/api/websites/2').json()
# params = {'help_in': [i for i in]}
# print(put('http://127.0.0.1:8080/api/users/2', params=params).json())
