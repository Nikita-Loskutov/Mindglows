from flask import Flask, render_template, send_from_directory, request, jsonify, redirect
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ChatMember
from aiogram.filters import Command
from aiogram import F
from threading import Thread
from db_utils import add_user, get_user, update_user_coins, update_invited_friends, award_referral_bonus, daily_reward_amount, accrue_profit_per_hour
from db_utils import get_card_data, update_card_level, session, User
import datetime


TOKEN = '7636282193:AAHHIcQdFrM5ZV2_ObyjjjvUwCqr6FFjL2U' #Ваш токен бота
apiserv = "https://4a3b-89-163-140-175.ngrok-free.app"  #ссылка вашего сервера
your_channel = "https://t.me/your_channel" #ваш тг канал


bot = Bot(token=TOKEN)
dp = Dispatcher()


app = Flask(__name__, static_folder='../src', template_folder='../src')


#Роуты Flask
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return send_from_directory('../src', 'index.html')

@app.route('/user/<username>')
def user_page(username):
    user_id = request.args.get('user_id')
    return render_template("index.html", user_id=user_id, username=username)

@app.route('/user_data', methods=['GET'])
def user_data():
    user_id = request.args.get('user_id', 0)
    user = get_user(user_id)
    if user:
        profit_gained = accrue_profit_per_hour(user)
        level_thresholds = [
            0, 5000, 25000, 100000, 1000000,
            2000000, 10000000, 50000000, 1000000000, 10000000000
        ]

        if user.level < len(level_thresholds):
            next_level_coins = level_thresholds[user.level] - user.coins
        else:
            next_level_coins = "Max level"

        return jsonify(
            success=True,
            coins=user.coins,
            profit_per_tap=user.profit_per_tap,
            profit_per_hour=user.profit_per_hour,
            level=user.level,
            next_level_coins=next_level_coins,

            task_tg_done=user.task_tg_done,
            task_x_done=user.task_x_done,
            task_inst_done=user.task_inst_done,
            task_yt_done=user.task_yt_done,
            task_part_done=user.task_part_done,

            profit_gained=profit_gained,

            daily_day=user.daily_reward_day,
            daily_claimed=user.daily_reward_claimed,
            last_reward_claim_date=user.last_reward_claim_date.isoformat() if user.last_reward_claim_date else None
        )
    else:
        return jsonify(success=False, error="User not found"), 404

    

@app.route('/update_coins', methods=['POST'])
def update_coins():
    user_id = request.headers.get('User-ID')
    coins = request.json.get('coins')
    update_user_coins(user_id, coins)
    return jsonify({'success': True})

@app.route('/get_card_data', methods=['GET'])
def get_card_data_endpoint():
    user_id = request.args.get('user_id')
    card_type = request.args.get('card_type')
    
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        card_data = get_card_data(user, card_type)
        return jsonify(card_data)
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/upgrade_card', methods=['POST'])
def upgrade_card():
    user_id = request.json.get('user_id')
    card_type = request.json.get('card_type')
    if update_card_level(user_id, card_type):
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.update_profit()
            session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 400


CARD_TYPES = [
    'token', 'staking', 'genesis', 'echeleon', 'ledger', 'quantum', 'multitap'
]

@app.route('/get_user_cards', methods=['GET'])
def get_user_cards():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    user = session.query(User).filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    cards = []
    for card_type in CARD_TYPES:
        data = get_card_data(user, card_type)
        # добавим тип для фронта
        data['type'] = card_type
        cards.append(data)

    return jsonify(cards)

