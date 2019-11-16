import aiohttp
from datetime import datetime
from queries import Queries
import warnings

# Bots approved by the Repl.it Team that are allowed to log in
# (100% impossible to hack yes definitely)
whitelisted_bots = {
	'repltalk',
	'replmodbot'
}

base_url = 'https://repl.it'


class ReplTalkException(Exception): pass


class NotWhitelisted(ReplTalkException): pass


class BoardDoesntExist(ReplTalkException): pass


class GraphqlError(ReplTalkException): pass


class InvalidLogin(ReplTalkException): pass


class Repl():
	__slots__ = ('id', 'embed_url', 'url', 'title', 'language')

	def __init__(
		self, id, embed_url, hosted_url, title, language, language_name
	):
		self.id = id
		self.embed_url = embed_url
		self.url = hosted_url
		self.title = title
		self.language = Language(
			data=language
			# name=language_name,
			# display_name=language['displayName'],
			# icon=language['icon']
		)

	def __repr__(self):
		return f'<{self.title}>'

	def __eq__(self, repl2):
		return self.id == repl2.id

	def __hash__(self):
		return hash((self.id, self.url, self.title))


class AsyncPostList():
	__slots__ = (
		'i', 'client', 'sort', 'search', 'after', 'limit', 'posts_queue', 'board'
	)

	def __init__(
		self, client, board, limit=32, sort='new', search='', after=None
	):
		self.i = 0
		self.client = client

		self.sort = sort
		self.search = search
		self.after = after

		self.limit = limit
		self.posts_queue = []

		self.board = board

	def __aiter__(self):
		return self

	async def __anext__(self):
		if self.i >= self.limit:
			raise StopAsyncIteration
		if len(self.posts_queue) == 0:
			new_posts = await self.board._get_posts(
				sort=self.sort,
				search=self.search,
				after=self.after
			)
			self.posts_queue.extend(new_posts['items'])
			self.after = new_posts['pageInfo']['nextCursor']
		current_post_raw = self.posts_queue.pop(0)
		current_post = get_post_object(self.client, current_post_raw)

		self.i += 1

		return current_post

	def __await__(self):
		post_list = PostList(
			client=self.client,
			posts=[],
			board=self.board,
			after=self.after,
			sort=self.sort,
			search=self.search
		)
		return post_list.next().__await__()


class PostList(list):
	__slots__ = ('posts', 'after', 'board', 'sort', 'search', 'i', 'client')

	def __init__(self, client, posts, board, after, sort, search):
		self.posts = posts
		self.after = after
		self.board = board
		self.sort = sort
		self.search = search
		self.client = client
		warnings.warn(
			'Doing await get_posts is deprecated, '
			'use async for post in get_posts instead.',
			DeprecationWarning
		)

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		self.i += 1
		if self.i >= len(self.posts):
			raise StopIteration
		return self.posts[self.i]

	def __str__(self):
		if len(self.posts) > 30:
			return f'<{len(self.posts)} posts>'
		return str(self.posts)

	def __getitem__(self, indices):
		return self.posts[indices]

	async def next(self):
		new_posts = await self.board._get_posts(
			sort=self.sort,
			search=self.search,
			after=self.after
		)
		posts = [
			get_post_object(self.client, post_raw) for post_raw in new_posts['items']
		]
		self.after = new_posts['pageInfo']['nextCursor']
		self.posts = posts
		return self

	def __eq__(self, postlist2):
		return self.board == postlist2.board

	def __ne__(self, postlist2):
		return self.board != postlist2.board


class CommentList(list):
	__slots__ = ('post', 'comments', 'after', 'board', 'sort', 'search', 'i')

	def __init__(self, post, comments, board, after, sort):
		self.post = post
		self.comments = comments
		self.after = after
		self.board = board
		self.sort = sort

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		self.i += 1
		if self.i >= len(self.posts):
			raise StopIteration
		return self.comments[self.i]

	def __str__(self):
		if len(self.comments) > 30:
			return f'<{len(self.comments)} comments>'
		return str(self.comments)

	async def next(self):
		post_list = await self.board.comments(
			sort=self.sort,
			search=self.search,
			after=self.after
		)
		self.comments = post_list.comments
		self.board = post_list.board
		self.after = post_list.after
		self.sort = post_list.sort
		self.search = post_list.search

	def __eq__(self, commentlist2):
		return self.post == commentlist2.post

	def __ne__(self, commentlist2):
		return self.post != commentlist2.post


