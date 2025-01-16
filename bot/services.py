async def send_message(message, mes_list):
    """
    Отправка сообщений в цикле из переданного списка.
    """
    for part in mes_list:
        await message.answer(part, parse_mode="Markdown")

    m = f"{message.from_user.username} {message.text}"
    await message.bot.send_message(text=m, chat_id=249503190)
