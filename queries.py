import graphql


class Queries:
	'There are all the graphql strings used'
	language_attributes = graphql.Field((
		'id',
		'displayName',
		'key',
		'category',
		'tagline',
		'icon',
		'isNew'
	))
	language_field = graphql.Field({
		'lang': language_attributes
	})
	languages_field = graphql.Field({
		'languages': language_attributes
	})
	user_attributes = graphql.Field((
		'id',
		'username',
		'url',
		'image',
		'karma',
		'firstName',
		'lastName',
		'fullName',
		'displayName',
		'isLoggedIn',
		'bio',
		graphql.Field({'organization': 'name'}),
		graphql.Field({'subscription': 'planId'}),
		languages_field,
		graphql.Field({'roles': ('id', 'name', 'key', 'tagline')}),
	))
	user_field = graphql.Field({'user': user_attributes})
	repl_field = graphql.Field({
		'repl': (
			'id',
			graphql.Alias(
				'embedUrl',
				graphql.Field('url', args={'lite': 'true'})
			),
			'hostedUrl',
			'title',
			language_field,
			'language',
			'timeCreated'
		)
	})
	board_field = graphql.Field({
		'board': (
			'id',
			'url',
			'slug',
			'cta',
			'titleCta',
			'bodyCta',
			'buttonCta',
			'description',
			'name',
			'replRequired',
			'isLocked',
			'isPrivate'
		)
	})

	def connection_generator(attributes):
		return graphql.Field({
			'pageInfo': (
				'hasNextPage',
				# 'hasPreviousPage',
				'nextCursor',
				# 'previousCursor'
			),
			'items': attributes
		})
	# print(connection_generator('hi'))
	# exit()
	comment_attributes = graphql.Field((
		# user_field,
		'id',
		'body',
		'voteCount',
		'timeCreated',
		'timeUpdated',
		user_field,
		'url',
		{'post': 'id'},
		{'parentComment': 'id'},
		{'comments': 'id'},
		'isAuthor',
		'canEdit',
		'canVote',
		'canComment',
		'hasVoted',
		'canReport',
		'hasReported',
		'isAnswer',
		'canSelectAsAnswer',
		'canUnselectAsAnswer',
		graphql.Field(
			'preview',
			args={
				'removeMarkdown': 'true',
				'length': 150
			}
		)
	))
	comment_connection_field = graphql.Field(
		'comments',
		args={
			'after': '$after',
			'count': '$count',
			'order': '$order'
		},
		data=connection_generator(comment_attributes)
	)
	post_vote_connection = graphql.Field(
		graphql.Field(
			'votes',
			args={
				'before': '$votesBefore',
				'after': '$votesAfter',
				'count': '$votesCount',
				'order': '$votesOrder',
				'direction': '$votesDirection'
			},
			data=connection_generator((
				'id',
				{'user': 'id'},
				{'post': 'id'}
			))
		)
	)

	post_attributes = graphql.Field((
		'id',
		'title',
		'body',
		'showHosted',
		'voteCount',
		'commentCount',
		'isPinned',
		'isLocked',
		'timeCreated',  # datetime
		'timeUpdated',  # datetime
		'url',
		user_field,  # User
		board_field,  # Board
		repl_field,  # Repl
		comment_connection_field,
		post_vote_connection,
		'isAnnouncement',
		'isAuthor',
		'canEdit',
		'canComment',
		'canVote',
		'canPin',
		'canSetType',
		'canChangeBoard',
		'canLock',
		'hasVoted',
		'canReport',
		'hasReported',
		'isAnswered',
		'isAnswerable',
		{'answeredBy': user_attributes},
		{'answer': comment_attributes},
		'tutorialPages',
		graphql.Field(
			'preview',
			args={
				'removeMarkdown': 'true',
				'length': 150
			}
		)
	))
	comment_connection_field = graphql.Field((
		connection_generator(comment_attributes)
	))

	comment_detail_comment_fragment = graphql.Fragment(
		'CommentDetailComment',
		'Comment',
		comment_attributes
	)
	get_post = graphql.Query(
		'post',
		{
			'$id': 'Int!',
			'$count': 'Int',
			'$order': 'String',
			'$after': 'String',
			'$votesBefore': 'String',
			'$votesAfter': 'String',
			'$votesCount': 'Int',
			'$votesOrder': 'String',
			'$votesDirection': 'String',
		},
		graphql.Field(
			args={'id': '$id'},
			data={
				'post': post_attributes
			}
		)
	)
	get_leaderboard = graphql.Query(
		'leaderboard', {'$after': 'String'},
		{
			graphql.Field(args={'after': '$after'}, data={
				'leaderboard': connection_generator(user_attributes)
			})
		}
	)
	# get_all_posts = f'''
	# query posts($order: String, $after: String, $searchQuery: String) {{
	# 	posts(order: $order, after: $after, searchQuery: $searchQuery) {{
	# 		pageInfo {{
	# 			nextCursor
	# 		}}
	# 		items {{
	# 			{post_field}
	# 		}}
	# 	}}
	# }}
	# '''
	posts_feed = graphql.Query(
		'PostsFeed',
		{
			'$order': 'String',
			'$after': 'String',
			'$searchQuery': 'String',
			'$languages': '[String!]',
			'$count': 'Int',
			'$boardSlugs': '[String!]',
			'$pinAnnouncements': 'Boolean',
			'$pinPinned': 'Boolean',

			'$votesBefore': 'String',
			'$votesAfter': 'String',
			'$votesCount': 'Int',
			'$votesOrder': 'String',
			'$votesDirection': 'String'
		},
		graphql.Field(
			name='posts',
			args={
				'order': '$order',
				'after': '$after',
				'searchQuery': '$searchQuery',
				'languages': '$languages',
				'count': '$count',
				'boardSlugs': '$boardSlugs',
				'pinAnnouncements': '$pinAnnouncements',
				'pinPinned': '$pinPinned'
			},
			data=connection_generator(post_attributes)
		)
	)
	get_comments = graphql.Query(
		'post',
		{'$id': 'Int!', '$commentsOrder': 'String', '$commentsAfter': 'String'},
		{
			graphql.Field('post', args={'id': '$id'}, data={
				graphql.Field(
					'comments',
					args={'order': '$commentsOrder', 'after': '$commentsAfter'},
					data={
						'pageInfo': 'nextCursor',
						'items': (
							comment_detail_comment_fragment,
							{
								'comments': comment_detail_comment_fragment
							}
						)
					}
				)
			})
		},
		fragments=[comment_detail_comment_fragment]
	)
	# get_comments = f'''
	# query post(
	# 	$id: Int!, $commentsOrder: String, $commentsAfter: String
	# ) {{
	# 	post(id: $id) {{
	# 		comments(order: $commentsOrder, after: $commentsAfter) {{
	# 			pageInfo {{
	# 				nextCursor
	# 			}}
	# 			items {{
	# 				...CommentDetailComment
	# 				comments {{
	# 					...CommentDetailComment
	# 				}}
	# 			}}
	# 		}}
	# 	}}
	# }}

	# fragment CommentDetailComment on Comment {{
	# 	id
	# 	body
	# 	timeCreated
	# 	canEdit
	# 	canComment
	# 	canReport
	# 	hasReported
	# 	url
	# 	voteCount
	# 	canVote
	# 	hasVoted
	# 	{user_field}
	# }}

	# '''
	# query comments($after: String, $order: String) {
	# 	comments(after: $after, order: $order) {
	# 		items {
	# 			id
	# 		}
	# 	}
	# }
	# get_all_comments = f'''
	# query comments($after: String, $order: String) {{
	# 	comments(after: $after, order: $order) {{
	# 		items {{
	# 			{comment_field}
	# 			comments {{
	# 				{comment_field}
	# 			}}
	# 		}}
	# 		pageInfo {{
	# 			hasNextPage
	# 			nextCursor
	# 		}}
	# 	}}
	# }}
	# '''
	get_user = graphql.Query(
		'userByUsername',
		{'$username': 'String!'},
		graphql.Alias(
			'user',
			graphql.Field(
				{'userByUsername': user_attributes},
				args={'username': '$username'}
			)
		)
	)
	post_exists = graphql.Query('post', {'$id': 'Int!'}, {
		graphql.Field('post', args={'id': '$id'}, data='id')
	})

	create_post = '''
	mutation createPost($input: CreatePostInput!) {
		createPost(input: $input) {
			post {
				id
				url
				showHosted
				board {
					id
					name
					slug
					url
					replRequired
					template
				}
			}
		}
	}
	'''