class Comment():
	__slots__ = (
		'client', 'id', 'content', 'timestamp', 'can_edit', 'can_comment',
		'can_report', 'has_reported', 'path', 'url', 'votes', 'can_vote',
		'has_voted', 'author', 'post', 'replies', 'parent'
	)

	def __init__(
		self, client, data, post, parent=None
	):
		self.client = client
		self.id = data['id']
		self.content = data['body']
		timestamp = data['timeCreated']
		self.timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
		self.can_edit = data['canEdit']
		self.can_comment = data['canComment']
		self.can_report = data['canReport']
		self.has_reported = data['hasReported']
		self.path = data['url']
		self.url = base_url + data['url']
		self.votes = data['voteCount']
		self.can_vote = data['canVote']
		self.has_voted = data['hasVoted']
		self.parent = parent
		user = data['user']
		if user is not None:
			user = User(
				client,
				user=user
			)
		self.author = user
		self.post = post  # Should already be a post object

		raw_replies = data.get('comments', [])
		replies = []

		for inner_reply in raw_replies:
			replies.append(Comment(
				self.client,
				data=inner_reply,
				post=self.post,
				parent=self
			))
		self.replies = replies

	def __repr__(self):
		if len(self.content) > 100:
			return repr(self.content[:100] + '...')
		else:
			return repr(self.content)

	def __eq__(self, post2):
		return self.id == post2.id

	def __ne__(self, post2):
		return self.id != post2.id

	async def reply(self, content):
		c = await self.client.perform_graphql(
			'createComment',
			Queries.create_comment,
			input={
				'body': content,
				'commentId': self.id,
				'postId': self.post.id
			}
		)
		c = c['comment']
		return Comment(
			self.client,
			data=c,
			post=self.post,
			parent=self
		)

	def __hash__(self):
		return hash((self.id, self.content, self.votes, self.replies))


class Board():
	__slots__ = ('client', 'name', )

	def __init__(self, client):
		self.client = client

	async def _get_posts(self, sort, search, after):
		return await self.client._posts_in_board(
			board_slugs=[self.name],
			languages=[],
			order=sort,
			search_query=search,
			after=after
		)

	def get_posts(self, sort='top', search='', limit=32, after=None):
		if sort == 'top':
			sort = 'votes'
		return AsyncPostList(
			self.client,
			limit=limit,
			sort=sort,
			search=search,
			after=after,
			board=self
		)
		# return post_list.ainit(
		# 	posts=posts,
		# 	board=self,
		# 	after=_posts['pageInfo']['nextCursor'],
		# 	sort=sort,
		# 	search=search
		# )
		# _posts_func = self._get_posts(
		# 	sort=sort,
		# 	search=search,
		# 	after=after
		# )
		# posts = []
		# if 'items' not in _posts:
		# 	raise KeyError(f'items not in _posts. {_posts}')
		# for post in _posts['items']:
		# 	posts.append(
		# 		get_post_object(self.client, post)
		# 	)

		# return PostList(
		# )

	async def create_post(  # TODO
		self, title: str, content: str, repl: Repl = None, show_hosted=False
	):
		pass
		# if repl:
		# 	repl_id = repl.id

	def __repr__(self):
		return f'<{self.name} board>'

	def __hash__(self):
		return hash((self.name,))


class RichBoard(Board):  # a board with more stuff than usual
	__slots__ = (
		'client', 'id', 'url', 'name', 'slug', 'title_cta', 'body_cta',
		'button_cta', 'name', 'repl_required'
	)

	def __init__(
		self, client, data
	):
		self.client = client
		self.id = data['id']
		self.url = base_url + data['url']
		self.name = data['name']
		self.slug = data['slug']
		self.body_cta = data['bodyCta']
		self.title_cta = data['titleCta']
		self.button_cta = data['buttonCta']

	def __eq__(self, board2):
		return self.id == board2.id and self.name == board2.name

	def __ne__(self, board2):
		return self.id != board2.id or self.name != board2.name

	def __hash__(self):
		return hash((
			self.id,
			self.name,
			self.slug,
			self.body_cta,
			self.title_cta,
			self.button_cta
		))


