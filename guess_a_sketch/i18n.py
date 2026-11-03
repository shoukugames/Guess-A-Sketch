"""English / Japanese text. Players always spell English words; in Japanese
mode the menus and messages are Japanese and each word's Japanese name is
shown as a clue once it is solved."""

import locale
import os

LANGUAGES = ("en", "ja")
LANG = "en"

STRINGS = {
    "en": {
        "subtitle": "Spell the word before the sketch is finished!",
        "play": "PLAY",
        "difficulty": "Difficulty",
        "points_x": "points x%d",
        "start_level": "Start level",
        "level_letters": "Level %d  -  %d letters",
        "expert_note": "Expert: 60-second timer",
        "for_parents": "For Parents",
        "credits": "Credits",
        "quit": "Quit",
        "language": "Language",
        "diff_Easy": "Easy", "diff_Medium": "Medium", "diff_Hard": "Hard",
        # play
        "level": "Level %d",
        "play_sub": "%d-letter words  -  word %d of %d  -  %s",
        "score": "Score",
        "time": "Time",
        "wrong_letters": "Wrong letters:  ",
        "chances": "Chances",
        "hints": "Hints",
        "hint_btn": "Hint  (%d left)",
        "pause": "Pause",
        "word_intro": "Level %d - word %d of %d",
        "already": "You already tried %s",
        "praise": ("Nice!", "Good one!", "Yes!", "Great!"),
        "wrong_one": "No %s - 1 chance left",
        "wrong_many": "No %s - %d chances left",
        "hint_msg": "Hint: the word has a %s",
        "no_hints": "No hints left!",
        "great_job": "Great job!",
        "points_plus": "+%d points",
        "click_continue": "Click or press Enter to continue",
        "click_enter": "Click or press Enter",
        "times_up": "Time's up!",
        "out_of_chances": "Out of chances!",
        "word_was": "The word was  %s",
        "paused": "Paused",
        "resume": "Resume",
        "quit_title": "Quit to Title",
        "level_complete": "Level %d complete!",
        "score_line": "Score: %d",
        "next_level": "Next: Level %d  -  %d-letter words",
        "expert_msg": "Expert mode! Tougher words and only 60 seconds.",
        "tougher_msg": "Words keep getting tougher. 60 seconds each.",
        "secs_per_word": "%d seconds per word",
        "continue": "Continue",
        # game over
        "game_over": "Game Over",
        "why_time": "Time ran out on:  %s",
        "why_chances": "Out of chances on:  %s",
        "final_score": "Final score:  %d",
        "level_reached": "Level reached:  %d   (%s)",
        "words_spelled": "Words spelled:  %d",
        "time_played": "Time played:  %s",
        "play_again": "Play Again",
        "main_menu": "Main Menu",
        # parents
        "total_time": "Total time played",
        "games_played": "Games played",
        "best_score": "Best score",
        "highest_level": "Highest level",
        "words_total": "Words spelled",
        "practice": "Words to practice (missed):  ",
        "none_yet": "none yet",
        "col_date": "Date", "col_played": "Played", "col_score": "Score", "col_mode": "Mode",
        "col_level": "Level", "col_result": "Result", "col_missed": "Missed word (level)",
        "missed_fmt": "%s  (level %d)",
        "no_games": "No games played yet. Progress appears here after each game.",
        "page": "Page %d of %d",
        "newer": "< Newer", "older": "Older >",
        "clear": "Clear History", "confirm": "Click again to confirm",
        "back": "Back",
        "res_Quit": "Quit", "res_Time ran out": "Time ran out", "res_Out of chances": "Out of chances",
        # credits
        "version": "Version %s",
        "released": "Released %s",
        "created_by": "Created by",
        "authors": "Shawn Rapaz and Claude Code",
        "website": "Website",
        "email": "Email",
        "music_note": "Original music & sound effects generated for this game.",
        "made_with": "Made with Python and pygame.",
        "font_note": "Japanese font: M PLUS Rounded 1c (SIL Open Font License)",
        # durations
        "dur_h": "%dh %02dm", "dur_m": "%dm %02ds", "dur_s": "%ds",
    },
    "ja": {
        "subtitle": "スケッチがかんせいするまえに、ことばをあてよう！",
        "play": "スタート",
        "difficulty": "むずかしさ",
        "points_x": "とくてん x%d",
        "start_level": "スタートレベル",
        "level_letters": "レベル %d  -  %d もじ",
        "expert_note": "エキスパート：60びょう",
        "for_parents": "おうちの方へ",
        "credits": "クレジット",
        "quit": "おわる",
        "language": "ことば",
        "diff_Easy": "かんたん", "diff_Medium": "ふつう", "diff_Hard": "むずかしい",
        # play
        "level": "レベル %d",
        "play_sub": "%dもじのことば  -  %d / %d もんめ  -  %s",
        "score": "スコア",
        "time": "じかん",
        "wrong_letters": "まちがえたもじ：  ",
        "chances": "チャンス",
        "hints": "ヒント",
        "hint_btn": "ヒント（のこり %d）",
        "pause": "いちじていし",
        "word_intro": "レベル %d - %d / %d もんめ",
        "already": "%s はもうつかったよ",
        "praise": ("いいね！", "そのちょうし！", "せいかい！", "すごい！"),
        "wrong_one": "%s ははいってないよ - のこり 1 かい",
        "wrong_many": "%s ははいってないよ - のこり %d かい",
        "hint_msg": "ヒント：%s がはいっているよ",
        "no_hints": "ヒントはもうないよ！",
        "great_job": "よくできました！",
        "points_plus": "+%d てん",
        "click_continue": "クリックか Enter でつぎへ",
        "click_enter": "クリックか Enter でつぎへ",
        "times_up": "じかんぎれ！",
        "out_of_chances": "チャンスがなくなった！",
        "word_was": "こたえは  %s",
        "paused": "いちじていし",
        "resume": "つづける",
        "quit_title": "タイトルへもどる",
        "level_complete": "レベル %d クリア！",
        "score_line": "スコア：%d",
        "next_level": "つぎ：レベル %d  -  %dもじのことば",
        "expert_msg": "エキスパートモード！むずかしいことばで60びょう！",
        "tougher_msg": "ことばがどんどんむずかしくなるよ。1もん60びょう。",
        "secs_per_word": "1もん %d びょう",
        "continue": "つぎへ",
        # game over
        "game_over": "ゲームオーバー",
        "why_time": "じかんぎれ：  %s",
        "why_chances": "チャンスぎれ：  %s",
        "final_score": "さいごのスコア：  %d",
        "level_reached": "とどいたレベル：  %d  （%s）",
        "words_spelled": "できたことば：  %d",
        "time_played": "あそんだじかん：  %s",
        "play_again": "もういちど",
        "main_menu": "メニューへ",
        # parents (adults: kanji is fine)
        "total_time": "合計プレイ時間",
        "games_played": "プレイ回数",
        "best_score": "最高スコア",
        "highest_level": "最高レベル",
        "words_total": "正解した単語",
        "practice": "練習したい単語（まちがえた単語）：  ",
        "none_yet": "まだありません",
        "col_date": "日時", "col_played": "プレイ時間", "col_score": "スコア", "col_mode": "難易度",
        "col_level": "レベル", "col_result": "結果", "col_missed": "まちがえた単語（レベル）",
        "missed_fmt": "%s（レベル %d）",
        "no_games": "まだプレイ記録がありません。ゲームが終わるとここに表示されます。",
        "page": "%d / %d ページ",
        "newer": "< 新しい", "older": "古い >",
        "clear": "記録を消去", "confirm": "もう一度押すと消去",
        "back": "もどる",
        "res_Quit": "中断", "res_Time ran out": "時間切れ", "res_Out of chances": "チャンス切れ",
        # credits
        "version": "バージョン %s",
        "released": "リリース日：%s",
        "created_by": "制作",
        "authors": "Shawn Rapaz ＆ Claude Code",
        "website": "ウェブサイト",
        "email": "メール",
        "music_note": "音楽と効果音はこのゲームのためのオリジナルです。",
        "made_with": "Python と pygame で制作しました。",
        "font_note": "日本語フォント：M PLUS Rounded 1c（SIL Open Font License）",
        # durations
        "dur_h": "%d時間%02d分", "dur_m": "%d分%02d秒", "dur_s": "%d秒",
    },
}

