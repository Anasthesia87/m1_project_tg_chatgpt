from .start import start
from .help import help
from .random import random_fact, random_fact_more, random_fact_end
from .gpt import gpt, handler_prompt, cancel_gpt, cancel_gpt_command
from .talk import talk, select_person, talk_handler, talk_finish
from .quiz import quiz_start, quiz_select_topic, quiz_process_answer, quiz_more, quiz_change_topic, quiz_finish
from .voice import voice
from .translate import translate_start, translate_selected_language, translate_process_text, translate_change_language
