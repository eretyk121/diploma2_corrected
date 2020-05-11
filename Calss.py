import time
import requests
from pprint import pprint
import pandas as pd
import psycopg2 as ps

ID = 'soldatenkov121'
TOKEN = '63bd9b357f079b30e4ea43a61b75cf79a83479878af900188b02bae5fec5177ee4d4e142b8e73d9312a34'

class User:
    def __init__(self, token):
        self.token = token

# Получаю стандартные параметры
    def get_params(self):
        return dict(
            access_token=self.token,
            v='5.52'
        )

# получаю информацию о ключевом пользователе
    def get_info(self, new_id):
        params = self.get_params()
        params['user_ids'] = new_id
        params['fields'] = 'id, first_name, last_name, city, interests, ' \
                           'movies, relation, sex, bdate'
        response = requests.get(
            'https://api.vk.com/method/users.get',
            params
        )
        resp_json = response.json()
        return resp_json

# Преобразование топ-10 пользователей в список с лучшими фото
    def top_photo(self, ids):
        params = self.get_params()
        result_list = []
        for id in ids:
            params['owner_id'] = id
            params['album_id'] = 'profile'
            params['extended'] = 1
            response = requests.get(
                'https://api.vk.com/method/photos.get',
                params
            )
            time.sleep(0.2)
            resp_json = response.json()
            list_top_photos = []
            urls_list = []
            try:
                for one in resp_json['response']['items']:
                    list_top_photos.append({'id': one['id'], 'likes': one['likes']['count']})
                df = pd.DataFrame(list_top_photos)
                list_top3 = df.sort_values(['likes'], ascending=False).head(3)['id'].values.tolist()
                for photo in list_top3:
                    photo = f'https://vk.com/id{id}?z=photo{id}_{photo}%2Falbum{id}_0%2Frev'
                    urls_list.append(photo)
                if len(urls_list) < 3:
                    continue
                else:
                    result_list.append({f'https://vk.com/id{id}': urls_list})
            except:
                pass
        # with open('test.json', 'w', encoding='utf-8') as text:
        #     json.dump(result_list, text)
        return result_list

# Получаю список групп ключевого пользователя
    def get_groups(self, user):
        params = self.get_params()
        params['user_id'] = user
        response = requests.get(
            'https://api.vk.com/method/groups.get',
            params
        )
        time.sleep(0.3)
        groups_id = response.json()['response']['items']
        return groups_id

# список друзей ключевого пользователя
    def get_friends(self, user):
        friends_list = []
        params = self.get_params()
        params['user_id'] = self.get_info(user)['response'][0]['id']
        # params['fields'] = 'sex, bdate, city'
        response = requests.get('https://api.vk.com/method/friends.get', params)
        resp_json = response.json()
        # print(resp_json)
        friends_list = resp_json['response']['items']
        return friends_list

# поиск количества общих групп со списком людей подходящих под основне условия
    def find_common_groups(self, list_people, user):
        list_people_with_common_groups = []
        user_id = self.get_info(user)['response'][0]['id']
        my_groups = self.get_groups(user_id)
        for men in list_people:
            list_groups = []
            men_groups = self.get_groups(men)
            for group in men_groups:
                if group in my_groups:
                    list_groups.append(group)
            list_people_with_common_groups.append([{'id': men}, {'group_count': len(list_groups)}])
        return list_people_with_common_groups

# поиск количества общих друзей с людьми подходящими под основные условия
    def find_common_friends(self, list_people):
        list_common_friends = []
        code_list = []
        params = self.get_params()
        i = 0
        while i < len(list_people):
            for one in list_people[i:i + 24]:
                code_list.append('API.users.get({"user_id":"' + str(one) + '", "fields": "common_count"})')
            string_code = str(code_list).replace("'", "")
            code = f'return {string_code}'
            response = requests.get('https://api.vk.com/method/execute?code=' + code + ';', params)
            resp_json = response.json()
            for user in resp_json['response']:
                list_common_friends.append([{'id': user[0]['id']}, {'count': user[0]['common_count']}])
            code_list.clear()
            if i > (len(list_people) - 24):
                i = i + (len(list_people) - i)
            else:
                i = i + 24
        return list_common_friends

