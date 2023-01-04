import logging
import telegram
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, \
    RegexHandler, ConversationHandler, CallbackQueryHandler, Filters
import config as cf
import sqlite3

TOKEN = cf.BasicInfo.token
bot = telegram.Bot(token=TOKEN)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
# updates = bot.get_updates()
updater.start_polling(timeout=123)  # Начать использовать бота
parse = cf.BasicInfo.parse_mode

MENU, RESUME_LVL_1, BASE_LVL_2, COLLECTIVE_LVL_3, CAREER_LVL_4 = range(5)

resume_exm, test_resume, sql_start, sql_questions, \
none_code_start, py_start, final_msg, personal_exp_start, \
operations_start, tech_skills_start, metrics_start, engineering_start, \
ncp1, ncp2, ncp3, ncp4, eng1, eng2, eng3, adv1,\
upg1, upg2, com1, com2, com3, com4, com5,\
rec1, rec2, rec3, rec4, rec5, rec6, rec7,\
mot1, mot2, mot3, mot4, mot5,\
tas1, tas2, tas3, tas4, tas5, = range(44)

conn = sqlite3.connect('mybase.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS mybase(telegram_id INT PRIMARY KEY,
test1_res TEXT, test2_res TEXT, test3_res TEXT, test4_res TEXT, test5_res TEXT,
 test1_ans TEXT, test2_ans TEXT, test3_ans TEXT, test4_ans TEXT, test5_ans TEXT);""")


def add_user_to_base(userid):
    conn = sqlite3.connect('mybase.db')
    cur = conn.cursor()
    info = cur.execute('SELECT * FROM mybase WHERE telegram_id=?', (int(userid),)).fetchone()
    if info is None:
        cur.execute("""INSERT INTO mybase(telegram_id) VALUES(?);""", (int(userid),))
        conn.commit()


def wait():
    sleep(1.5)


def start(update, context):
    """
    Стартовое сообщение с соо, что делает бот, и с меню кнопок для перехода к желаемому для изучения материалу.
    """
    add_user_to_base(update.message.from_user.id)

    print(f'start {update.message.from_user}')
    keyboard = cf.Start.keyboard
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard,
                                                one_time_keyboard=True,
                                                resize_keyboard=True)
    start_message = cf.Start.start_message
    start_message_2 = cf.Start.start_message_2
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=start_message, parse_mode=parse)
    wait()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             reply_markup=reply_markup,
                             text=start_message_2)
    return MENU


def resume_info(update, context):
    """ Информация по составлению резюме и выбор примера резюме или тестирования """
    print(f'Читают резюме {update.message.from_user}')
    id = update.effective_chat.id
    message_1 = cf.ResumeInfo.message_1
    message_2 = cf.ResumeInfo.message_2
    message_3 = cf.ResumeInfo.message_3
    message_4 = cf.ResumeInfo.message_4
    inl_keyboard_4 = [[telegram.InlineKeyboardButton(text="Пример резюме", callback_data=str(resume_exm)),
                       telegram.InlineKeyboardButton(text="Пройти тест", callback_data=str(test_resume))]]
    inline_markup = telegram.InlineKeyboardMarkup(inl_keyboard_4, one_time_keyboard=True, resize_keyboard=True)

    context.bot.send_message(chat_id=id, text=message_1, reply_markup=telegram.ReplyKeyboardRemove())
    wait()
    context.bot.send_photo(chat_id=id, photo=open('котик.jpg', 'rb'),
                           caption=message_2, parse_mode=parse)
    wait()
    context.bot.send_message(chat_id=id, text=message_3, parse_mode=parse)
    wait()
    context.bot.send_photo(chat_id=id, caption=message_4, photo=open('пример.jpg', 'rb'), reply_markup=inline_markup)
    return RESUME_LVL_1


def resume_example(update, context):
    print('Просматривают пример резюме')
    id = update.effective_chat.id
    update.callback_query.answer()
    context.bot.send_photo(chat_id=id, caption='', photo=open('resume_example.jpg', 'rb'),
                           reply_markup=telegram.InlineKeyboardMarkup
                           ([[telegram.InlineKeyboardButton(text='Создать своё резюме :)',
                                                            url='https://ekaterinburg.hh.ru/applicant/resumes/'
                                                                'new?hhtmFrom=main&hhtmFromLabel=header')]]))


def get_flag(userid):
    """получение для первого теста номера вопроса, равняющегося кол-ву ответов"""
    conn = sqlite3.connect('mybase.db')
    cur = conn.cursor()
    info = cur.execute('SELECT test1_ans FROM mybase WHERE telegram_id=?', (int(userid),)).fetchone()
    conn.commit()
    if info[0] is None:
        return 0
    else:
        str_info = ''.join(info)
        return len(str_info)


def put_answer(userid, update):
    """ запись ответа на одни вопрос теста 1 в базу для пользователя Т """
    conn = sqlite3.connect('mybase.db')
    cur = conn.cursor()
    info = cur.execute('SELECT test1_ans FROM mybase WHERE telegram_id=?', (int(userid),)).fetchone()
    conn.commit()
    if info[0] is None:
        answer = str(update)
    else:
        answer = ''.join(info) + str(update)
    cur.execute('UPDATE mybase SET test1_ans = ? WHERE telegram_id=?', (str(answer), int(userid),))
    conn.commit()


def get_answers(userid):
    """ считывание результатов ответов """
    conn = sqlite3.connect('mybase.db')
    cur = conn.cursor()
    info = cur.execute('SELECT test1_ans FROM mybase WHERE telegram_id=?', (int(userid),)).fetchone()
    conn.commit()
    return ''.join(info)


def clear_answers(userid):
    """очиска поля с ответами теста 1"""
    conn = sqlite3.connect('mybase.db')
    cur = conn.cursor()
    cur.execute('UPDATE mybase SET test1_ans = ? WHERE telegram_id=?', (None, int(userid),))
    conn.commit()


def save_result(userid, answers):
    """сохранение результата из поля ответов в поле результатов"""
    conn = sqlite3.connect('mybase.db')
    cur = conn.cursor()
    cur.execute('UPDATE mybase SET test1_res = ? WHERE telegram_id=?', (answers, int(userid),))
    conn.commit()


def test_lvl_1(update, context):
    print('Проходят тест')
    id = update.effective_chat.id
    if update.callback_query:
        update.callback_query.answer()
        context.bot.send_message(text='Супер! Тест состоит из 5 вопросов по теоретической части. Желаем удачи!',
                                 chat_id=id)
        clear_answers(id)
        flag = 0
    else:
        flag = get_flag(update.message.from_user.id)

    wait()

    keyboard = [['A', 'B'], ['C']]
    options = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    question_1 = cf.TestONE.question_1
    question_2 = cf.TestONE.question_2
    question_3 = cf.TestONE.question_3
    question_4 = cf.TestONE.question_4
    question_5 = cf.TestONE.question_5
    question_list = (question_1, question_2, question_3, question_4, question_5)
    while flag < 5:
        context.bot.send_message(chat_id=id, text=question_list[flag], reply_markup=options,
                                 parse_mode=parse)
        return RESUME_LVL_1
    if flag == 5:
        context.bot.send_message(chat_id=id, text=cf.TestONE.to_know_result,
                                 reply_markup=telegram.ReplyKeyboardMarkup([['Узнать результат']],
                                                                           one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return RESUME_LVL_1


def expect_answer_test_1(update, context):
    id = update.effective_chat.id
    user_answer = update.message.text
    put_answer(id, user_answer)
    return test_lvl_1(update, context)


def get_result_test_1(update, context):
    id = update.effective_chat.id
    keyboard = telegram.ReplyKeyboardMarkup([], one_time_keyboard=True, resize_keyboard=True)
    answer_pattern_list = ['A', 'B', 'A', 'C', 'B']
    wrong_answers = []
    test_1_answer_list = list(get_answers(update.message.from_user.id))

    for i in range(len(answer_pattern_list)):
        if test_1_answer_list[i] == answer_pattern_list[i]:
            continue
        else:
            wrong_answers.append(i + 1)
    print(wrong_answers)
    save_result(id, ''.join(test_1_answer_list))
    if len(wrong_answers) == 5:
        clear_answers(update.message.from_user.id)
        context.bot.send_message(chat_id=id, text=cf.TestONE.failed,
                                 reply_markup=telegram.ReplyKeyboardMarkup([cf.TestONE.try_again_btn],
                                                                           one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return BASE_LVL_2
    elif 3 <= len(wrong_answers) <= 4:
        clear_answers(update.message.from_user.id)
        context.bot.send_message(chat_id=id, text=f'{cf.TestONE.less_than_ok} {", ".join(map(str, wrong_answers))}',
                                 reply_markup=telegram.ReplyKeyboardMarkup([cf.TestONE.try_again_btn],
                                                                           one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return BASE_LVL_2
    elif 1 <= len(wrong_answers) <= 2:
        clear_answers(update.message.from_user.id)
        context.bot.send_message(chat_id=id, text=f'{cf.TestONE.ok_result} {", ".join(map(str, wrong_answers))}',
                                 reply_markup=telegram.ReplyKeyboardMarkup([cf.TestONE.try_again_btn,
                                                                            cf.TestONE.next_lvl_btn],
                                                                           one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return BASE_LVL_2
    else:
        clear_answers(update.message.from_user.id)
        context.bot.send_message(chat_id=id, text=cf.TestONE.excellent_result,
                                 reply_markup=telegram.ReplyKeyboardMarkup([cf.TestONE.next_lvl_btn],
                                                                           one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return BASE_LVL_2


def inline_former(text, call_data):
    inline = [[telegram.InlineKeyboardButton(text=text, callback_data=str(call_data))]]
    inline_markup = telegram.InlineKeyboardMarkup(inline, one_time_keyboard=True, resize_keyboard=True)
    return inline_markup


def question_base_menu(update, context):
    print(f'Читают базу вопросов {update.message.from_user}')
    mark = telegram.ReplyKeyboardMarkup(cf.QuestionBase.menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_photo(chat_id=update.effective_chat.id, caption=cf.QuestionBase.start_message,
                           photo=open('кот_вопрос.jpg', 'rb'), reply_markup=mark)
    return BASE_LVL_2


def analitics(update, context):
    mark = telegram.ReplyKeyboardMarkup(cf.Analitics.options_keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.options, reply_markup=mark)
    return BASE_LVL_2


def sql_part_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.start_SQL,
                             reply_markup=inline_former("Начинаем!", sql_start))
    return BASE_LVL_2


def sql_part(update, context):
    send_msg_with_query(update, context, 'text', None, sql_start, cf.Analitics.SQL_message_1,
                        "Отлично, дальше!", sql_questions, BASE_LVL_2)
    send_msg_with_query(update, context, 'text', None, sql_questions, cf.Analitics.SQL_message_2, None, None,
                        BASE_LVL_2)


def none_code_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.none_code_start,
                             reply_markup=inline_former("Вперёд!", none_code_start))
    return BASE_LVL_2


def none_code_part(update, context):
    send_msg_with_query(update, context, 'text', None, none_code_start,
                        cf.Analitics.none_code_message_1, "Дальше", ncp1, BASE_LVL_2)
    send_msg_with_query(update, context, 'text', None, ncp1,
                        cf.Analitics.none_code_message_2, "Дальше", ncp2, BASE_LVL_2)
    send_msg_with_query(update, context, 'text', None, ncp2,
                        cf.Analitics.none_code_message_3, "Дальше", ncp3, BASE_LVL_2)
    send_msg_with_query(update, context, 'text', None, ncp3,
                        cf.Analitics.none_code_message_4, "Дальше", ncp4, BASE_LVL_2)
    send_msg_with_query(update, context, 'text', None, ncp4, cf.Analitics.none_code_message_5, None, None, BASE_LVL_2)
    return BASE_LVL_2


def py_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.py_start,
                             reply_markup=inline_former("Вперёд!", py_start))


def py_part(update, context):
    send_msg_with_query(update, context, 'text', None, py_start, cf.Analitics.py_message_1, None, None, BASE_LVL_2)


def product_management(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.ProductManagement.product_start_msg,
                             reply_markup=telegram.ReplyKeyboardMarkup(cf.ProductManagement.product_start_menu,
                                                                       one_time_keyboard=True, resize_keyboard=True))
    return BASE_LVL_2


def personal_exp(update, context):
    base_method(update, context, cf.ProductManagement.personal_exp_start,
                cf.ProductManagement.personal_exp_msg_1, personal_exp_start, BASE_LVL_2)


def operations(update, context):
    base_method(update, context, cf.ProductManagement.operation_start,
                cf.ProductManagement.operation_msg_1, operations_start, BASE_LVL_2)


def tech_skills(update, context):
    base_method(update, context, cf.ProductManagement.tech_skills_start,
                cf.ProductManagement.tech_skills_msq_1, tech_skills_start, BASE_LVL_2)


def metrics(update, context):
    base_method(update, context, cf.ProductManagement.metrics_start,
                cf.ProductManagement.metrics_msg_1, metrics_start, BASE_LVL_2)


def engineering(update, context):
    id = update.effective_chat.id
    if update.message:
        context.bot.send_message(chat_id=id, text=cf.Engineering.engineering_start,
                                 reply_markup=inline_former("Вперёд!", engineering_start))
        return BASE_LVL_2
    send_msg_with_query(update, context, 'text', None, engineering_start, cf.Engineering.engineering_msg_1,
                        "Смотреть дальше", eng1, BASE_LVL_2)
    send_msg_with_query(update, context, 'photo', 'code_1.jpg', eng1, cf.Engineering.engineering_msg_2,
                        "Дальше", eng2, BASE_LVL_2)
    send_msg_with_query(update, context, 'text', None, eng2, cf.Engineering.engineering_msg_3,
                        "Дальше", eng3, BASE_LVL_2)
    send_msg_with_query(update, context, 'photo', 'code_2.jpg', eng3, cf.Engineering.engineering_msg_4,
                        None, None, BASE_LVL_2)


def get_opinion(update, context):
    id = update.effective_chat.id
    context.bot.send_message(chat_id=id, text=cf.GetUserOpinion.start_msg)
    return BASE_LVL_2


def base_method(update, context, text_msg_msg, text_msg_call, callback, returned_command):
    id = update.effective_chat.id
    query = update.callback_query
    if update.message:
        context.bot.send_message(chat_id=id, text=text_msg_msg, reply_markup=inline_former("Вперёд!", callback))
        return returned_command
    if query.data == str(callback):
        query.answer()
        context.bot.send_message(chat_id=id, text=text_msg_call, parse_mode=parse)
        return returned_command
    return returned_command


def send_msg_with_query(update, context, msg_type, photo_url, call_data_to_compare, text_msg,
                        call_msg, new_call_data, returned_command):
    id = update.effective_chat.id
    query = update.callback_query
    if msg_type == 'text':
        if call_msg is None and new_call_data is None and query.data == str(call_data_to_compare):
            query.answer()
            context.bot.send_message(chat_id=id, text=text_msg, parse_mode=parse)
            return returned_command
        elif query.data == str(call_data_to_compare):
            query.answer()
            context.bot.send_message(chat_id=id, text=text_msg, reply_markup=inline_former(call_msg, new_call_data),
                                     parse_mode=parse)
            return returned_command
    if msg_type == 'photo':
        if call_msg is None and new_call_data is None and query.data == str(call_data_to_compare):
            query.answer()
            context.bot.send_photo(chat_id=id, caption=text_msg, photo=open(photo_url, 'rb'), parse_mode=parse)
            return returned_command
        elif query.data == str(call_data_to_compare):
            query.answer()
            context.bot.send_photo(chat_id=id, caption=text_msg, photo=open(photo_url, 'rb'),
                                   reply_markup=inline_former(call_msg, new_call_data), parse_mode=parse)
            return returned_command


def test_lvl_2(update, context):
    mark = telegram.ReplyKeyboardMarkup([['Вернуться к меню']], one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='В разработке аналитиками, придите позже! Спасибо за понимание',
                             reply_markup=mark)
    return BASE_LVL_2


def new_collective(update, context):
    id = update.effective_chat.id
    if update.message:
        if update.message.text == 'Новый коллектив':
            context.bot.send_photo(chat_id=id, caption=cf.NewCollective.start_mes, photo=open('cats-work.jpg', 'rb'),
                                   reply_markup=telegram.ReplyKeyboardMarkup(cf.NewCollective.keyboard_options,
                                                                             one_time_keyboard=True,
                                                                             resize_keyboard=True),
                                   parse_mode=parse)
            return COLLECTIVE_LVL_3
        elif update.message.text == 'Первый день':
            context.bot.send_message(chat_id=id, text=cf.NewCollective.first_day, parse_mode=parse)
            wait()
            context.bot.send_message(chat_id=id, text=cf.NewCollective.first_day_2, parse_mode=parse)
            wait()
            context.bot.send_message(chat_id=id, text=cf.NewCollective.first_day_3, parse_mode=parse)
            return COLLECTIVE_LVL_3
        elif update.message.text == 'Советы психологов':
            context.bot.send_message(chat_id=id, text=cf.NewCollective.advices, parse_mode=parse)
            context.bot.send_message(chat_id=id, text=cf.NewCollective.advices_2,
                                     reply_markup=inline_former('Продолжить', adv1), parse_mode=parse)
            return COLLECTIVE_LVL_3
        elif update.message.text == 'Ошибки':
            context.bot.send_photo(chat_id=id, caption=cf.NewCollective.mistakes, photo=open('cat_nope.jpg', 'rb'),
                                   reply_markup=telegram.ReplyKeyboardMarkup(cf.NewCollective.keyboard_options,
                                                                             one_time_keyboard=True,
                                                                             resize_keyboard=True),
                                   parse_mode=parse)
            return COLLECTIVE_LVL_3
    elif update.callback_query:
        send_msg_with_query(update, context, 'text', None, adv1, cf.NewCollective.advices_3,
                            None, None, COLLECTIVE_LVL_3)


def career_menu(update, context):
    id = update.effective_chat.id
    if update.message.text == 'Карьерный рост' or update.message.text == 'Вернуться к меню':
        context.bot.send_message(chat_id=id, text=cf.Career.position, parse_mode=parse,
                                 reply_markup=telegram.ReplyKeyboardMarkup(cf.Career.staff_boss_choise_kboard,
                                                                           one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return CAREER_LVL_4
    elif update.message.text == 'Начальник' or update.message.text == 'Вернуться назад':
        context.bot.send_photo(chat_id=id, caption=cf.Career.boss, photo=open('cat-boss.jpg', 'rb'),
                               reply_markup=telegram.ReplyKeyboardMarkup(cf.Career.boss_kboard,
                                                                         one_time_keyboard=True,
                                                   resize_keyboard=True), parse_mode=parse)
        return CAREER_LVL_4
    elif update.message.text == 'Сотрудник':
        context.bot.send_photo(chat_id=id, caption=cf.Career.staff, photo=open('cats-work.jpg', 'rb'),
                               reply_markup=telegram.ReplyKeyboardMarkup(cf.Career.staff_kboard,
                                                                         one_time_keyboard=True,
                                                                         resize_keyboard=True), parse_mode=parse)
        return CAREER_LVL_4


def staff_line_upgrade(update, context):
    id = update.effective_chat.id
    if update.message:
        if update.message.text == 'Повышение':
            context.bot.send_message(chat_id=id, text=cf.Career.upgrade_staff_1, parse_mode=parse,
                                     reply_markup=inline_former('Продолжить', upg1))
    elif update.callback_query:
        send_msg_with_query(update, context, 'text', None, upg1, cf.Career.upgrade_staff_2,
                            'Заключение', upg2, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, upg2, cf.Career.upgrade_staff_3,
                            None, None, CAREER_LVL_4)


def boss_line(update, context):
    id = update.effective_chat.id
    if update.message.text == 'Коммуникации':
        context.bot.send_message(chat_id=id, text=cf.Career.what_to_start_with_q, parse_mode=parse,
                                 reply_markup=telegram.ReplyKeyboardMarkup(cf.Career.communication_kboard,
                                                                           one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return CAREER_LVL_4
    if update.message.text == 'Управление людьми':
        context.bot.send_message(chat_id=id, text=cf.Career.what_to_start_with_q, parse_mode=parse,
                                 reply_markup=telegram.ReplyKeyboardMarkup(cf.Career.managing_kboard,
                                                                           one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return CAREER_LVL_4

def boss_line_communication(update, context):
    id = update.effective_chat.id
    if update.message:
        context.bot.send_message(chat_id=id, text=cf.Career.boss_com_problem_1_1, parse_mode=parse)
        wait()
        context.bot.send_message(chat_id=id, text=cf.Career.boss_com_problem_1_2, parse_mode=parse,
                                 reply_markup=inline_former('Следующий пункт', com1))
        return CAREER_LVL_4
    if update.callback_query:
        send_msg_with_query(update, context, 'text', None, com1, cf.Career.boss_com_problem_2,
                            'Следующий пункт', com2, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, com2, cf.Career.boss_com_problem_3,
                            'Следующий пункт', com3, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, com3, cf.Career.boss_com_problem_4,
                            'Следующий пункт', com4, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, com4, cf.Career.boss_com_problem_5,
                            'Заключение', com5, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, com5, cf.Career.boss_com_problem_final,
                            None, None, CAREER_LVL_4)


def boss_line_recomendation(update, context):
    id = update.effective_chat.id
    if update.message:
        context.bot.send_message(chat_id=id, text=cf.Career.boss_recom_step_1, parse_mode=parse,
                                 reply_markup=inline_former('Следующий шаг', rec1))
        return CAREER_LVL_4
    if update.callback_query:
        send_msg_with_query(update, context, 'text', None, rec1, cf.Career.boss_recom_step_2,
                            'Следующий шаг', rec2, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, rec2, cf.Career.boss_recom_step_3,
                            'Следующий шаг', rec3, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, rec3, cf.Career.boss_recom_step_4,
                            'Следующий шаг', rec4, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, rec4, cf.Career.boss_recom_step_5,
                            'Следующий шаг', rec5, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, rec5, cf.Career.boss_recom_step_6,
                            'Следующий шаг', rec6, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, rec6, cf.Career.boss_recom_step_7,
                            'Заключение', rec7, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, rec7, cf.Career.boss_recom_final,
                            None, None, CAREER_LVL_4)


def boss_line_motivation(update, context):
    id = update.effective_chat.id
    if update.message:
        context.bot.send_message(chat_id=id, text=cf.Career.motivation_1, parse_mode=parse)
        wait()
        context.bot.send_message(chat_id=id, text=cf.Career.motivation_2, parse_mode=parse,
                                 reply_markup=inline_former('Следующий пункт', mot1))
        return CAREER_LVL_4
    if update.callback_query:
        send_msg_with_query(update, context, 'text', None, mot1, cf.Career.motivation_3,
                            'Следующий пункт', mot2, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, mot2, cf.Career.motivation_4,
                            'Следующий пункт', mot3, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, mot3, cf.Career.motivation_5,
                            'Следующий пункт', mot4, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, mot4, cf.Career.motivation_6,
                            'Заключение', mot5, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, mot5, cf.Career.motivation_final,
                            None, None, CAREER_LVL_4)


def boss_line_task_forming(update, context):
    id = update.effective_chat.id
    if update.message:
        context.bot.send_message(chat_id=id, text=cf.Career.task_forming, parse_mode=parse)
        wait()
        context.bot.send_message(chat_id=id, text=cf.Career.task_forming_1, parse_mode=parse,
                                 reply_markup=inline_former('Следующий шаг', tas1))
        return CAREER_LVL_4
    if update.callback_query:
        send_msg_with_query(update, context, 'text', None, tas1, cf.Career.task_forming_2,
                            'Следующий шаг', tas2, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, tas2, cf.Career.task_forming_3,
                            'Следующий шаг', tas3, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, tas3, cf.Career.task_forming_4,
                            'Следующий шаг', tas4, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, tas4, cf.Career.task_forming_5,
                            'Последний шаг', tas5, CAREER_LVL_4)
        send_msg_with_query(update, context, 'text', None, tas5, cf.Career.task_forming_6,
                            None, None, CAREER_LVL_4)


def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                MessageHandler(Filters.regex('Создать резюме'), resume_info),
                MessageHandler(Filters.regex('База вопросов на собеседование'), question_base_menu),
                MessageHandler(Filters.regex('Новый коллектив'), new_collective),
                MessageHandler(Filters.regex('Карьерный рост'), career_menu)
            ],
            RESUME_LVL_1: [
                MessageHandler(Filters.regex('B') | Filters.regex('C') | Filters.regex('A'), expect_answer_test_1),
                CallbackQueryHandler(test_lvl_1, pattern=str(test_resume)),
                MessageHandler(Filters.regex('Узнать результат'), get_result_test_1),
                CallbackQueryHandler(resume_example, pattern=str(resume_exm))
            ],
            BASE_LVL_2: [
                MessageHandler(Filters.regex('Попробовать снова'), test_lvl_1),
                MessageHandler(Filters.regex('Перейти на следующий уровень'), question_base_menu),
                MessageHandler(Filters.regex('Вернуться к меню'), question_base_menu),

                MessageHandler(Filters.regex('Аналитика'), analitics),
                MessageHandler(Filters.regex('SQL'), sql_part_start),
                CallbackQueryHandler(sql_part, pattern=str(sql_start)),
                CallbackQueryHandler(sql_part, pattern=str(sql_questions)),
                MessageHandler(Filters.regex('None-coding'), none_code_start),
                CallbackQueryHandler(none_code_part, pattern=str(none_code_start)),
                CallbackQueryHandler(none_code_part, pattern=str(ncp1)),
                CallbackQueryHandler(none_code_part, pattern=str(ncp2)),
                CallbackQueryHandler(none_code_part, pattern=str(ncp3)),
                CallbackQueryHandler(none_code_part, pattern=str(ncp4)),
                MessageHandler(Filters.regex('Python'), py_start),
                CallbackQueryHandler(py_part, pattern=str(py_start)),
                MessageHandler(Filters.regex('Product менеджмент'), product_management),
                MessageHandler(Filters.regex('Личный опыт'), personal_exp),
                CallbackQueryHandler(personal_exp, pattern=str(personal_exp_start)),
                MessageHandler(Filters.regex('Операции'), operations),
                CallbackQueryHandler(operations, pattern=str(operations_start)),
                MessageHandler(Filters.regex('Технические навыки'), tech_skills),
                CallbackQueryHandler(tech_skills, pattern=str(tech_skills_start)),
                MessageHandler(Filters.regex('Метрики'), metrics),
                CallbackQueryHandler(metrics, pattern=str(metrics_start)),
                MessageHandler(Filters.regex('Разработка'), engineering),
                CallbackQueryHandler(engineering, pattern=str(engineering_start)),
                CallbackQueryHandler(engineering, pattern=str(eng1)),
                CallbackQueryHandler(engineering, pattern=str(eng2)),
                CallbackQueryHandler(engineering, pattern=str(eng3)),

                MessageHandler(Filters.regex('Рассказать о своем опыте'), get_opinion),

                MessageHandler(Filters.regex('Пройти тест'), test_lvl_2)
            ],
            COLLECTIVE_LVL_3: [
                MessageHandler(Filters.regex('Первый день')
                               | Filters.regex('Советы психологов')
                               | Filters.regex('Ошибки'), new_collective),
                CallbackQueryHandler(new_collective, pattern=str(adv1)),
            ],
            CAREER_LVL_4: [
                MessageHandler(Filters.regex('Вернуться к меню')
                               | Filters.regex('Сотрудник')
                               | Filters.regex('Начальник')
                               | Filters.regex('Вернуться назад'), career_menu),
                MessageHandler(Filters.regex('Повышение'), staff_line_upgrade),
                CallbackQueryHandler(staff_line_upgrade, pattern=str(upg1)),
                CallbackQueryHandler(staff_line_upgrade, pattern=str(upg2)),
                MessageHandler(Filters.regex('Коммуникации')
                               | Filters.regex('Управление людьми'), boss_line),
                MessageHandler(Filters.regex('Как наладить коммуникацию?'), boss_line_communication),
                CallbackQueryHandler(boss_line_communication, pattern=str(com1)),
                CallbackQueryHandler(boss_line_communication, pattern=str(com2)),
                CallbackQueryHandler(boss_line_communication, pattern=str(com3)),
                CallbackQueryHandler(boss_line_communication, pattern=str(com4)),
                CallbackQueryHandler(boss_line_communication, pattern=str(com5)),
                MessageHandler(Filters.regex('Как себя зарекомендовать?'), boss_line_recomendation),
                CallbackQueryHandler(boss_line_recomendation, pattern=str(rec1)),
                CallbackQueryHandler(boss_line_recomendation, pattern=str(rec2)),
                CallbackQueryHandler(boss_line_recomendation, pattern=str(rec3)),
                CallbackQueryHandler(boss_line_recomendation, pattern=str(rec4)),
                CallbackQueryHandler(boss_line_recomendation, pattern=str(rec5)),
                CallbackQueryHandler(boss_line_recomendation, pattern=str(rec6)),
                CallbackQueryHandler(boss_line_recomendation, pattern=str(rec7)),
                MessageHandler(Filters.regex('Как замотивировать?'), boss_line_motivation),
                CallbackQueryHandler(boss_line_motivation, pattern=str(mot1)),
                CallbackQueryHandler(boss_line_motivation, pattern=str(mot2)),
                CallbackQueryHandler(boss_line_motivation, pattern=str(mot3)),
                CallbackQueryHandler(boss_line_motivation, pattern=str(mot4)),
                CallbackQueryHandler(boss_line_motivation, pattern=str(mot5)),
                MessageHandler(Filters.regex('Как правильно ставить задачи?'), boss_line_task_forming),
                CallbackQueryHandler(boss_line_task_forming, pattern=str(tas1)),
                CallbackQueryHandler(boss_line_task_forming, pattern=str(tas2)),
                CallbackQueryHandler(boss_line_task_forming, pattern=str(tas3)),
                CallbackQueryHandler(boss_line_task_forming, pattern=str(tas4)),
                CallbackQueryHandler(boss_line_task_forming, pattern=str(tas5))
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    dispatcher.add_handler(conv_handler)


main()
