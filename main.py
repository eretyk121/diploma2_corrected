from Class import User, TOKEN

def vkinder():
    user = input('Введите никнэйм или id пользователя: ')
    object = User(TOKEN)
    list_well_poeple = object.get_friens_of_friends(user)
    print(f'Количество людей подходящих по обязательным параметрам {len(list_well_poeple)}')
    common_friends = object.find_common_friends(list_well_poeple)
    common_groups = object.find_common_groups(list_well_poeple, user)
    common_interests = object.get_interests_of_people(user, list_well_poeple)
    sorted_list = object.sorted_people(common_friends, common_groups, common_interests)
    print(f'Количество людей после проверки на дубли {len(sorted_list)}')
    photos = object.top_photo(sorted_list)
    print(f'Количество людей с доступными фотографиями {len(photos)}')
    object.add_result_to_db(photos[:10])
    print('Данные успешно записаны')
    object.read_from_db()
    
if __name__ == '__main__':
    vkinder()
