import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

vk_session = vk_api.VkApi(token='ТУТ БЫЛ ТОКЕН')
session_api = vk_session.get_api()
long_poll = VkLongPoll(vk_session)


def send_some_msg(id, some_text):
    vk_session.method("messages.send", {"user_id":id, "message":some_text,"random_id":0})

def message_answer(message):
    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                msg = event.text
                id = event.user_id
                if msg == message:
                    send_some_msg(id, "Попробуй сделать что-то ещё")

message_answer("Я сделала что-то!!")