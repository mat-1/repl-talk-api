import aiohttp
from datetime import datetime


# Bots approved by the Repl.it Team that are allowed to log in
# (100% impossible to hack yes definitely)
whitelisted_bots = {
	'repltalk'
}

base_url = 'https://repl.it'


class NotWhitelisted(Exception): pass


class BoardDoesntExist(Exception): pass


class GraphqlError(Exception): pass


class InvalidLogin(Exception): pass


board_ids = {
	'share': 3,
	'ask': 6,
	'announcements': 14,
	'challenge': 16,
	'learn': 17
}


class PostList(list):
	__slots__ = ('posts', 'after', 'board', 'sort', 'search', 'i')

	def __init__(self, posts, board, after, sort, search):
		self.posts = posts
		self.after = after
		self.board = board
		self.sort = sort
		self.search = search

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
		post_list = await self.board.get_posts(
			sort=self.sort,
			search=self.search,
			after=self.after
		)
		self.posts = post_list.posts
		self.board = post_list.board
		self.after = post_list.after
		self.sort = post_list.sort
		self.search = post_list.search
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
		'client', 'id', 'content', 'datetime', 'can_edit', 'can_comment',
		'can_report', 'has_reported', 'url', 'votes', 'can_vote', 'has_voted',
		'author', 'post', 'replies', 'parent'
	)

	def __init__(
		self, client, id, body, time_created, can_edit,
		can_comment, can_report, has_reported, url, votes,
		can_vote, has_voted, user, post, comments,
		parent=None
	):
		self.client = client
		self.id = id
		self.content = body
		self.datetime = datetime.strptime(time_created, '%Y-%m-%dT%H:%M:%S.%fZ')
		self.can_edit = can_edit
		self.can_comment = can_comment
		self.can_report = can_report
		self.has_reported = has_reported
		self.url = base_url + url
		self.votes = votes
		self.can_vote = can_vote
		self.has_voted = has_voted
		self.parent = parent
		if user is not None:
			user = User(
				client,
				user=user
			)
		self.author = user
		self.post = post  # Should already be a post object
		replies = []
		for c in comments:
			try:
				co = c['comments']
			except KeyError:
				co = []
			replies.append(Comment(
				self.client,
				id=c['id'],
				body=c['body'],
				time_created=c['timeCreated'],
				can_edit=c['canEdit'],
				can_comment=c['canComment'],
				can_report=c['canReport'],
				has_reported=c['hasReported'],
				url=c['url'],
				votes=c['voteCount'],
				can_vote=c['canVote'],
				has_voted=c['hasVoted'],
				user=c['user'],
				post=self.post,
				comments=co,
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
			graphql.create_comment,
			input={
				'body': content,
				'commentId': self.id,
				'postId': self.post.id
			}
		)
		c = c['comment']
		return Comment(
			self,
			id=c['id'],
			body=c['body'],
			time_created=c['timeCreated'],
			can_edit=c['canEdit'],
			can_comment=c['canComment'],
			can_report=c['canReport'],
			has_reported=c['hasReported'],
			url=c['url'],
			votes=c['voteCount'],
			can_vote=c['canVote'],
			has_voted=c['hasVoted'],
			user=c['user'],
			post=self.post,
			comments=c['comments']
		)


class Board():
	__slots__ = ('client', 'name', )

	def __init__(self, client):
		self.client = client

	async def _get_posts(self, sort, search, after):
		if self.name == 'all':
			return await self.client._get_all_posts(
				order=sort,
				search_query='',
				after=after
			)
		else:
			if self.name in board_ids:
				board_id = board_ids[self.name]

				return await self.client._posts_in_board(
					board_id=board_id,  # :ok_hand:
					order=sort,
					search_query=search,
					after=after
				)
			else:
				raise BoardDoesntExist(f'Board "{self.name}" doesn\'t exist.')

	async def get_posts(self, sort='top', search='', after=None):
		if sort == 'top':
			sort = 'votes'
		_posts = await self._get_posts(
			sort=sort,
			search=search,
			after=after
		)
		posts = []
		if 'items' not in _posts:
			raise KeyError(f'items not in _posts. {_posts}')
		for post in _posts['items']:
			posts.append(
				get_post_object(self.client, post)
			)
		return PostList(
			posts=posts,
			board=self,
			after=_posts['pageInfo']['nextCursor'],
			sort=sort,
			search=search
		)

	def __repr__(self):
		return f'<{self.name} board>'


class RichBoard(Board):  # a board with more stuff than usual
	__slots__ = ('client', 'id', 'url', 'name', 'slug', 'title_cta', 'body_cta', 'button_cta', 'name')
	def __init__(
		self, client, id, url, slug, title_cta, body_cta, button_cta, name
	):
		self.id = id
		self.url = base_url + url
		self.name = name
		self.slug = slug
		self.client = client
		self.body_cta = body_cta
		self.title_cta = title_cta
		self.button_cta = button_cta

	def __eq__(self, board2):
		return self.id == board2.id and self.name == board2.name

	def __ne__(self, board2):
		return self.id != board2.id or self.name != board2.name


class Language():
	__slots__ = ('name', 'display_name', 'icon')
	def __init__(
		self, name, display_name, icon=None
	):
		self.name = name
		self.display_name = display_name
		if icon[0] == '/':
			icon = 'https://repl.it' + icon
		self.icon = icon

	def __str__(self):
		return self.display_name

	def __repr__(self):
		return f'<{self.name}>'

	def __eq__(self, lang2):
		return self.name == lang2.name

	def __ne__(self, lang2):
		return self.name != lang2.name


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
			name=language_name,
			display_name=language['displayName'],
			icon=language['icon']
		)

	def __repr__(self):
		return f'<{self.title}>'

	def __eq__(self, repl2):
		return self.id == repl2.id


