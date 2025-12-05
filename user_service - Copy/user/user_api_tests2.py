import unittest
import json

import requests
user_url = 'https://cs518userserviceronang.azurewebsites.net/api/user/'
# user_url = "http://localhost:7071/api/user/"
func_key = 't8J6d5Q6_j_DhBCwq42BktPCNljBEkEPCaAYP3STDz2DAzFuLOlooA=='
# func_key = None

class TestUserMethods(unittest.TestCase):

    def test_GET_user_user_and_pass(self):
        res = requests.post(user_url, json={
            'username': 'wasd',
            'password': 'dsaw'},
                            headers={'x-functions-key': func_key})
        print(res.status_code, res.text)
        self.assertEqual(res.status_code, 200)
        _id = res.text
        username = "wasd"
        password = "dsaw"
        res = requests.get(user_url, params = {"username": username, "password": password, "code": func_key})

        print(res.status_code, res.text)
        self.assertEqual(res.status_code,200)
        _id = res.text
        #
        # res = requests.delete(user_url+_id, headers={'x-functions-key': func_key})
        # print(res.status_code, res.text)
        # self.assertEqual(res.status_code,200)

if __name__ == '__main__':
    unittest.main()
