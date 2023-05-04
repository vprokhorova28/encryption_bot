import encryption
import nest_asyncio
from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message, ReplyKeyboardRemove, InputFile, Document
from aiogram.utils import executor

from config import TOKEN

nest_asyncio.apply()

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

button_choose = KeyboardButton('Выбрать действие')
start_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(button_choose)


@dp.message_handler(commands=['start'])
async def process_start_command(msg: Message, state: FSMContext):
    await state.reset_state()
    await bot.send_message(msg.from_user.id, "Привет!\nЯ бот, который "
                                             "помогает с шифрованием.\nНажми /help, чтобы "
                                             "посмотреть что я умею", reply_markup=start_markup)


@dp.message_handler(commands=['help'])
async def process_help_command(msg: Message):
    await bot.send_message(msg.from_user.id, "Я умею:\n- шифровать и расшифровывать текст на русском "
                                             "с помощью шифров Цезаря и Виженера\n"
                                             "- взламывать тексты (на русском), зашифрованные "
                                             "с помощью шифра Цезаря")


class ChooseAction(StatesGroup):
    action = State()


class Encryption(StatesGroup):
    action_type = State()
    cipher_type = State()
    key = State()
    input_text = State()


class Hack(StatesGroup):
    hack_input_text = State()


class Steganography(StatesGroup):
    input_file_name = State()
    encoding = State()
    input_bmp_file_name = State()
    output_bmp_file_name = State()


action_choose_markup = ReplyKeyboardMarkup(resize_keyboard=True)
action_choose_markup.insert(KeyboardButton("Зашифровать"))
action_choose_markup.insert(KeyboardButton("Расшифровать"))
action_choose_markup.insert(KeyboardButton("Взломать"))
# action_choose_markup.insert(KeyboardButton("Зашифровать в картинке"))

cipher_choose_markup = ReplyKeyboardMarkup(resize_keyboard=True)
cipher_choose_markup.insert(KeyboardButton("Шифр Цезаря"))
cipher_choose_markup.insert(KeyboardButton("Шифр Виженера"))


@dp.message_handler(Text("Выбрать действие"))
async def choose_action(msg: Message):
    await bot.send_message(msg.from_user.id, "Выберите действие⬇", reply_markup=action_choose_markup)
    # await Encryption.action_type.set()
    await ChooseAction.action.set()


@dp.message_handler(Text(["Зашифровать", "Расшифровать"]), state=ChooseAction.action)
async def action_chosen(msg: Message, state: FSMContext):
    if msg.text == "Зашифровать":
        await state.update_data(action_type="шифрования")
    elif msg.text == "Расшифровать":
        await state.update_data(action_type="расшифровки")
    await bot.send_message(msg.from_user.id, "Выберите шифр⬇", reply_markup=cipher_choose_markup)
    await Encryption.cipher_type.set()


@dp.message_handler(Text(["Шифр Цезаря", "Шифр Виженера"]), state=Encryption.cipher_type)
async def encryption_cipher_type(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(cipher_type=msg.text)
    await bot.send_message(msg.from_user.id,
                           f'Введите ключ для {data["action_type"]}:\n'
                           f'Число для шифра Цезаря\nСлово на русском для шифра Виженера',
                           reply_markup=ReplyKeyboardRemove())
    await Encryption.key.set()


@dp.message_handler(state=Encryption.key)
async def encryption_key(msg: Message, state: FSMContext):
    await state.update_data(key=msg.text)
    data = await state.get_data()
    await bot.send_message(msg.from_user.id, f'Отправьте текст для {data["action_type"]}',
                           reply_markup=ReplyKeyboardRemove())
    await Encryption.input_text.set()


@dp.message_handler(state=Encryption.input_text)
async def encryption_text(msg: Message, state: FSMContext):
    await state.update_data(input_text=msg.text)
    data = await state.get_data()
    mode = 1
    new_text = 'Ошибка'
    if data["action_type"] == "расшифровки":
        mode = -1
    if data["cipher_type"] == "Шифр Цезаря":
        if data["key"].isdigit():
            new_text = encryption.caesar_cipher(data["input_text"], shift=int(data["key"]), mode=mode)
        else:
            new_text = "Для шифра Цезаря ключ должен быть числом. Попробуйте еще раз"
    elif data["cipher_type"] == "Шифр Виженера":
        if data["key"].isalpha():
            new_text = encryption.vigener_cipher(data["input_text"], key=data["key"], mode=mode)
        else:
            new_text = "Для шифра Виженера ключ должен состоять только из русских букв. " \
                       "Попробуйте еще раз"
    if not new_text:
        new_text = 'Ошибка'
    await bot.send_message(msg.from_user.id, new_text, reply_markup=action_choose_markup)
    await ChooseAction.action.set()


@dp.message_handler(Text("Взломать"), state=ChooseAction.action)
async def action_chosen(msg: Message, state: FSMContext):
    await bot.send_message(msg.from_user.id, "Отправьте текст для взлома\n"
                                             "Текст должен быть длинным, чтобы программа смогла его взломать\n"
                                             "Обязательно должны быть использованы все русские буквы, "
                                             "за исключением может быть ё",
                           reply_markup=ReplyKeyboardRemove())
    await Hack.hack_input_text.set()


@dp.message_handler(state=Hack.hack_input_text)
async def action_chosen(msg: Message, state: FSMContext):
    await state.update_data(hack_input_text=msg.text)
    data = await state.get_data()
    new_text = encryption.decipher(data["hack_input_text"])
    await bot.send_message(msg.from_user.id, new_text,
                           reply_markup=action_choose_markup)
    await ChooseAction.action.set()


if __name__ == '__main__':
    executor.start_polling(dp)