def get_post_object(client, post):
	return Post(
		client,
		id=post['id'],
		title=post['title'],
		body=post['body'],
		is_announcement=post['isAnnouncement'],
		is_pinned=post['isPinned'],
		comment_count=post['commentCount'],
		url=post['url'],
		board=post['board'],
		time_created=post['timeCreated'],
		can_edit=post['canEdit'],
		can_comment=post['canComment'],
		can_pin=post['canPin'],
		can_set_type=post['canSetType'],
		can_report=post['canReport'],
		has_reported=post['hasReported'],
		is_locked=post['isLocked'],
		show_hosted=post['showHosted'],
		vote_count=post['voteCount'],
		can_vote=post['canVote'],
		has_voted=post['hasVoted'],
		user=post['user'],
		repl=post['repl'],
		is_answered=post['isAnswered'],
		is_answerable=post['isAnswerable']
	)


class Post():
	__slots__ = ('client', 'id', 'title', 'content', 'is_announcement', 'url', 'board', 'datetime', 'can_edit', 'can_comment', 'can_pin', 'can_set_type', 'can_report', 'has_reported', 'is_locked', 'show_hosted', 'votes', 'can_vote', 'has_voted', 'author', 'repl', 'answered', 'can_answer', 'pinned', 'comment_count', 'language')
	def __init__(
		self, client, id, title, body, is_announcement,
		url, board, time_created, can_edit, can_comment,
		can_pin, can_set_type, can_report, has_reported,
		is_locked, show_hosted, vote_count, can_vote,
		has_voted, user, repl, is_answered, is_answerable, is_pinned, comment_count
	):
		self.client = client
		self.id = id
		self.title = title
		self.content = body
		self.is_announcement = is_announcement
		self.url = base_url + url
		board = RichBoard(
			client=client,
			id=board['id'],
			url=board['url'],
			slug=board['slug'],
			title_cta=board['titleCta'],
			body_cta=board['bodyCta'],
			button_cta=board['buttonCta'],
			name=board['name']
		)
		self.board = board
		self.datetime = datetime.strptime(time_created, '%Y-%m-%dT%H:%M:%S.%fZ')
		self.can_edit = can_edit
		self.can_comment = can_comment
		self.can_pin = can_pin
		self.can_set_type = can_set_type
		self.can_report = can_report
		self.has_reported = has_reported
		self.is_locked = is_locked
		self.show_hosted = show_hosted
		self.votes = vote_count
		self.can_vote = can_vote
		self.has_voted = has_voted

		if user is not None:
			user = User(
				client,
				user=user
			)
		self.author = user
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
		self.answered = is_answered
		self.can_answer = is_answerable
		self.pinned = is_pinned
		self.comment_count = comment_count

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
				id=c['id'],
				body=c['body'],
				time_created=c['timeCreated'],
				can_edit=c['canEdit'],
				can_comment=c['canComment'],
				can_report=c['canReport'],
				has_reported=c['hasReported'],
				url=c['url'],
				votes=c['voteCount'],
				can_vote=c['canVote'],
				has_voted=c['hasVoted'],
				user=c['user'],
				post=self,
				comments=c['comments']
			))
		return comments

	async def post_comment(self, content):
		c = await self.client.perform_graphql(
			'createComment',
			graphql.create_comment,
			input={
				'body': content,
				'postId': self.id
			}
		)
		c = c['comment']
		return Comment(
			client=self.client,
			id=c['id'],
			body=c['body'],
			time_created=c['timeCreated'],
			can_edit=c['canEdit'],
			can_comment=c['canComment'],
			can_report=c['canReport'],
			has_reported=c['hasReported'],
			url=c['url'],
			votes=c['voteCount'],
			can_vote=c['canVote'],
			has_voted=c['hasVoted'],
			user=c['user'],
			post=self,
			comments=[]
		)


