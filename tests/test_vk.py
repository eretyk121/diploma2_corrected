import unittest
from unittest.mock import patch
from reserv import User, TOKEN
import psycopg2 as ps

class Test_Vk(unittest.TestCase):

    def setUp(self):
        self.user = User(TOKEN)
        self.target = 'soldatenkov121'
        self.list_id = [18098504, 5061261, 8232281, 228511688, 53474230, 515998263, 497652951,
                        7080060, 170748077, 179025535, 3315453, 88987002, 1876621, 406139125, 306363520, 294965239, 580804664,
                        2804766, 2056295, 337499341, 4406188, 137865023, 1876621, 4636673, 1987841,
                        1536945, 3608077, 139257921, 3239552, 406139125, 4475210, 12569844, 244967,
                        144388448, 15403227, 291862747, 2366848, 479272361, 552779320, 2732258,
                        378638550, 1477880, 51812, 8506526, 71423323, 455130366, 1350660, 5091112,
                        3688733, 5456628]

# Тест на корректность получения ID пользователя.
    def test_get_info(self):
        response = self.user.get_info('soldatenkov121')['response'][0]['id']
        self.assertTrue(response, int())

# Тест на корректность количества фотографий для пользователей
    def test_photo(self):
        response = self.user.top_photo(self.list_id)
        for photo in response:
            for key, value in photo.items():
                self.assertEqual(len(value), 3)

# Тест на корректность записи в базу и одновременно на отсеивание в методе sorted_people URL которые уже есть в базе.
    def test_write_data(self):
        with  ps.connect(dbname='studing', user='igor1', password='1234') as conn:
            with conn.cursor() as cur:
                count_before = 0
                count_after = 0
                cur.execute(f'select * from vk;')
                for row in cur:
                    count_before += 1
                list_friends = self.user.find_common_friends(self.list_id)
                list_groups = self.user.find_common_groups(self.list_id, self.target)
                sorted_list = self.user.sorted_people(list_friends, list_groups)
                list_with_photo = self.user.top_photo(sorted_list)
                write_data = self.user.add_result_to_db(list_with_photo[:10])
                cur.execute(f'select * from vk;')
                for row in cur:
                    count_after += 1
                added_rows = count_after - count_before
                self.assertEqual(added_rows, 10)