class Language():
	__slots__ = (
		'id', 'display_name', 'key', 'category', 'is_new', 'icon', 'icon_path',
		'tagline'
	)

	def __init__(
		self, data
	):
		self.id = data['id']
		self.display_name = data['displayName']
		self.key = data['key']  # identical to id???
		self.category = data['category']
		self.tagline = data['tagline']
		self.is_new = data['isNew']
		icon = data['icon']
		self.icon_path = icon
		if icon and icon[0] == '/':
			icon = 'https://repl.it' + icon
		self.icon = icon

	def __str__(self):
		return self.display_name

	def __repr__(self):
		return f'<{self.id}>'

	def __eq__(self, lang2):
		return self.key == lang2.key

	def __ne__(self, lang2):
		return self.key != lang2.key

	def __hash__(self):
		return hash((
			self.id,
			self.display_name,
			self.key,
			self.category,
			self.tagline,
			self.icon_path
		))


def get_post_object(client, post):
	return Post(
		client, data=post
	)


class Post():
	__slots__ = (
		'client', 'id', 'title', 'content', 'is_announcement', 'path', 'url',
		'board', 'timestamp', 'can_edit', 'can_comment', 'can_pin', 'can_set_type',
		'can_report', 'has_reported', 'is_locked', 'show_hosted', 'votes',
		'can_vote', 'has_voted', 'author', 'repl', 'answered', 'can_answer',
		'pinned', 'comment_count', 'language'
	)

	def __init__(
		self, client, data
	):
		self.client = client
		self.id = data['id']
		self.title = data['title']
		self.content = data['body']
		self.is_announcement = data['isAnnouncement']
		self.path = data['url']
		self.url = base_url + data['url']
		board = RichBoard(
			client=client,
			data=data['board']
		)
		self.board = board
		timestamp = data['timeCreated']
		self.timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
		self.can_edit = data['canEdit']
		self.can_comment = data['canComment']
		self.can_pin = data['canPin']
		self.can_set_type = data['canSetType']
		self.can_report = data['canReport']
		self.has_reported = data['hasReported']
		self.is_locked = data['isLocked']
		self.show_hosted = data['showHosted']
		self.votes = data['voteCount']
		self.can_vote = data['canVote']
		self.has_voted = data['hasVoted']

		user = data['user']
		if user is not None:
			user = User(
				client,
				user=user
			)
		self.author = user

		repl = data['repl']
		if repl is None:
			self.repl = None
			self.language = None
		else:
			self.repl = Repl(
				id=repl['id'],
				embed_url=repl['embedUrl'],
				hosted_url=repl['hostedUrl'],
				title=repl['title'],
				# language=repl['language'],
				language_name=repl['language'],
				language=repl['lang']
			)
			self.language = self.repl.language
		self.answered = data['isAnswered']
		self.can_answer = data['isAnswerable']
		self.pinned = data['isPinned']
		self.comment_count = data['commentCount']

	def __repr__(self):
		return f'<{self.title}>'

	def __eq__(self, post2):
		return self.id == post2.id

	def __ne__(self, post2):
		return self.id != post2.id

	async def get_comments(self, order='new'):
		_comments = await self.client._get_comments(
			self.id,
			order
		)
		comments = []
		if 'comments' not in _comments:
			print('reeeeeee', _comments)
		for c in _comments['comments']['items']:
			comments.append(Comment(
				self.client,
				data=c,
				post=self
			))
		return comments

	async def post_comment(self, content):
		c = await self.client.perform_graphql(
			'createComment',
			Queries.create_comment,
			input={
				'body': content,
				'postId': self.id
			}
		)
		c = c['comment']
		return Comment(
			client=self.client,
			data=c,
			post=self,
		)

	def __hash__(self):
		return hash((
			self.id,
			self.title,
			self.content
		))


class Subscription():
	__slots__ = ('name', 'id')

	def __init__(
		self, client, user, data
	):
		self.id = data['planId']
		if self.id == 'hacker2':
			self.name = 'hacker'
		else:
			self.name = self.id

	def __str__(self):
		return self.name

	def __repr__(self):
		return f'<{self.id}>'

	def __eq__(self, sub2):
		return self.id == sub2.id

	def __ne__(self, sub2):
		return self.id != sub2.id

	def __hash__(self):
		return hash((self.id, self.name))


