import os
from dotenv import load_dotenv
import logging
import re
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import paramiko
import psycopg2
from psycopg2 import Error

load_dotenv()
token = os.getenv('TOKEN')
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_database = os.getenv('DB_DATABASE')
db_repl_user = os.getenv('DB_REPL_USER')
db_repl_password = os.getenv('DB_REPL_PASSWORD')
db_repl_host = os.getenv('DB_REPL_HOST')
db_repl_port = os.getenv('DB_REPL_PORT')

phone_number_output = None
email_output = None

phone_numbers_id = 0
emails_id = 0


SAVE_PHONE_NUMBER = range(1)
SAVE_EMAIL = range(1)

# Подключаем логирование
logging.basicConfig(
    filename='logfile_bot.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'
def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска почтовых ящиков: ')
    return 'find_email'
def verifyPassworCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки его на сложнонсть: ')
    return 'verify_password'

    update.message.reply_text('Введите текст для поиска почтовых ящиков: ')
    return 'get_ss'

def save_phone_number (update: Update, context):
    global phone_number_output
    global phone_numbers_id

    phone_number_output = phone_number_output.replace('\n', '')
    phone_number_output = phone_number_output.replace('. ', ';')
    parsed_output = phone_number_output.split(";")
    del parsed_output[-1]
    user_input = update.message.text
    user_input = user_input.lower()
    if str(user_input) == "да":
        connection = None
        try:
            i = 0
            connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_database)
            cursor = connection.cursor()
            while i < len(parsed_output):
                phone_numbers_id += 1
                cursor.execute(f"INSERT INTO phone_numbers (id, phone_number) VALUES (\'{phone_numbers_id}\', \'{parsed_output[i+1]}\');")
                connection.commit()
                logging.info("Команда успешно выполнена")
                i += 2
            update.message.reply_text('Информация о найденных телефонных номерах сохранена в БД')
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Произошла ошибка при попытке записи информации в БД')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
    elif user_input == "нет":
        update.message.reply_text('Информация о найденных телефонных номерах сохранена не будет')
    else:
        update.message.reply_text('Введён некорретный ответ, повторите запрос')
    return ConversationHandler.END # Завершаем работу обработчика диалога

def find_phone_number (update: Update, context):
    global phone_number_output
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'\+7[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{2}[- ]?\d{2}|8[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{2}[- ]?\d{2}')

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]};\n' # Записываем очередной номер
        
    update.message.reply_text("Найденные номера телефонов:") # Отправляем сообщение пользователю
    update.message.reply_text(phoneNumbers)
    update.message.reply_text("Сохранить найденные номера телефонов в базу данных? Ответьте \"Да\" или \"Нет\"")
    phone_number_output = phoneNumbers

    return SAVE_PHONE_NUMBER # Завершаем работу обработчика диалога

def save_email (update: Update, context):
    global email_output
    global emails_id

    email_output = email_output.replace('\n', '')
    email_output = email_output.replace('. ', ';')
    parsed_output = email_output.split(";")
    del parsed_output[-1]
    user_input = update.message.text
    user_input = user_input.lower()
    if str(user_input) == "да":
        connection = None
        try:
            i = 0
            connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_database)
            cursor = connection.cursor()
            while i < len(parsed_output):
                emails_id += 1
                cursor.execute(f"INSERT INTO emails (id, email) VALUES (\'{emails_id}\', \'{parsed_output[i+1]}\');")
                connection.commit()
                logging.info("Команда успешно выполнена")
                i += 2
            update.message.reply_text('Информация о найденных почтовых адресах сохранена в БД')
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Произошла ошибка при попытке записи информации в БД')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
    elif user_input == "нет":
        update.message.reply_text('Информация о найденных почтовых адресах сохранена не будет')
    else:
        update.message.reply_text('Введён некорретный ответ, повторите запрос')
    return ConversationHandler.END # Завершаем работу обработчика диалога

def find_email(update: Update, context):
    global email_output
    user_input = update.message.text 

    emailCheckRegex = re.compile(r'[A-Za-z0-9]+[.-_]*[A-Za-z0-9]+@[A-Za-z0-9-]+\.[A-Z|a-z]{2,}+') 

    emailCheckList = emailCheckRegex.findall(user_input) # Ищем почтовые ящики

    if not emailCheckList: # Обрабатываем случай, когда почтовых ящиков нет
        update.message.reply_text('Почтовые ящики')
        return # Завершаем выполнение функции
    
    emailCheckResult = '' # Создаем строку, в которую будем записывать почтовые ящики
    for i in range(len(emailCheckList)):
        emailCheckResult += f'{i+1}. {emailCheckList[i]};\n' # Записываем очередной почтовый ящик
        
    update.message.reply_text("Найденные почтовые адреса:")
    update.message.reply_text(emailCheckResult) # Отправляем сообщение пользователю
    update.message.reply_text("Сохранить найденные почтовые адреса в базу данных? Ответьте \"Да\" или \"Нет\"")
    email_output = emailCheckResult
    return SAVE_EMAIL # Завершаем работу обработчика диалога

