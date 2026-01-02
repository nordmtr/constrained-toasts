import logging
import os
import random
from pathlib import Path

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

BASE_DIR = Path(__file__).resolve().parent
WHITELIST_NAME = "whitelist.txt"
BLACKLIST_NAME = "blacklist.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("constrained_toasts")
COMMANDS = [
    BotCommand("add_whitelist", "Add a word to the whitelist"),
    BotCommand("add_blacklist", "Add a word to the blacklist"),
    BotCommand("remove_whitelist", "Remove a word from the whitelist"),
    BotCommand("remove_blacklist", "Remove a word from the blacklist"),
    BotCommand("get_toast", "Get random words: /get_toast b <N> w <M>"),
    BotCommand("start", "Show help"),
]


def get_data_dir() -> Path:
    env_value = os.getenv("TOAST_DATA_DIR")
    if env_value:
        return Path(env_value).expanduser().resolve()
    return BASE_DIR / "data"


def normalize_word(raw: str) -> str:
    cleaned = " ".join(raw.strip().split())
    return cleaned.lower()


def read_words_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    words: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        normalized = normalize_word(line)
        if normalized and normalized not in seen:
            words.append(normalized)
            seen.add(normalized)
    return words


def read_words(path: Path) -> set[str]:
    return set(read_words_list(path))


def add_word(path: Path, raw_word: str) -> tuple[bool, str]:
    normalized = normalize_word(raw_word)
    if not normalized:
        return False, "empty"
    words = read_words(path)
    if normalized in words:
        return False, normalized
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{normalized}\n")
    return True, normalized


def write_words(path: Path, words: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(words)
    if content:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def remove_word(path: Path, raw_word: str) -> tuple[bool, str]:
    normalized = normalize_word(raw_word)
    if not normalized:
        return False, "empty"
    words = read_words_list(path)
    if normalized not in set(words):
        return False, normalized
    write_words(path, [word for word in words if word != normalized])
    return True, normalized


def sample_words(path: Path, count: int) -> list[str]:
    if count <= 0:
        return []
    words = list(read_words(path))
    return random.sample(words, count)


def parse_toast_args(args: list[str]) -> tuple[int, int]:
    if len(args) % 2 != 0 or not args:
        raise ValueError("Expected pairs like b <N> w <M>.")

    counts = {"b": None, "w": None}
    idx = 0
    while idx < len(args):
        key = args[idx].lower()
        if key in {"b", "blacklist"}:
            bucket = "b"
        elif key in {"w", "whitelist"}:
            bucket = "w"
        else:
            raise ValueError(f"Unexpected key: {args[idx]}")

        if counts[bucket] is not None:
            raise ValueError(f"Duplicate entry for {key}.")

        try:
            value = int(args[idx + 1])
        except ValueError as exc:
            raise ValueError(f"Invalid number for {key}.") from exc

        if value < 0:
            raise ValueError(f"Negative number for {key}.")

        counts[bucket] = value
        idx += 2

    if counts["b"] is None or counts["w"] is None:
        raise ValueError("Missing b or w counts.")

    return counts["b"], counts["w"]


def build_toast_response(blacklist_count: int, whitelist_count: int) -> tuple[bool, str]:
    if blacklist_count < 0 or whitelist_count < 0:
        return False, "Counts must be zero or positive."

    blacklist_path = get_data_dir() / BLACKLIST_NAME
    whitelist_path = get_data_dir() / WHITELIST_NAME
    blacklist_words = read_words(blacklist_path)
    whitelist_words = read_words(whitelist_path)

    if blacklist_count > len(blacklist_words) or whitelist_count > len(whitelist_words):
        return (
            False,
            "Not enough words. "
            f"Blacklist has {len(blacklist_words)}, whitelist has {len(whitelist_words)}.",
        )

    sampled_blacklist = random.sample(list(blacklist_words), blacklist_count)
    sampled_whitelist = random.sample(list(whitelist_words), whitelist_count)

    blacklist_text = ", ".join(sampled_blacklist) if sampled_blacklist else "-"
    whitelist_text = ", ".join(sampled_whitelist) if sampled_whitelist else "-"

    return (
        True,
        f"Blacklist ({blacklist_count}): {blacklist_text}\n"
        f"Whitelist ({whitelist_count}): {whitelist_text}",
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        "Commands:\n"
        "/add_whitelist <word>\n"
        "/add_blacklist <word>\n"
        "/remove_whitelist <word>\n"
        "/remove_blacklist <word>\n"
        "/get_toast b <N> w <M>"
    )


async def add_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    raw_word = " ".join(context.args).strip()
    if not raw_word:
        await update.message.reply_text("Usage: /add_whitelist <word>")
        return

    added, info = add_word(get_data_dir() / WHITELIST_NAME, raw_word)
    if added:
        await update.message.reply_text(f"Added to whitelist: {info}")
    else:
        if info == "empty":
            await update.message.reply_text("Word is empty after normalization.")
        else:
            await update.message.reply_text(f"Already in whitelist: {info}")


async def add_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    raw_word = " ".join(context.args).strip()
    if not raw_word:
        await update.message.reply_text("Usage: /add_blacklist <word>")
        return

    added, info = add_word(get_data_dir() / BLACKLIST_NAME, raw_word)
    if added:
        await update.message.reply_text(f"Added to blacklist: {info}")
    else:
        if info == "empty":
            await update.message.reply_text("Word is empty after normalization.")
        else:
            await update.message.reply_text(f"Already in blacklist: {info}")


async def remove_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    raw_word = " ".join(context.args).strip()
    if not raw_word:
        await update.message.reply_text("Usage: /remove_whitelist <word>")
        return

    removed, info = remove_word(get_data_dir() / WHITELIST_NAME, raw_word)
    if removed:
        await update.message.reply_text(f"Removed from whitelist: {info}")
    else:
        if info == "empty":
            await update.message.reply_text("Word is empty after normalization.")
        else:
            await update.message.reply_text(f"Not found in whitelist: {info}")


async def remove_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    raw_word = " ".join(context.args).strip()
    if not raw_word:
        await update.message.reply_text("Usage: /remove_blacklist <word>")
        return

    removed, info = remove_word(get_data_dir() / BLACKLIST_NAME, raw_word)
    if removed:
        await update.message.reply_text(f"Removed from blacklist: {info}")
    else:
        if info == "empty":
            await update.message.reply_text("Word is empty after normalization.")
        else:
            await update.message.reply_text(f"Not found in blacklist: {info}")


async def get_toast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    try:
        blacklist_count, whitelist_count = parse_toast_args(context.args)
    except ValueError:
        await update.message.reply_text("Usage: /get_toast b <N> w <M>")
        return
    ok, message = build_toast_response(blacklist_count, whitelist_count)
    await update.message.reply_text(message)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(COMMANDS)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set.")

    application = ApplicationBuilder().token(token).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_whitelist", add_whitelist))
    application.add_handler(CommandHandler("add_blacklist", add_blacklist))
    application.add_handler(CommandHandler("remove_whitelist", remove_whitelist))
    application.add_handler(CommandHandler("remove_blacklist", remove_blacklist))
    application.add_handler(CommandHandler("get_toast", get_toast))

    logger.info("Bot started.")
    application.run_polling()


if __name__ == "__main__":
    main()