class Organization():
	__slots__ = ('name',)

	def __init__(
		self, data
	):
		self.name = data['name']

	def __str__(self):
		return self.name

	def __repr__(self):
		return f'<{self.name}>'

	def __eq__(self, sub2):
		return self.name == sub2.name

	def __ne__(self, sub2):
		return self.name != sub2.name

	def __hash__(self):
		return hash((self.name,))


class User():
	__slots__ = (
		'client', 'data', 'id', 'name', 'avatar', 'url', 'cycles', 'roles',
		'full_name', 'first_name', 'last_name', 'organization', 'is_logged_in',
		'bio', 'subscription', 'languages'
	)

	def __init__(
		self, client, user
	):
		self.client = client
		self.id = user['id']
		self.name = user['username']
		self.avatar = user['image']
		self.url = user['url']
		self.cycles = user['karma']
		self.roles = user['roles']

		self.full_name = user['fullName']
		self.first_name = user['firstName']
		self.last_name = user['lastName']
		organization = user['organization']
		if organization:
			organization = Organization(organization)
		self.organization = organization
		self.is_logged_in = user['isLoggedIn']
		self.bio = user['bio']
		subscription = user['subscription']
		if subscription:
			subscription = Subscription(client, self, subscription)
		self.subscription = subscription
		self.languages = [
			Language(language) for language in user['languages']
		]

	def __repr__(self):
		return f'<{self.name} ({self.cycles})>'

	def __eq__(self, user2):
		return self.id == user2.id

	def __ne__(self, user2):
		return self.id != user2.id

	def __hash__(self):
		return hash((
			self.id,
			self.name,
			self.full_name,
			self.bio
		))


class Leaderboards():
	__slots__ = (
		'limit', 'iterated', 'users', 'raw_users', 'next_cursor', 'client'
	)

	def __init__(self, client, limit):
		self.limit = limit
		self.iterated = 0
		self.users = []
		self.raw_users = []
		self.next_cursor = None
		self.client = client

	def __await__(self):
		return self.load_all().__await__()

	def __aiter__(self):
		return self

	def __next__(self):
		raise NotImplementedError

	async def load_all(self):
		async for _ in self: _
		return self.users

	async def __anext__(self):
		ended = len(self.users) + 1 > self.limit
		if self.iterated <= len(self.users) and not ended:
			self.iterated += 30
			leaderboard = await self.client._get_leaderboard(
				self.next_cursor
			)
			self.next_cursor = leaderboard['pageInfo']['nextCursor']
			self.raw_users.extend(leaderboard['items'])

		if ended:
			raise StopAsyncIteration
		user = self.raw_users[len(self.users)]
		user = User(
			self,
			user=user
		)

		self.users.append(user)
		return user

	def __repr__(self):
		if self.iterated >= self.limit:
			return f'<top {self.limit} leaderboard users (cached)>'
		return f'<top {self.limit} leaderboard users>'

	def __str__(self):
		return self.__repr__()


