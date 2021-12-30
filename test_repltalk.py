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
		async for post in self.client.boards.all.get_posts(sort='New', limit=1):
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
			self.run_async(self.client.get_post(0))
		except repltalk.PostNotFound:
			return
		raise Exception('Deleted post did not raise PostNotFound')

	async def async_test_comments(self):
		post = await self.client.get_post(5599)
		for c in await post.get_comments():
			self.assertIsInstance(c.id, int)

	def test_comments(self):
		self.run_async(self.async_test_comments())

	def test_user_comments(self):
		user = self.run_async(self.client.get_user('mat1'))
		comments = self.run_async(user.get_comments())
		self.assertIsInstance(comments, list, 'Not a list of comments?')

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
		async for post in self.client.boards.all.get_posts(sort='New'):
			pass

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
		async for post in self.client.boards.all.get_posts(sort='New', limit=64):
			self.assertIsInstance(post, repltalk.Post)

	def test_async_for_posts(self):
		self.run_async(self.async_test_async_for_posts())

	def make_example_user(self, override={}):
		data = {
			'id': '747811',
			'username': 'mat1',
			'image': None,
			'url': 'https://repl.it/@mat1',
			'karma': 1000,
			'roles': [],
			'fullName': 'mat',
			'firstName': 'mat',
			'lastName': ' ',
			'timeCreated': '2000-1-01T01:01:00.000Z',
			'organization': None,
			'isLoggedIn': False,
			'bio': 'I do dev. https://matdoes.dev',
			'isHacker': True,
			'languages': []
		}
		data.update(override)
		return repltalk.User(self.client, data)

	def make_example_board(self, rich=True):
		return repltalk.RichBoard(self.client, {
			'id': 14,
			'url': '/talk/announcements',
			'name': 'Announcements',
			'slug': 'announcements',
			'body_cta': None,
			'title_cta': None,
			'button_cta': 'Post an update'
		})

	def make_example_post(self, lazy=False):
		if lazy:
			return repltalk.LazyPost(self.client, {
				'id': '135633',
				'title': 'Repl Talk Rules and Guidelines [README]',
				'url': '/talk/announcements/Repl-Talk-Rules-and-Guidelines-README/135633',
				'body': None,
				'user': self.make_example_user().data,
			})
		else:
			return repltalk.Post(self.client, {
				'id': '135633',
				'title': 'Repl Talk Rules and Guidelines [README]',
				'body': 'Rules',
				'isAnnouncement': True,
				'url': '/talk/announcements/Repl-Talk-Rules-and-Guidelines-README/135633',
				'board': self.make_example_board().data,
				'timeCreated': '2000-1-01T01:01:00.000Z',
				'canEdit': False,
				'canComment': True,
				'canPin': False,
				'canSetType': False,
				'canReport': True,
				'hasReported': False,
				'isLocked': False,
				'showHosted': False,
				'voteCount': 100,
				'votes': {
					'items': []
				},
				'canVote': True,
				'hasVoted': False,
				'user': self.make_example_user().data,
				'repl': None,
				'isAnswered': False,
				'isAnswerable': False,
				'isPinned': True,
				'commentCount': 100
			})

	def make_example_report(self):
		return repltalk.Report(self.client, {
			'id': 1,
			'type': 'post',
			'reason': 'Report reason',
			'resolved': False,
			'timeCreated': None,
			'creator': self.make_example_user().data,
			'post': self.make_example_post(lazy=True).data
		})


	async def async_test_report_get_attached(self):
		print('making example report')
		report = self.make_example_report()
		assert isinstance(report.post, repltalk.LazyPost)
		await report.get_attached()
		assert isinstance(report.post, repltalk.Post)
		await report.get_attached()
		assert isinstance(report.post, repltalk.Post)

	def test_report_get_attached(self):
		self.run_async(self.async_test_report_get_attached())


if __name__ == '__main__':
	unittest.main()