def verify_password(update: Update, context):
    user_input = update.message.text # получаем пароль

    passwordStrongRegex_length = re.compile(r'.{8,}') # шаблон проверки на длину 
    passwordStrongRegex_AZ = re.compile(r'[A-Z]+') # шаблон проверки на заглавные буквы
    passwordStrongRegex_az = re.compile(r'[a-z]+') # шаблон проверки на строчные буквы
    passwordStrongRegex_09 = re.compile(r'[0-9]+') # шаблон проверки на цифры
    passwordStrongRegex_symbols = re.compile(r'[!@#$%^&\*()]+') # шаблон проверки на спецсимволы
    passwordStrong_length = passwordStrongRegex_length.search(user_input) # проверка на длину
    passwordStrong_AZ = passwordStrongRegex_AZ.search(user_input) # проверка на заглавные буквы
    passwordStrong_az = passwordStrongRegex_az.search(user_input) # проверка на строчные буквы
    passwordStrong_09 = passwordStrongRegex_09.search(user_input) # проверка на цифры
    passwordStrong_symbols = passwordStrongRegex_symbols.search(user_input) # проверка на спецсимволы

    if passwordStrong_length and passwordStrong_AZ and passwordStrong_az and passwordStrong_09 and passwordStrong_symbols: # чек истинности проверок
        update.message.reply_text("Пароль сложный")
    else:
        update.message.reply_text("Пароль простой")
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_release(update: Update, context):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('cat /etc/os-release')
    get_release_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о релизе системы: \n\n\n{get_release_info}\n\n')

def get_uname(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('uname -a')
    get_uname_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация об архитектуре процессора, имени хоста системы и версии ядра: \n\n\n{get_uname_info}\n\n')

def get_uptime(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('uptime')
    get_uptime_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'О времени работы: \n\n\n{get_uptime_info}\n\n')

def get_df(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('df -h')
    get_df_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информации о состоянии файловой системы: \n\n\n{get_df_info}\n\n')

def get_free(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('free -h')
    get_free_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о состоянии оперативной памяти: \n\n\n{get_free_info}\n\n')

def get_mpstat(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('mpstat -A')
    get_mpstat_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о производительности системы: \n\n\n{get_mpstat_info}\n\n')

def get_w(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('w')
    get_w_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о работающих в данной системе пользователях: \n\n\n{get_w_info}\n\n')

def get_auths(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('last -n 10')
    get_auths_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о последних 10 входов в систему: \n\n\n{get_auths_info}\n\n')

def get_critical(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stder = ssh.exec_command('journalctl -p crit -n 5 -q')
    get_critical_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о последних 5 критических сообщениях: \n\n\n{get_critical_info}\n\n')

def get_ps(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('ps')
    get_ps_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о запущенных процессах: \n\n\n{get_ps_info}\n\n')

def get_ss(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('ss -tu')
    get_ss_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация об используемых портах: \n\n\n{get_ss_info}\n\n')

def get_apt_list(update: Update, context: CallbackContext) -> None:
    try:
        package_name = context.args[0]
    except IndexError:
        package_name = None

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    
    if package_name:
        stdin, stdout, stderr = ssh.exec_command(f'apt list {package_name}')
    else:
        stdin, stdout, stderr = ssh.exec_command('apt list --installed')
    
    get_apt_info = stdout.read().decode('utf-8')
    ssh.close()

    if package_name:
        update.message.reply_text(f'Информация о пакете {package_name}: \n\n\n{get_apt_info}\n\n')
    else:
        if len(get_apt_info) > 4040:
            update.message.reply_text("Информация об установленных пакетах: \n\n\n")
            for x in range(0, len(get_apt_info), 4096):
                update.message.reply_text(get_apt_info[x:x+4096])
        else:
            update.message.reply_text(f"Информация об установленных пакетах: \n\n\n{get_apt_info}\n\n")
    

def get_services(update: Update, context):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('systemctl | grep running')
    get_services_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о запущенных сервисах: \n\n\n{get_services_info}\n\n')

def get_repl_logs(update: Update, context):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
#    stdin, stdout, stderr = ssh.exec_command('sudo tail -n 20 /var/log/postgresql/postgresql-15-main.log')
    stdin, stdout, sederr = ssh.exec_command('docker logs devops3-2-postgres_primary-1 |& grep replica')
    get_repl_logs_info = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Последние 20 строк журнала репликации: \n\n\n{get_repl_logs_info}\n\n')

def get_emails(update: Update, context):

    logging.basicConfig(
    filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)

    connection = None

    try:
        connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        response = " id |\t\temails\n----+--------------------------"
        for row in data:
            response = response + "\n " + str(row[0]) + "| " + str(row[1])
        update.message.reply_text(response)
        logging.info("Execute complite")
    except (Exception, Error) as error:
        logging.error("Error with working with PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def get_phone_numbers(update: Update, context):

    logging.basicConfig(filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8")

    connection = None

    try:
        connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phone_numbers;")
        data = cursor.fetchall()
        response = " id |\t\tphone_numbers\n----+--------------------------"
        for row in data:
            response = response + "\n " + str(row[0]) + "| " + str(row[1])
        update.message.reply_text(response)
        logging.info("Execute complite")
    except (Exception, Error) as error:
        logging.error("Error with working with PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def get_tables_id():
    global emails_id
    global phone_numbers_id

    logging.basicConfig(filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8")

    connection = None

    try:
        connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_database)
        email_cursor = connection.cursor()
        phone_cursor = connection.cursor()
        email_cursor.execute("SELECT * FROM emails;")
        phone_cursor.execute("SELECT * from phone_numbers")
        data = email_cursor.fetchall()
        for row in data:
            emails_id = row[0]
        data = phone_cursor.fetchall()
        for row in data:
            phone_numbers_id = row[0]
        logging.info("Execute complite")
    except (Exception, Error) as error:
        logging.error("Error with working with PostgreSQL: %s", error)
    finally:
        if connection is not None:
            phone_cursor.close()
            email_cursor.close()
            connection.close()

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(token, use_context=True)
    get_tables_id()
    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            SAVE_PHONE_NUMBER: [MessageHandler(Filters.text & ~Filters.command, save_phone_number)],
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            SAVE_EMAIL: [MessageHandler(Filters.text & ~Filters.command, save_email)],
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPassworCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
