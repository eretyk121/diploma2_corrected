from reserv import User, TOKEN
from pprint import pprint

def vkinder(user):
    object = User(TOKEN)
    # information = user.get_info(user)
    # user_id = information['response'][0]['id']
    # friends = object.get_friends(user)
    # my_groups = object.get_groups(user)
    list_well_poeple = object.get_friens_of_friends(user)
    print(len(list_well_poeple))

    common_friends = object.find_common_friends(list_well_poeple)
    common_groups = object.find_common_groups(list_well_poeple, user)
    # list_id = [18098504, 5061261, 8232281, 228511688, 53474230, 515998263, 497652951, 2732258, 7080060, 170748077, 179025535, 3315453, 88987002, 1876621, 406139125, 306363520, 294965239, 580804664]
    sorted_list = object.sorted_people(common_friends, common_groups)
    print(len(sorted_list))
    photos = object.top_photo(sorted_list)
    print(len(photos))
    object.add_result_to_db(photos[:10])
    # print('Данные успешно записаны')
    # read = object.read_from_db()
    # print(read)

if __name__ == '__main__':
    vkinder('soldatenkov121')