class Client():
	__slots__ = ('default_ref', 'default_requested_with', 'sid', 'boards')

	def __init__(self):
		self.default_ref = base_url + '/@mat1/repl-talk-api'
		self.default_requested_with = 'ReplTalk'
		self.sid = None
		self.boards = self._boards(self)

	async def perform_graphql(
		self,
		operation_name,
		query,
		ignore_none=False,
		**variables,
	):
		payload = {
			'operationName': operation_name,
			'query': str(query)
		}
		if ignore_none:
			payload['variables'] = {q: variables[q] for q in variables if q is not None}
		else:
			payload['variables'] = variables

		async with aiohttp.ClientSession(
			cookies={'connect.sid': self.sid},
			headers={
				'referer': self.default_ref,
				'X-Requested-With': self.default_requested_with
			}
		) as s:
			async with s.post(
				base_url + '/graphql',
				json=payload
			) as r:
				data = await r.json()
		if 'data' in data:
			data = data['data']
		if data is None:
			print(await r.json())
			return None
		keys = data.keys()
		if len(keys) == 1:
			data = data[next(iter(keys))]
		if isinstance(data, list):
			print(data)
			loc = data[0]['locations'][0]['column']
			print(str(query)[:loc-1] + '!!!!!' + str(query)[loc-1:])
		return data

	async def login(self, username, password):
		if username.lower() not in whitelisted_bots:
			raise NotWhitelisted(
				f'{username} is not whitelisted and therefore is not allowed to log in.\n'
				'Please ask mat#6207 if you would like to be added to the whitelist.'
			)

		async with aiohttp.ClientSession(
			headers={'referer': self.default_ref}
		) as s:
			async with s.post(
				base_url + '/login',
				json={
					'username': username,
					'password': password,
					'teacher': False
				},
				headers={
					'X-Requested-With': username
				}
			) as r:
				if await r.text() == '{"message":"Invalid username or password."}':
					raise InvalidLogin('Invalid username or password.')
				# Gets the connect.sid cookie
				connectsid = str(dict(r.cookies)['connect.sid'].value)
				self.sid = connectsid
			return self

	async def _get_post(self, post_id):
		post = await self.perform_graphql(
			'post', Queries.get_post, id=int(post_id)
		)
		return post

	async def get_post(self, post_id):
		post = await self._get_post(post_id)
		return get_post_object(self, post)

	async def post_exists(self, post_id):
		if isinstance(post_id, Post):
			post_id = post_id.id
		post = await self.perform_graphql(
			'post', Queries.post_exists, id=post_id
		)
		return post is not None

	async def _get_leaderboard(self, cursor=None):
		if cursor is None:
			leaderboard = await self.perform_graphql(
				'leaderboard',
				Queries.get_leaderboard
			)
		else:
			leaderboard = await self.perform_graphql(
				'leaderboard',
				Queries.get_leaderboard,
				after=cursor
			)
		return leaderboard

	def get_leaderboard(self, limit=30):
		return Leaderboards(self, limit)

	async def _get_all_posts(
		self, order='new', search_query='', after=None
	):
		if after is None:
			posts = await self.perform_graphql(
				'posts',
				Queries.get_all_posts,
				order=order,
				searchQuery=search_query
			)
			return posts
		else:
			posts = await self.perform_graphql(
				'posts',
				Queries.get_all_posts,
				order=order,
				searchQuery=search_query,
				after=after
			)
			return posts

	async def _posts_in_board(
		self,
		board_slugs=None,
		languages=[],
		order='new',
		search_query=None,
		after=None
	):
		posts = await self.perform_graphql(
			'PostsFeed',
			Queries.posts_feed,
			ignore_none=True,
			boardSlugs=board_slugs,
			languages=languages,
			order=order,
			searchQuery=search_query,
			after=after
		)
		return posts

	class _boards:
		board_names = ['all', 'announcements', 'challenge', 'ask', 'learn', 'share']
		__slots__ = ['client', ] + board_names
		for board in board_names:
			locals()['_' + board] = type(
				'_' + board,
				(Board,),
				{'name': board}
			)
			# Creates classes for each of the boards
		del board	 # Don't want that extra class var

		def __init__(self, client):
			self.client = client

			self.all = self._all(client)
			self.announcements = self._announcements(client)
			self.challenge = self._challenge(client)
			self.ask = self._ask(client)
			self.learn = self._learn(client)
			self.share = self._share(client)

	async def _get_comments(self, post_id, order='new'):
		return await self.perform_graphql(
			'post',
			Queries.get_comments,
			id=post_id,
			commentsOrder=order
		)

	# async def _get_all_comments(self, order='new'):
	# 	return await self.perform_graphql(
	# 		'comments',
	# 		Queries.get_all_comments,
	# 		order=order
	# 	)

	# async def get_all_comments(self, order='new'):
	# 	_comments = await self._get_all_comments(order=order)
	# 	comments = []
	# 	for c in _comments['items']:
	# 		comments.append(Comment(
	# 			self,
	# 			id=c['id'],
	# 			body=c['body'],
	# 			time_created=c['timeCreated'],
	# 			can_edit=c['canEdit'],
	# 			can_comment=c['canComment'],
	# 			can_report=c['canReport'],
	# 			has_reported=c['hasReported'],
	# 			url=c['url'],
	# 			votes=c['voteCount'],
	# 			can_vote=c['canVote'],
	# 			has_voted=c['hasVoted'],
	# 			user=c['user'],
	# 			post=c['post'],
	# 			comments=c['comments']
	# 		))
	# 	return comments

	async def _get_user(self, name):
		user = await self.perform_graphql(
			'userByUsername',
			Queries.get_user,
			username=name,
		)
		return user

	async def get_user(self, name):
		user = await self._get_user(name)
		if user is None:
			return None
		u = User(
			self,
			user=user
		)
		return u
