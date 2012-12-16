from lettuce import *


@step('I have the number (\d+)')
def have_the_number(step, number):
    a = 1