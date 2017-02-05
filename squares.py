"""Superbowl 2017 Squares game

relies on two files:
* superbowl.csv which has a list of Name,Bet
* board.tsv which is written by this file and later read

usage:
import squares
game = squares.Squares()
# see boards.tsv

import squares
game = squares.Squares(new=False)
game.find_winner(34, 34, squares.Quarter.FIRST)

"""

from __future__ import division

import argparse
import math
import random
import csv
import enum


class Quarter(enum.Enum):
	FIRST = 0
	SECOND = 1
	THIRD = 2
	FINAL = 3


class Person(object):
	def __init__(self, name, payment):
		self.name = name
		self.payment = int(payment)

	def __repr__(self):
		return self.name


class Squares(object):

	def __init__(self, new=True):
		self.board = [[None for i in range(0,10)] for j in range(0, 10)]
		self.people = set()
		self.total_pot = 0
		if new:
			self.create_new()
		else:
			self.from_existing()

	def create_new(self):
		"""Generate a Squares game from a set of people and bets, defined in superbowl.csv"""

		self.board = [[None for i in range(0,10)] for j in range(0, 10)]
		self.people = set()
		self.total_pot = 0

		with open('superbowl.csv', 'rb') as superbowl_csv:
			 people_reader = csv.DictReader(superbowl_csv)
			 for row in people_reader:
			 	person = Person(row['Name'], row['Bet'])
				self.people.add(person)
				self.total_pot += person.payment

		self._generate_board()

		with open('board.tsv', 'wb') as board_tsv:
			tsvout = csv.writer(board_tsv, delimiter='\t')
			for row in self.board:
				tsvout.writerow(row)

	def from_existing(self):
		"""Hydrate a Squares game from an existing set of csv files including a board"""

		# Add people that were existing
		with open('superbowl.csv', 'rb') as superbowl_csv:
			 people_reader = csv.DictReader(superbowl_csv)
			 for row in people_reader:
			 	self._add_person(Person(row['Name'], row['Bet']))

		# create board from existing
		self.board = []
		with open('board.tsv', 'rb') as board_tsv:
			tsv_reader = csv.reader(board_tsv, delimiter='\t')
			for row in tsv_reader:
				self.board.append(row)

	def _generate_board(self):
		"""This should only be run once -- at kickoff

		Randomly assigns board squares proportionally to bets
		"""

		# Figure out how many squares each person gets
		cost_per_square = 100 / self.total_pot
		people_to_num_squares = {}
		num_filled_squares = 0
		for person in self.people:
			num_squares_for_person = int(math.floor(100 / (self.total_pot / person.payment)))
			people_to_num_squares[person] = num_squares_for_person
			num_filled_squares += num_squares_for_person

		# Get the non-filled squares (likely all of them)
		possible_squares = []
		for i, row in enumerate(self.board):
			for j, col in enumerate(row):
				if col == None:
					possible_squares.append((i, j))

		# Fill rows
		for person in people_to_num_squares:
			num_squares = people_to_num_squares[person]
			for i in range(num_squares):
				square = random.choice(possible_squares)
				self.board[square[0]][square[1]] = person
				# this is choice without replacement
				possible_squares.remove(square)

	def find_winner(self, falcons_score, patriots_score, quarter):

		falcons_digit = int(str(falcons_score)[-1])
		patriots_digit = int(str(patriots_score)[-1])

		winning_name = self.board[falcons_digit][patriots_digit]

		if quarter == Quarter.FIRST:
			money = self.total_pot / 8
		elif quarter == Quarter.SECOND:
			money = self.total_pot / 4
		elif quarter == Quarter.THIRD:
			money = self.total_pot / 8
		elif quarter == Quarter.FINAL:
			money = self.total_pot / 2

		print 'Winner: {}'.format(winning_name)
		print 'Payout: {}'.format(money)