class Subscription():
	__slots__ = ('name', 'plan_id', 'name', 'plan')
	def __init__(
		self, client, user, subscription
	):
		if subscription is None:
			self.name = None
			self.plan_id = None
		else:
			self.plan_id = subscription['planId']
			if self.plan_id == 'hacker2':
				self.plan = 'hacker'
			else:
				self.name = self.plan_id

	def __str__(self):
		return self.name

	def __repr__(self):
		return f'<{self.plan_id}>'

	def __eq__(self, sub2):
		return self.plan_id == sub2.plan_id

	def __ne__(self, sub2):
		return self.plan_id != sub2.plan_id


class User():
	__slots__ = ('client', 'data', 'id', 'name', 'avatar', 'url', 'cycles', 'roles', 'full_name', 'first_name', 'last_name', 'organization', 'is_logged_in', 'bio', 'subscription', 'languages')
	def __init__(
		self, client, user
	):
		self.client = client
		self.data = user
		self.id = user['id']
		self.name = user['username']
		self.avatar = user['image']
		self.url = user['url']
		self.cycles = user['karma']
		self.roles = user['roles']

		self.full_name = user['fullName']
		self.first_name = user['firstName']
		self.last_name = user['lastName']
		self.organization = user['organization']
		self.is_logged_in = user['isLoggedIn']
		self.bio = user['bio']
		subscription = Subscription(client, self, user['subscription'])
		self.subscription = subscription
		self.languages = user['languages']

	def __repr__(self):
		return f'<{self.name} ({self.cycles})>'

	def __eq__(self, user2):
		return self.id == user2.id

	def __ne__(self, user2):
		return self.id != user2.id


class Leaderboards():
	__slots__ = ('limit', 'iterated', 'users', 'raw_users', 'next_cursor', 'client')
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


class graphql:
	'There are all the graphql strings used'
	user_attributes = [
		'id', 'username', 'url', 'image', 'karma', 'firstName', 'lastName',
		'fullName', 'displayName', 'isLoggedIn', 'bio', 'organization { name }',
		'subscription { planId }',
		'languages { id key displayName tagline icon }',
		'roles { id name key tagline }'
	]
	user_part = 'user {' + ' '.join(user_attributes) + '}'
	repl_part = '''
		repl {
			id
			embedUrl: url(lite: true)
			hostedUrl
			title
			lang {
				icon
				displayName
			}
			language
			timeCreated
		}'''
	board_part = '''
	board {
		id
		url
		slug
		titleCta
		bodyCta
		buttonCta
		description
		name
	}'''
	post_part = f'''
		id
		title
		body
		url
		commentCount
		isPinned
		isLocked
		isAnnouncement
		timeCreated
		voteCount
		canVote
		hasVoted
		{board_part}
		canEdit
		canComment
		canPin
		canSetType
		canReport
		hasReported
		showHosted
		isAnswered
		isAnswerable
		{repl_part}
		{user_part}
	'''
	comment_part = f'''
		{user_part}
		id
		body
		timeCreated
		canEdit
		canComment
		canReport
		comments {{
			id
		}}
		hasReported
		url
		voteCount
		canVote
		hasVoted
		post {{
			{post_part}
		}}
	'''
	create_comment = f'''
	mutation createComment($input: CreateCommentInput!) {{
		createComment(input: $input) {{
			comment {{
				id
				...CommentDetailComment
				comments {{
					id
					...CommentDetailComment
				}}
				parentComment {{
					id
				}}
			}}
		}}
	}}

	fragment CommentDetailComment on Comment {{
		id
		body
		timeCreated
		canEdit
		canComment
		canReport
		hasReported
		url
		voteCount
		canVote
		hasVoted
		{user_part}
	}}
	'''
	get_post = f'''
	query post($id: Int!) {{
		post(id: $id) {{
			{post_part}
		}}
	}}
	'''
	get_leaderboard = f'''
	query leaderboard($after: String) {{
		leaderboard(after: $after) {{
			pageInfo {{
				nextCursor
			}}
			items {{
				{' '.join(user_attributes)}
			}}
		}}
	}}
	'''
	get_all_posts = f'''
	query posts($order: String, $after: String, $searchQuery: String) {{
		posts(order: $order, after: $after, searchQuery: $searchQuery) {{
			pageInfo {{
				nextCursor
			}}
			items {{
				{post_part}
			}}
		}}
	}}
	'''
	post_by_board = f'''
	query postsByBoard(
		$id: Int!, $searchQuery: String, $postsOrder: String, $postsAfter: String
	) {{
		postsByBoard(
			id: $id, searchQuery: $searchQuery, order: $postsOrder, after: $postsAfter
		) {{
			pageInfo {{
				nextCursor
			}}
			items {{
				{post_part}
			}}
		}}
	}}
	'''
	get_comments = f'''
	query post(
		$id: Int!, $commentsOrder: String, $commentsAfter: String
	) {{
		post(id: $id) {{
			comments(order: $commentsOrder, after: $commentsAfter) {{
				pageInfo {{
					nextCursor
				}}
				items {{
					...CommentDetailComment
					comments {{
						...CommentDetailComment
					}}
				}}
			}}
		}}
	}}

	fragment CommentDetailComment on Comment {{
		id
		body
		timeCreated
		canEdit
		canComment
		canReport
		hasReported
		url
		voteCount
		canVote
		hasVoted
		{user_part}
	}}

	'''
	get_all_comments = f'''
	query comments($after: String, $order: String) {{
		comments(after: $after, order: $order) {{
			items {{
				{comment_part}
				comments {{
					{comment_part}
				}}
			}}
			pageInfo {{
				hasNextPage
				nextCursor
			}}
		}}
	}}
	'''
	get_user = f'''
	query userByUsername(
		$username: String!,
	) {{
		user: userByUsername(username: $username) {{
			{' '.join(user_attributes)}
		}}
	}}
	'''
	post_exists = 'query post($id: Int!) { post(id: $id) { id } }'


