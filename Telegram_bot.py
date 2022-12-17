import logging
import telegram
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, \
    RegexHandler, ConversationHandler, CallbackQueryHandler, Filters
import config as cf

TOKEN = cf.BasicInfo.token
bot = telegram.Bot(token=TOKEN)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  level=logging.INFO)
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
#updates = bot.get_updates()
updater.start_polling(timeout=123)  # оптимальное время на случай плохого соединения

MENU, RESUME_LVL_1, QUESTION_BASE, BASE_LVL_2 = range(4)

resume_exm, test_resume, sql_start, sql_questions, \
none_code_start, py_start, final_msg, personal_exp_start, \
operations_start, tech_skills_start, metrics_start, engineering_start = range(12)


def wait():
    sleep(1.5)


def start(update, context):
    """
    Стартовое сообщение с соо, что делает бот, и с меню кнопок для перехода к желаемому для изучения материалу.
    """
    print(f'start {update.message.from_user}')
    keyboard = cf.Start.keyboard
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard,
                                                one_time_keyboard=True,
                                                resize_keyboard=True)
    start_message = cf.Start.start_message
    start_message_2 = cf.Start.start_message_2
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=start_message, parse_mode=cf.BasicInfo.parse_mode)
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
                           caption=message_2, parse_mode=cf.BasicInfo.parse_mode)
    wait()
    context.bot.send_message(chat_id=id, text=message_3, parse_mode=cf.BasicInfo.parse_mode)
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


test_1_answer_list = []
flag = 0


def test_lvl_1(update, context):
    print('Проходят тест')
    id = update.effective_chat.id
    if update.callback_query:
        update.callback_query.answer()
        context.bot.send_message(text='Супер! Тест состоит из 5 вопросов по теоретической части. Желаем удачи!',
                             chat_id= id)
    wait()
    wait()

    keyboard = [['A', 'B'],['C']]
    options =  telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    question_1 = cf.TestONE.question_1
    question_2 = cf.TestONE.question_2
    question_3 = cf.TestONE.question_3
    question_4 = cf.TestONE.question_4
    question_5 = cf.TestONE.question_5
    question_list = (question_1, question_2, question_3, question_4, question_5)
    global flag
    print(flag)
    while flag<5:
        context.bot.send_message(chat_id=id, text=question_list[flag], reply_markup=options,
                                 parse_mode=cf.BasicInfo.parse_mode)
        flag = flag + 1
        return RESUME_LVL_1
    if flag == 5:
        flag = 0
        context.bot.send_message(chat_id=id, text=cf.TestONE.to_know_result,
                                 reply_markup=telegram.ReplyKeyboardMarkup([['Узнать результат']],
                                                                           one_time_keyboard=True, resize_keyboard=True))
        return RESUME_LVL_1


def expect_answer_test_1(update, context):
    id = update.effective_chat.id
    user_answer = update.message.text
    test_1_answer_list.append(user_answer)
    return test_lvl_1(update, context)


def get_result_test_1(update, context):
    id = update.effective_chat.id
    keyboard = telegram.ReplyKeyboardMarkup([], one_time_keyboard=True, resize_keyboard=True)
    answer_pattern_list = ['A', 'B', 'A', 'C', 'B']
    wrong_answers = []
    for i in range (len(answer_pattern_list)):
        if test_1_answer_list[i] == answer_pattern_list[i]:
            continue
        else:
            wrong_answers.append(i+1)
            print(wrong_answers)
    print(wrong_answers)
    if len(wrong_answers)==5:
        context.bot.send_message(chat_id=id, text=cf.TestONE.failed,
                                 reply_markup=telegram.ReplyKeyboardMarkup([cf.TestONE.try_again_btn],
                                one_time_keyboard=True, resize_keyboard=True))
        return BASE_LVL_2
    elif 3<=len(wrong_answers)<=4:
        context.bot.send_message(chat_id=id, text=f'{cf.TestONE.less_than_ok} {", ".join(map(str, wrong_answers))}',
                                 reply_markup=telegram.ReplyKeyboardMarkup([cf.TestONE.try_again_btn],
                                one_time_keyboard=True, resize_keyboard=True))
        return BASE_LVL_2
    elif 1<=len(wrong_answers)<=2:
        context.bot.send_message(chat_id=id, text=f'{cf.TestONE.ok_result} {", ".join(map(str, wrong_answers))}',
                                 reply_markup=telegram.ReplyKeyboardMarkup([cf.TestONE.try_again_btn,
                                                                            cf.TestONE.next_lvl_btn],
                                                                            one_time_keyboard=True,
                                                                           resize_keyboard=True))
        return BASE_LVL_2
    else:
        context.bot.send_message(chat_id=id, text=cf.TestONE.excellent_result,
                                 reply_markup=telegram.ReplyKeyboardMarkup([cf.TestONE.next_lvl_btn],
                                one_time_keyboard=True, resize_keyboard=True))
        return BASE_LVL_2


