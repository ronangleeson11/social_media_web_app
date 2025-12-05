import unittest
import user

conn_str = "mongodb://localhost:27017/"


class TestUserMethods(unittest.TestCase):

    def test_user_address(self):
        user.connect(conn_str)
        user.reset()

        uid = user.create_user("John", "Johnspassword")
        self.assertIsNotNone(uid)

        addr1 = {
            'line1': "123 Anywhere Rd",
            'city': 'Nowhere',
            'state': 'NH'
        }

        user.add_user_address(uid, addr1)
        user.add_user_address(uid, addr1)

        addrs = user.get_user_addresses(uid)
        # print(addrs)
        self.assertEqual(addrs[0].get('state'), 'NH')


if __name__ == '__main__':
    unittest.main()




