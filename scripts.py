import os

def run_black():
    os.system('black tests globalpayments')


def run_pyright():
    os.system('poetry run pyright')
