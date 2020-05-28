import unittest
import repltalk
import asyncio
import datetime

# The following code is for unit tests,
# please read README.md for documentation

class TestReplTalk(unittest.TestCase):
	def setUp(self):
		self.client = repltalk.Client()
		self.loop = asyncio.get_event_loop()
		self.run_async = self.loop.run_until_complete

	async def async_test_board_posts(self):
		async for post in self.client.boards.all.get_posts(sort='new', limit=1):
			self.assertIsInstance(post.author, repltalk.User)

	def test_board_posts(self):
		self.run_async(self.async_test_board_posts())

	def test_post(self):
		post = self.run_async(self.client.get_post(5599))
		self.assertIsNotNone(post, 'Post should not be None')
		self.assertIsNotNone(post.board, 'Post board should not be None')
		self.assertIsInstance(
			post.timestamp, datetime.datetime, 'Post time is a datetime object'
		)
		self.assertIsNotNone(post.author, 'Author is not None')
		if post.repl is not None:
			self.assertIsNotNone(post.repl.language)
		self.assertTrue(post.board.name.istitle(), 'Board name is a title')
		self.assertTrue(post.board.slug.islower(), 'Board slug is lowercase')

	def test_deleted_post(self):
		try:
			post = self.run_async(self.client.get_post(0))
		except repltalk.PostNotFound:
			return

	# def test_post_comments(self):
	# 	comments = self.run_async(self.client.get_all_comments())

	async def async_test_comments(self):
		post = await self.client.get_post(5599)
		for c in await post.get_comments():
			self.assertIsInstance(c.id, int)
	
	# def test_report(self):
	# 	post = self.run_async(self.client.get_post(21533))
	# 	self.run_async(post.report('Ignore this, just AA testing the report w/ mats repl.it API')) # its my ignore this post

	def test_comments(self):
		self.run_async(self.async_test_comments())

	def test_user_comments(self):
		user = self.run_async(self.client.get_user('mat1'))
		comments = self.run_async(user.get_comments())
		self.assertIsInstance(comments, list, 'Not a list of comments?')
	
	def test_user_posts(self):
		user = self.run_async(self.client.get_user('mat1'))
		posts = self.run_async(user.get_posts())
		self.assertIsInstance(posts, list, 'Not a list of comments?')

	def test_post_exists(self):
		exists = self.run_async(self.client.post_exists(1))
		self.assertFalse(exists, 'Invalid post should not exist')

		exists = self.run_async(self.client.post_exists(5599))
		self.assertTrue(exists, 'Real post should exist')

	def test_get_user(self):
		user = self.run_async(self.client.get_user('a'))
		self.assertIsNone(user)

		user = self.run_async(self.client.get_user('mat1'))
		self.assertIsInstance(user.id, int, 'User ID is not an integer')
		self.assertIsNotNone(user)

	async def async_test_leaderboards(self):
		users = await self.client.get_leaderboard()
		for user in users:
			self.assertIsInstance(user.id, int)

	def test_leaderboards(self):
		self.run_async(self.async_test_leaderboards())

	async def async_test_get_new_posts(self):
		await self.client.boards.all.get_posts(sort='new')

	def test_get_new_posts(self):
		self.run_async(self.async_test_get_new_posts())

	def test_answered(self):
		post = self.run_async(self.client.get_post(12578))
		self.assertTrue(post.answered)
		self.assertTrue(post.can_answer)

	def test_language(self):
		post = self.run_async(self.client.get_post(13315))
		self.assertEqual(post.language.id, 'python3')
		self.assertEqual(str(post.language), 'Python')

	async def async_test_async_for_posts(self):
		async for post in self.client.boards.all.get_posts(sort='new', limit=64):
			self.assertIsInstance(post, repltalk.Post)

	def test_async_for_posts(self):
		self.run_async(self.async_test_async_for_posts())


unittest.main()
