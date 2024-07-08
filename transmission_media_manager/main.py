import telebot

from transmission_media_manager.settings import settings
from transmission_media_manager.torrent import MediaType, Media, add_torrent

bot = telebot.TeleBot(settings.telegram_api_token)

NOT_TORRENT_MESSAGE = '{filename} не .торрент файл!'

MEDIA_TYPE_KEYBOARD = telebot.types.InlineKeyboardMarkup()
for media_type in MediaType:
    MEDIA_TYPE_KEYBOARD.add(
        telebot.types.InlineKeyboardButton(
            text=media_type.value,
            callback_data=media_type.value,
        )
    )

WHICH_STORAGE_KEYBOARD = telebot.types.InlineKeyboardMarkup()
WHICH_STORAGE_KEYBOARD.add(
    telebot.types.InlineKeyboardButton(
        text='Личное',
        callback_data='personal',
    )
)
WHICH_STORAGE_KEYBOARD.add(
    telebot.types.InlineKeyboardButton(
        text='Общее',
        callback_data='general',
    )
)

SaveInfo = dict[str, str]


def get_media_path(save_info: SaveInfo, username: str) -> str:
    if save_info['store'] == 'general':
        username = 'all'
    else:
        username = settings.name_mapping[username]
    media = Media(username)
    return media.get_media_path(MediaType(save_info['media_type']))


def extract_save_info(message_text: str) -> SaveInfo:
    media_type_data = message_text.split('\n\n')[1]
    return dict(
        (value.split(':')[0].strip(), value.split(':')[1].strip())
        for value in media_type_data.split('\n')
    )


@bot.message_handler(content_types=['document'])
def handle_torrent_file(message: telebot.types.Message):
    if message.chat.username not in settings.users:
        bot.send_message(message.chat.id, 'access_denied')
        return
    if not message.document.file_name.endswith('.torrent'):
        bot.reply_to(message, NOT_TORRENT_MESSAGE.format(
            filename=message.document.file_name
        ))
        return

    bot.send_message(
        message.chat.id,
        f'Добавление нового файла\n\nfile_id: {message.document.file_id}',
        reply_markup=MEDIA_TYPE_KEYBOARD,
    )


@bot.callback_query_handler(func=lambda call: call.data in MediaType.values())
def handle_media_type(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=call.message.text + f'\nmedia_type: {call.data}',
        reply_markup=WHICH_STORAGE_KEYBOARD,
    )


@bot.callback_query_handler(
    func=lambda call: call.data in ['personal', 'general']
)
def handle_media_store(call):
    new_message = call.message.text + f'\nstore: {call.data}'
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=new_message,
    )
    save_info = extract_save_info(new_message)
    media_path = get_media_path(
        save_info=save_info,
        username=call.message.chat.username,
    )
    add_torrent(
        torrent_file=bot.download_file(bot.get_file(save_info['file_id']).file_path),
        torrent_path=media_path,
    )
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f'Начата загрузка в {media_path}',
    )


def main():
    bot.infinity_polling()


if __name__ == '__main__':
    main()