# Поиск людей в друзьях друзей пользователя
    def get_friens_of_friends(self, user_login):
        list_of_friends_of_friends = []
        code_list = []
        user_id = self.get_info(user_login)['response'][0]['id']
        my_friends = self.get_friends(user_id)
        params = self.get_params()
        gender = self.get_info(user_login)['response'][0]['sex']
        city_id = self.get_info(user_login)['response'][0]['city']['id']
        bdate = int(self.get_info(user_login)['response'][0]['bdate'].split('.')[2])
        search_quantity = 0
        if len(my_friends) < 50:
            search_quantity = 300
        elif 50 < len(my_friends) < 100:
            search_quantity = 200
        elif 100 < len(my_friends) < 200:
            search_quantity = 100
        elif len(my_friends) > 200:
            search_quantity = 80
        print(search_quantity)
        i = 0
        while i < len(my_friends):
            for one in my_friends[i:i+24]:
                code_list.append('API.friends.get({"user_id":"'+str(one)+'", "count": '+str(search_quantity)+','
                                    ' "order": "random","fields": "sex, bdate, city, relation"})')
            string_code = str(code_list).replace("'", "")
            code = f'return {string_code}'
            response = requests.get('https://api.vk.com/method/execute?code=' + code + ';', params)
            resp_json = response.json()

            # Отсеивание людей по основным признакам
            try:
                for users in resp_json.values():
                    for user in users:
                        for one in user['items']:
                            if one['sex'] == gender or 'relation' not in one.keys():
                                continue
                            if one['relation'] not in [0, 1, 6] or 'city' not in one.keys():
                                continue
                            one_city = 'city' in one.keys() and one['city']['id']
                            one_bdate = 'bdate' in one.keys() and int(one['bdate'].split('.')[-1])

                            if not ((one_city == city_id) and one_bdate in range(bdate - 5, bdate + 5)):
                                continue
                            list_of_friends_of_friends.append(one['id'])
            except TypeError:
                pass    # насколько я понимаю, здесь есть люди у которых список друзей закрыт и user['item'] #
                            # выдает False. Для этого except TypeError.#
            code_list.clear()
            if i > (len(my_friends) - 24):
                i = i + (len(my_friends) - i)
            else:
                i = i + 24
            result = [x for n, x in enumerate(list_of_friends_of_friends) if x not in list_of_friends_of_friends[n + 1:]]
        return result

# сортировка результатов выборки по друзьям и группам
    def sorted_people(self, list_friends, list_groups):
        res_list = []
        res_group = []
        for one in list_friends:
            # print(one[0]['count'])
            res_list.append({'id': one[0]['id'], 'count': one[1]['count']})
        for one in list_groups:
            # print(one[0]['count'])
            res_group.append({'id': one[0]['id'], 'group_count': one[1]['group_count']})
        # print(res_group)
        df_1 = pd.DataFrame(res_group)
        df = pd.DataFrame(res_list)
        df_2 = pd.merge(df, df_1, how='inner', on='id')
        sorted_df = df_2.sort_values(by=['count', 'group_count'], ascending=False)
        sorted_list = sorted_df['id'].values.tolist()
        new_list = []

        # Проверка наличия URL в базе данных (защита от дублирования)
        for one in sorted_list:
            url = f'https://vk.com/id{one}'
            with ps.connect(dbname='studing', user='igor1', password='1234') as conn:
                with conn.cursor() as cur:
                    cur.execute(f"select * from vk where user_page = '{url}';")
                    result = cur.fetchall()
                    if not result:
                        new_list.append(one)
        return new_list

# запись результата в BD
    def add_result_to_db(self, list_with_photos):
        for one in list_with_photos:
            for key, value in one.items():
                with  ps.connect(dbname='studing', user='igor1', password='1234') as conn:
                    with conn.cursor() as cur:
                        cur.execute(f"insert into vk values(%s, %s, %s, %s);", (key, value[0], value[1], value[2]))

# чтение из BD
    def read_from_db(self):
        with  ps.connect(dbname='studing', user='igor1', password='1234') as conn:
            with conn.cursor() as cur:
                i = 0
                cur.execute(f'select * from vk;')
                for row in cur:
                    print(row)
                    i += 1
                print(f'Количество записей - {i}')




# if __name__ == '__main__':
#     user = User(TOKEN)
#     information = user.get_info('soldatenkov121')
#     user_id = information['response'][0]['id']
#     # print(len(information))
#     friends = user.get_friends(user_id)
#     # my_groups = user.get_groups(user_id)
#     list_well_poeple = user.get_friens_of_friends(user_id)
#     print(list_well_poeple)
    # common_friends = user.find_common_friends(list_well_poeple)
    # common_groups = user.find_common_groups(list_well_poeple)
    # sorted_list = user.sorted_people(common_friends, common_groups)
    # # list_id = [18098504, 5061261, 8232281, 228511688, 53474230, 515998263, 497652951, 2732258, 7080060, 170748077, 179025535, 3315453, 88987002, 1876621, 406139125, 306363520, 294965239, 580804664]
    # photos = user.top_photo(sorted_list)
    # user.add_result_to_db(photos)