# Japanese names, shown as a clue once a word is solved (and on result screens).
JA_NAMES = {
    "OX": "うし", "AX": "おの", "TV": "テレビ",
    "CAT": "ねこ", "DOG": "いぬ", "SUN": "たいよう", "HAT": "ぼうし", "CUP": "マグカップ", "BUS": "バス",
    "PIG": "ぶた", "CAR": "くるま", "EGG": "たまご", "BEE": "はち", "KEY": "かぎ", "BED": "ベッド",
    "FAN": "せんぷうき", "ANT": "あり", "OWL": "ふくろう", "WEB": "くものす", "JAR": "びん",
    "FISH": "さかな", "TREE": "き", "BOAT": "ふね", "STAR": "ほし", "CAKE": "ケーキ", "BIRD": "とり",
    "BALL": "ボール", "MOON": "つき", "DUCK": "あひる", "KITE": "たこ（凧）", "FROG": "かえる",
    "LAMP": "ランプ", "BELL": "ベル", "DRUM": "たいこ", "TENT": "テント", "HARP": "ハープ",
    "VASE": "かびん", "CRAB": "かに",
    "HOUSE": "いえ", "APPLE": "りんご", "CLOCK": "とけい", "CHAIR": "いす", "TRAIN": "きしゃ",
    "HEART": "ハート", "SNAKE": "へび", "PIZZA": "ピザ", "TRUCK": "トラック", "CLOUD": "くも（雲）",
    "ROBOT": "ロボット", "SPOON": "スプーン", "GHOST": "おばけ", "CROWN": "おうかん", "SNAIL": "かたつむり",
    "ROCKET": "ロケット", "FLOWER": "はな", "BANANA": "バナナ", "PENCIL": "えんぴつ", "TURTLE": "かめ",
    "GUITAR": "ギター", "CASTLE": "おしろ", "CANDLE": "ろうそく", "BUCKET": "バケツ",
    "SPIDER": "くも（蜘蛛）", "ANCHOR": "いかり", "CACTUS": "サボテン", "TEAPOT": "ティーポット",
    "BALLOON": "ふうせん", "RAINBOW": "にじ", "PENGUIN": "ペンギン", "PUMPKIN": "かぼちゃ",
    "SNOWMAN": "ゆきだるま", "TRUMPET": "トランペット", "DIAMOND": "ダイヤモンド", "OCTOPUS": "たこ（蛸）",
    "BICYCLE": "じてんしゃ", "LOBSTER": "ロブスター", "LANTERN": "ランタン", "VOLCANO": "かざん",
    "UMBRELLA": "かさ", "ELEPHANT": "ぞう", "AIRPLANE": "ひこうき", "MUSHROOM": "きのこ",
    "DINOSAUR": "きょうりゅう", "SANDWICH": "サンドイッチ", "ENVELOPE": "ふうとう", "SAILBOAT": "ヨット",
    "CAMPFIRE": "たきび", "SEAHORSE": "タツノオトシゴ",
    "BUTTERFLY": "ちょうちょ", "HAMBURGER": "ハンバーガー", "SPACESHIP": "うちゅうせん",
    "SNOWFLAKE": "ゆきのけっしょう", "TELESCOPE": "ぼうえんきょう", "LIGHTBULB": "でんきゅう",
    "CROCODILE": "ワニ", "DRAGONFLY": "とんぼ", "PINEAPPLE": "パイナップル", "SAXOPHONE": "サックス",
    "JELLYFISH": "くらげ",
    "LIGHTHOUSE": "とうだい", "WATERMELON": "すいか", "STRAWBERRY": "いちご", "HELICOPTER": "ヘリコプター",
    "BASKETBALL": "バスケットボール", "SKATEBOARD": "スケートボード", "MICROPHONE": "マイク",
    "PAINTBRUSH": "ふで", "SUNGLASSES": "サングラス", "TOOTHBRUSH": "はブラシ",
    "BINOCULARS": "そうがんきょう", "CHANDELIER": "シャンデリア", "TRAMPOLINE": "トランポリン",
    "WHEELCHAIR": "くるまいす",
}


def set_lang(lang):
    global LANG
    LANG = lang if lang in LANGUAGES else "en"


def T(key, *args):
    s = STRINGS[LANG].get(key, STRINGS["en"].get(key, key))
    return s % args if args else s


def ja_name(word):
    return JA_NAMES.get(word, "")


def word_label(word):
    """'CAT' in English mode, 'CAT（ねこ）' in Japanese mode."""
    if LANG == "ja" and word in JA_NAMES:
        return "%s（%s）" % (word, JA_NAMES[word])
    return word


def duration(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return T("dur_h", h, m)
    if m:
        return T("dur_m", m, s)
    return T("dur_s", s)


def system_default():
    """Japanese if the OS is set to Japanese, otherwise English."""
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        v = os.environ.get(var, "")
        if v:
            return "ja" if v.lower().startswith("ja") else "en"
    try:
        loc = locale.getlocale()[0] or ""
        if loc.lower().startswith(("ja", "japanese")):
            return "ja"
    except (ValueError, TypeError):
        pass
    if os.name == "nt":
        try:
            import ctypes
            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF == 0x11:  # LANG_JAPANESE
                return "ja"
        except (AttributeError, OSError):
            pass
    return "en"