def question_base_menu(update, context):
    print(f'Читают базу вопросов {update.message.from_user}')
    context.bot.send_photo(chat_id=update.effective_chat.id, caption=cf.QuestionBase.start_message,
                           photo=open('кот_вопрос.jpg', 'rb'),
                            reply_markup=telegram.ReplyKeyboardMarkup(cf.QuestionBase.menu_keyboard,
                                                                       one_time_keyboard=True, resize_keyboard=True))
    return BASE_LVL_2


def analitics(update, context):
    print(f'Аналитика, меню {update.message.from_user}')
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.options,
                             reply_markup=telegram.ReplyKeyboardMarkup(cf.Analitics.options_keyboard,
                                                                       one_time_keyboard=True, resize_keyboard=True))
    return BASE_LVL_2


def sql_part_start(update, context):
    print(f'SQL {update.message.from_user}')
    inline = [[telegram.InlineKeyboardButton(text="Начинаем!", callback_data=str(sql_start))]]
    inline_markup = telegram.InlineKeyboardMarkup(inline, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.start_SQL,
                             reply_markup=inline_markup)
    return BASE_LVL_2


def sql_part(update, context):
    id = update.effective_chat.id
    query = update.callback_query
    if query.data == str(sql_start):
        inline = [[telegram.InlineKeyboardButton(text="Отлично, дальше!", callback_data=str(sql_questions))]]
        inline_markup = telegram.InlineKeyboardMarkup(inline, one_time_keyboard=True, resize_keyboard=True)
        query.answer()
        context.bot.send_message(chat_id=id, text=cf.Analitics.SQL_message_1, reply_markup=inline_markup,
                                 parse_mode=cf.BasicInfo.parse_mode)
        return BASE_LVL_2
    if query.data == str(sql_questions):
        query.answer()
        context.bot.send_message(chat_id=id, text=cf.Analitics.SQL_message_2, parse_mode=cf.BasicInfo.parse_mode)
        return BASE_LVL_2
    return BASE_LVL_2


def none_code_start(update, context):
    print(f'None-code {update.message.from_user}')
    inline = [[telegram.InlineKeyboardButton(text="Вперёд!", callback_data=str(none_code_start))]]
    inline_markup = telegram.InlineKeyboardMarkup(inline, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.none_code_start,
                             reply_markup=inline_markup)
    return BASE_LVL_2


def none_code_part(update, context):
    update.callback_query.answer()
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.none_code_message_1,
                             parse_mode=cf.BasicInfo.parse_mode)
    wait()
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.none_code_message_2,
                             parse_mode=cf.BasicInfo.parse_mode)
    wait()
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.none_code_message_3,
                             parse_mode=cf.BasicInfo.parse_mode)
    wait()
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.none_code_message_4,
                             parse_mode=cf.BasicInfo.parse_mode)
    wait()
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.none_code_message_5,
                             parse_mode=cf.BasicInfo.parse_mode)
    return BASE_LVL_2


def py_start(update, context):
    print(f'Python {update.message.from_user}')
    inline = [[telegram.InlineKeyboardButton(text="Вперёд!", callback_data=str(py_start))]]
    inline_markup = telegram.InlineKeyboardMarkup(inline, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=cf.Analitics.py_start,
                             reply_markup=inline_markup)
    return BASE_LVL_2


