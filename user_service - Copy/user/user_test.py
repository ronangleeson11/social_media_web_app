import unittest
import user

conn_str = "mongodb://localhost:27017/"


class TestUserMethods(unittest.TestCase):

    def test_create_user(self):
        user.connect(conn_str)
        user.reset()

        uid = user.create_user("John", "Johnspassword")
        self.assertIsNotNone(uid)
        # self.assertEqual(res.count_documents({}),0)

    def test_read_user(self):
        user.connect(conn_str)
        user.reset()

        uid = user.create_user("John", "Johnspassword")
        # print(uid)
        u = user.read_user(uid)
        # print(u)
        self.assertTrue(u.get('username') == 'John')

    def test_read_users(self):
        user.connect(conn_str)
        user.reset()

        user.create_user("Jane", "Janespass")
        user.create_user("John", "password")
        user.create_user("John2", "password")
        us = user.read_users({'password': 'password'})
        # print(list(us))
        self.assertEqual(len(list(us)), 2)

    def test_update_user_pass(self):
        user.connect(conn_str)
        user.reset()

        uid = user.create_user("Jane", "Janespass")
        user.update_user_pass('Jane', "Janesnewpass")

        u = user.read_user(uid)
        self.assertEqual(u.get('password'), "Janesnewpass")

    def test_delete_user(self):
        pass
        user.connect(conn_str)
        user.reset()

        uid = user.create_user("Jane", "Janespass")
        result = user.delete_user(uid)
        # print(result)
        u = user.read_user(uid)
        # print(u)

        self.assertIsNone(u)


if __name__ == '__main__':
    unittest.main()
