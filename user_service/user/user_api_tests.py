import unittest
import json

import requests
points = 0
user_url = 'https://cs518userserviceronang.azurewebsites.net/api/user/'
# user_url = "http://localhost:7071/api/user/"
func_key = 't8J6d5Q6_j_DhBCwq42BktPCNljBEkEPCaAYP3STDz2DAzFuLOlooA=='

class TestUserMethods(unittest.TestCase):

    def test_CRUD_user(self):

        global points

        res = requests.post(user_url,json={
            'username':'dave2',
            'password':'evad'},
            headers={'x-functions-key': func_key})
        print(res.status_code, res.text)
        self.assertEqual(res.status_code,200)
        _id = res.text

        points += 1

        res = requests.put(user_url+_id,json={
            "password":'vade'},
            headers={'x-functions-key': func_key})
        print(res.status_code,res.text)
        self.assertEqual(res.status_code,200)

        points += 1

        res = requests.get(user_url+_id, headers={'x-functions-key': func_key})
        print(res.status_code, res.text)
        u = json.loads(res.text)
        self.assertEqual(u.get('password'),'vade')
        _id = u.get('_id').get('$oid')

        points += 1

        res = requests.delete(user_url+_id, headers={'x-functions-key': func_key})
        print(res.status_code, res.text)
        self.assertEqual(res.status_code,200)

        points += 1;

        res = requests.get(user_url + _id,
                           headers={'x-functions-key': func_key})
        print(res.status_code, res.text)
        self.assertEqual(res.status_code, 404)

        points += 1


if __name__ == '__main__':
    unittest.main()