def py_part(update, context):
    id = update.effective_chat.id
    query = update.callback_query
    if query.data == str(py_start):
        # inline = [[telegram.InlineKeyboardButton(text="Понятно!", callback_data=str(final_msg))]]
        # inline_markup = telegram.InlineKeyboardMarkup(inline, one_time_keyboard=True, resize_keyboard=True)
        query.answer()
        context.bot.send_message(chat_id=id, text=cf.Analitics.py_message_1,
                                  parse_mode=cf.BasicInfo.parse_mode)
        # context.bot.send_message(chat_id=id, text=cf.Analitics.py_message_1, reply_markup=inline_markup,
        #                          parse_mode=cf.BasicInfo.parse_mode)
        return BASE_LVL_2
    # if query.data == str(final_msg):
    #     query.answer()
    #     context.bot.send_message(chat_id=id, text=cf.Analitics.final_msg)
    #     return BASE_LVL_2
    return BASE_LVL_2


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
    query = update.callback_query
    inline = [[telegram.InlineKeyboardButton(text="Вперёд!", callback_data=str(engineering_start))]]
    inline_markup = telegram.InlineKeyboardMarkup(inline, one_time_keyboard=True, resize_keyboard=True)
    if update.message:
        context.bot.send_message(chat_id=id, text=cf.Engineering.engineering_start,
                                 reply_markup=inline_markup)
        return BASE_LVL_2
    if query.data == str(engineering_start):
        query.answer()
        context.bot.send_message(chat_id=id, text=cf.Engineering.engineering_msg_1,
                                 parse_mode=cf.BasicInfo.parse_mode)
        wait()
        context.bot.send_photo(chat_id=id, caption=cf.Engineering.engineering_msg_2, photo=open('code_1.jpg', 'rb'),
                                 parse_mode=cf.BasicInfo.parse_mode)
        wait()
        context.bot.send_message(chat_id=id, text=cf.Engineering.engineering_msg_3,
                                 parse_mode=cf.BasicInfo.parse_mode)
        wait()
        context.bot.send_photo(chat_id=id, caption=cf.Engineering.engineering_msg_4, photo=open('code_2.jpg', 'rb'),
                               parse_mode=cf.BasicInfo.parse_mode)
        return BASE_LVL_2
    return BASE_LVL_2


def base_method(update, context, text_msg_msg, text_msg_call, callback, returned_command):
    id = update.effective_chat.id
    query = update.callback_query
    inline = [[telegram.InlineKeyboardButton(text="Вперёд!", callback_data=str(callback))]]
    inline_markup = telegram.InlineKeyboardMarkup(inline, one_time_keyboard=True, resize_keyboard=True)
    if update.message:
        context.bot.send_message(chat_id=id, text=text_msg_msg,
                                 reply_markup=inline_markup)
        return returned_command
    if query.data == str(callback):
        query.answer()
        context.bot.send_message(chat_id=id, text=text_msg_call,
                                 parse_mode=cf.BasicInfo.parse_mode)
        return returned_command
    return returned_command


def test_lvl_2(update, context):
    mark = telegram.ReplyKeyboardMarkup([['Вернуться к меню']], one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='В разработке, придите позже! Спасибо за понимание',
                             reply_markup=mark)
    return BASE_LVL_2


def main():

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                MessageHandler(Filters.regex('Создать резюме'), resume_info),
                MessageHandler(Filters.regex('База вопросов на собеседование'), question_base_menu)
            ],
            RESUME_LVL_1: [
                MessageHandler(Filters.regex('B') | Filters.regex('C') | Filters.regex('A'), expect_answer_test_1),
                CallbackQueryHandler(test_lvl_1, pattern=str(test_resume)),
                MessageHandler(Filters.regex('Узнать результат'), get_result_test_1),
                CallbackQueryHandler(resume_example, pattern=str(resume_exm))
            ],
            BASE_LVL_2: [
                MessageHandler(Filters.regex('Попробовать снова'), test_lvl_1),
                MessageHandler(Filters.regex('Аналитика'), analitics),
                MessageHandler(Filters.regex('Перейти на следующий уровень'), question_base_menu),
                MessageHandler(Filters.regex('SQL'), sql_part_start),
                MessageHandler(Filters.regex('None-coding'), none_code_start),
                MessageHandler(Filters.regex('Python'), py_start),
                MessageHandler(Filters.regex('Вернуться к меню'), question_base_menu),
                CallbackQueryHandler(sql_part, pattern=str(sql_start)),
                CallbackQueryHandler(sql_part, pattern=str(sql_questions)),
                CallbackQueryHandler(none_code_part, pattern=str(none_code_start)),
                CallbackQueryHandler(py_part, pattern=str(py_start)),
                MessageHandler(Filters.regex('Product менеджмент'), product_management),
                MessageHandler(Filters.regex('Личный опыт'), personal_exp),
                MessageHandler(Filters.regex('Операции'), operations),
                MessageHandler(Filters.regex('Технические навыки'), tech_skills),
                MessageHandler(Filters.regex('Метрики'), metrics),
                CallbackQueryHandler(personal_exp, pattern=str(personal_exp_start)),
                CallbackQueryHandler(operations, pattern=str(operations_start)),
                CallbackQueryHandler(tech_skills, pattern=str(tech_skills_start)),
                CallbackQueryHandler(metrics, pattern=str(metrics_start)),
                MessageHandler(Filters.regex('Разработка'), engineering),
                CallbackQueryHandler(engineering, pattern=str(engineering_start)),
                MessageHandler(Filters.regex('Пройти тест'), test_lvl_2)
                #CallbackQueryHandler(py_part, pattern=str(final_msg))
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    dispatcher.add_handler(conv_handler)

main()
