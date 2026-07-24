from aiogram import types
from aiogram.types import InputMediaPhoto, FSInputFile
from aiogram.exceptions import TelegramBadRequest
import os

async def send_menu_photo(event, photo_path, caption, reply_markup, parse_mode="HTML"):
    if not os.path.exists(photo_path):
        # Fallback to text if photo doesn't exist
        if isinstance(event, types.CallbackQuery):
            try:
                await event.message.edit_text(text=caption, reply_markup=reply_markup, parse_mode=parse_mode)
            except TelegramBadRequest:
                try:
                    await event.message.delete()
                except:
                    pass
                await event.message.answer(text=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            await event.answer(text=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        return

    photo = FSInputFile(photo_path)
    
    if isinstance(event, types.CallbackQuery):
        try:
            # Try to edit media if the original message had a photo
            media = InputMediaPhoto(media=photo, caption=caption, parse_mode=parse_mode)
            await event.message.edit_media(media=media, reply_markup=reply_markup)
        except TelegramBadRequest:
            # If original message was text, edit_media will fail. So we delete and send a new photo message.
            try:
                await event.message.delete()
            except:
                pass
            await event.message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        # It's a regular message
        await event.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
