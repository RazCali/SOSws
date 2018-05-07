import string
import random

def generateRandStr(size):
	chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
	return ''.join(random.choice(chars) for _ in range(size))