@app.route('/update_profit_per_hour', methods=['POST'])
def update_profit_per_hour():
    try:
        data = request.get_json()
        user_id = request.headers.get('User-ID')
        profit_per_hour = data.get('profit_per_hour')

        if not user_id or profit_per_hour is None:
            return jsonify(success=False, error="Invalid data"), 400

        update_profit_per_hour(int(user_id), float(profit_per_hour))
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route('/claim_task_reward', methods=['POST'])
def claim_task_reward():
    user_id = request.json.get('user_id')
    task = request.json.get('task')
    reward = request.json.get('reward', 0)
    user = get_user(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    attr = f'task_{task}_done'
    if getattr(user, attr, False):
        return jsonify({'success': False, 'message': 'Уже получено!'})
    setattr(user, attr, True)
    user.coins += reward
    session.commit()
    return jsonify({'success': True})


REWARD_INTERVAL = datetime.timedelta(hours=24)

@app.route('/claim_daily_reward', methods=['POST'])
def claim_daily_reward():
    user_id = request.json.get('user_id')
    user = get_user(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})

    now = datetime.datetime.utcnow()
    last_claim = user.last_reward_claim_date

    if last_claim:
        elapsed = now - last_claim
        # Проверка: прошло ли достаточно времени
        if elapsed < REWARD_INTERVAL and user.daily_reward_claimed:
            # Осталось времени до следующей награды
            remaining = REWARD_INTERVAL - elapsed
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            return jsonify({
                'success': False,
                'message': f'The reward can be obtained through {mins} minutes and {secs} seconds'
            })

        # Если прошло слишком много времени (пропуск)
        if elapsed > REWARD_INTERVAL * 1.5:
            user.daily_reward_day = 1
    else:
        # Первый раз
        user.daily_reward_day = 1

    user.daily_reward_claimed = True
    user.last_reward_claim_date = now
    reward = daily_reward_amount(user.daily_reward_day)
    user.coins += reward
    user.daily_reward_day = user.daily_reward_day + 1 if user.daily_reward_day < 7 else 1
    session.commit()
    return jsonify({'success': True, 'reward': reward})

@app.route('/invited_friends')
def invited_friends():
    user_id = request.args.get('user_id')
    user = get_user(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    friends_str = user.friends_usernames or ""
    friends = [{'id': i, 'name': name} for i, name in enumerate(friends_str.split(',')) if name]
    return jsonify({'success': True, 'referrals': friends})


@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "User"

    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    web_app_url = f"{apiserv}/?user_id={user_id}&username={username}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Play in 1 click 🎮', web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton(text='Subscribe to the channel 📢', url=f'{your_channel}')],
        [InlineKeyboardButton(text='How to make money on the game 💰', callback_data='how_to_earn')]
    ])

    referrer_id = None
    if args and args[0].startswith('referrer_'):
        referrer_id = args[0].split('_')[1]

    existing_user = get_user(user_id)
    if existing_user:
        await message.answer(
            "Hello! Welcome to MindGlows🎮!\n"
            "From now on you are the director. Tap the screen, collect coins, pump passive income,"
            "Develop your own income strategy."
            "\nDon't forget about your friends - invite them to the game and get even more coins together!",
            reply_markup=keyboard
        )
        return

    new_user = add_user(user_id, username, referrer_id=referrer_id)

    if referrer_id:
        premium_status = await check_premium_status(user_id)
        award_referral_bonus(user_id, referrer_id, premium_status)

        await message.answer(
            "Hello! Welcome to MindGlows🎮!\n"
            "From now on you are the director. Tap the screen, collect coins, pump passive income,"
            "Develop your own income strategy."
            "\nDon't forget about your friends - invite them to the game and get even more coins together!",
            reply_markup=keyboard
        )



@dp.callback_query(F.data.in_({'how_to_earn'}))
async def button_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or callback_query.from_user.first_name or "User"

    web_app_url = f"{apiserv}/?user_id={user_id}&username={username}"
    keyboards = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Play in 1 click 🎮', web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton(text='Subscribe to the channel 📢', url=f'{your_channel}')]
    ])

    await callback_query.message.answer(
        "How to play MindGlows?\n"
        "💰Tap to earn\nTap the screen and collect coins.\n"
        "\n⛏Mine\nUpgrade cards that will give you the opportunity for passive income.\n"
        "\n⏰ Profit per hour\nThe exchange will work for you independently, even when you are not in the game for"
        " 3 hours. Then you will need to re-enter the game again.\n"
        "\n📈 LVL\nThe more coins you have on your balance, the higher the exchange level."
        " The higher the level, the faster you can earn even more coins.\n"
        "\n👥 Friends\nInvite your friends and you will get bonuses. Help your friend move to the next leagues,"
        " and you will receive even more bonuses.",
        reply_markup=keyboards
    )

    await callback_query.answer()


#Запуск Tг бота
async def telegram_main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


#Запуск Flask
def run_flask():
    app.run(host='0.0.0.0', port=5000, use_reloader=False)


if __name__ == '__main__':
    # Flask  в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Telegram запускается в основном потоке
    asyncio.run(telegram_main())