class Client():
	__slots__ = ('default_ref', 'default_requested_with', 'sid', 'boards')
	def __init__(self):
		self.default_ref = base_url + '/@mat1/repl-talk-api'
		self.default_requested_with = 'ReplTalk'
		self.sid = None
		self.boards = self._boards(self)

	async def perform_graphql(self, operation_name, query, **variables):
		payload = {
			'operationName': operation_name,
			'variables': variables,
			'query': query
		}

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
			'post', graphql.get_post, id=int(post_id)
		)
		return post

	async def get_post(self, post_id):
		post = await self._get_post(post_id)
		return get_post_object(self, post)

	async def post_exists(self, post_id):
		if isinstance(post_id, Post):
			post_id = post_id.id
		post = await self.perform_graphql(
			'post', graphql.post_exists, id=post_id
		)
		return post is not None

	async def _get_leaderboard(self, cursor=None):
		if cursor is None:
			leaderboard = await self.perform_graphql(
				'leaderboard',
				graphql.get_leaderboard
			)
		else:
			leaderboard = await self.perform_graphql(
				'leaderboard',
				graphql.get_leaderboard,
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
				graphql.get_all_posts,
				order=order,
				searchQuery=search_query
			)
			return posts
		else:
			posts = await self.perform_graphql(
				'posts',
				graphql.get_all_posts,
				order=order,
				searchQuery=search_query,
				after=after
			)
			return posts

	async def _posts_in_board(
		self, order='new', search_query='', board_id=0, after=None
	):
		if board_id == 0:
			raise Exception('board id cant be 0')
		if after is None:
			posts = await self.perform_graphql(
				'postsByBoard',
				graphql.post_by_board,
				postsOrder=order,
				searchQuery=search_query,
				id=board_id
			)
			return posts
		else:
			posts = await self.perform_graphql(
				'postsByBoard',
				graphql.post_by_board,
				postsOrder=order,
				searchQuery=search_query,
				postsAfter=after,
				id=board_id
			)
			return posts

	class _boards:
		board_names = ['all', 'announcements', 'challenge', 'ask', 'learn', 'share']
		__slots__ = ['client',] + board_names
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
			graphql.get_comments,
			id=post_id,
			commentsOrder=order
		)

	async def _get_all_comments(self, order='new'):
		return await self.perform_graphql(
			'comments',
			graphql.get_all_comments,
			order=order
		)

	async def get_all_comments(self, order='new'):
		_comments = await self._get_all_comments(order=order)
		comments = []
		for c in _comments['items']:
			comments.append(Comment(
				self,
				id=c['id'],
				body=c['body'],
				time_created=c['timeCreated'],
				can_edit=c['canEdit'],
				can_comment=c['canComment'],
				can_report=c['canReport'],
				has_reported=c['hasReported'],
				url=c['url'],
				votes=c['voteCount'],
				can_vote=c['canVote'],
				has_voted=c['hasVoted'],
				user=c['user'],
				post=c['post'],
				comments=c['comments']
			))
		return comments

	async def _get_user(self, name):
		user = await self.perform_graphql(
			'userByUsername',
			graphql.get_user,
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