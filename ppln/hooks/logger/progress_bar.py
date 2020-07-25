import sys

from colorama import Fore, Style

from ...utils.dist import master_only
from ...utils.progress_bar import ProgressBar
from ..registry import HOOKS
from .base import BaseLoggerHook
from .utils import get_lr


@HOOKS.register_module
class ProgressBarLoggerHook(BaseLoggerHook):
    def __init__(self, bar_width):
        super(ProgressBarLoggerHook, self).__init__()
        self.bar_width = bar_width
        self.bar = None

    def before_epoch(self, runner):
        self.bar = ProgressBar(task_num=len(runner.data_loader), bar_width=self.bar_width)

    @master_only
    def after_epoch(self, runner):
        sys.stdout.write("\n")

    def after_iter(self, runner):
        self.log(runner)

    @master_only
    def log(self, runner):
        epoch_color = Fore.YELLOW
        mode_color = (Fore.RED, Fore.BLUE)[runner.train_mode]
        text_color = (Fore.CYAN, Fore.GREEN)[runner.train_mode]
        epoch_text = f"{epoch_color}epoch:{Style.RESET_ALL} {runner.epoch + 1:<4}"
        log_items = [
            (" " * 11, epoch_text)[runner.train_mode],
            f"{mode_color}{runner.mode:<5}{Style.RESET_ALL}",
            f"{text_color}iter:{Style.RESET_ALL} {runner.iter + 1}",
            f'{text_color}lr:{Style.RESET_ALL} {", ".join([f"{lr:.3e}" for lr in get_lr(runner.optimizer)])}',
        ]

        for name, value in runner.epoch_outputs.items():
            if isinstance(value, float):
                value = f"{value:.2f}" if name in ["data_time", "time"] else f"{value:.4f}"
            log_items.append(f"{text_color}{name}:{Style.RESET_ALL} {value}")
        self.bar.update(f"{' | '.join(log_items)}")
