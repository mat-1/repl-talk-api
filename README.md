# Examples
```py
# Getting the newest posts on Repl Talk and printing their titles
for post in # TODO BECAUSE IM LAZY
```

# API Reference
How to use the `repltalk` lib for Python. The functions are pretty self explanatory but I've added a short description for each of them.
***
> *The following functions are all coroutines unless specifically specified because asyncio is cool*

## Client
`class repltalk.Client()`
+ `login(username, password)`
Logs in to Repl.it with your username and password. Your bot must be verified in order to use this function.
+ `get_post(post_id)`
Gets the post with that id. 
*returns Post*
+ `post_exists(post_id)`
Returns whether or not the post exists.
+ `get_leaderboard(limit=30)`
Gets the top users from the Repl Talk leaderboard. 
*returns list of `User`s*
+ `get_all_comments()`
Gets all the recent comments from Repl Talk. 
*returns list of `Comment`s
+ `get_user(username)`
Gets the user with that username. 
*returns User*
+ `boards`
See *Board*.

***
## Board
`class client.boards`
***
+ `all`
The *All* board on Repl Talk.
+ `share`
The *Share* board on Repl Talk.
+ `ask`
The *Ask* board on Repl Talk.
+ `announcements`
The *Announcements* board on Repl Talk.
+ `challenge`
The *Challenge* board on Repl Talk.
+ `learn`
The *Learn* board on Repl Talk.
***
+ `get_posts(sort='top', search='')`
Gets the most recent posts from that board.
Sort is the sorting order (top|hot|new) and search is the search query.
*returns PostList*
### RichBoard
A board that contains all the information from *Board*, and more.
You can get this by doing `await client.boards.get(board_name)` (NOT YET ADDED)
+ `name`
The name of the board.
+ `title_cta`
Title call to action
+ `body_cta`
Body call to action
+ `button_cta`
Button call to action
+ `repl_required`
Whether a Repl is required to be submitted.

***
## Post ('client', 'id', 'title', 'content', 'is_announcement', 'path', 'url', 'board',
		'timestamp', 'can_edit', 'can_comment', 'can_pin', 'can_set_type',
		'can_report', 'has_reported', 'is_locked', 'show_hosted', 'votes',
		'can_vote', 'has_voted', 'author', 'repl', 'answered', 'can_answer',
		'pinned', 'comment_count', 'language')
+ `id`
The post ID.
+ `title`
The post title.
+ `content`
The post content.
+ `board`
The board the post was made on.
+ `votes`
The amount of upvotes the post has.
+ `author`
The post author. Will be a User object.
+ `timestamp`
The time the post was created at. (datetime.datetime object)
+ `url`
The post url in Repl Talk.
+ `repl`
The repl attached to the post.
+ `language`
The *Language* of the Repl on the post.
+ `show_hosted`
Indicates whether the post has a hosted repl linked to it.
+ `is_announcement`
Whether the post is marked as an announcement.
+ `pinned`
Whether the post has been pinned to the top of the board
+ `can_edit`
Indicates if the user can edit the post. This will be *False* unless you created the post.
+ `can_comment`
If the user can comment on the post.
+ `can_vote`
Indicates if the user can upvote the post.
+ `has_voted`
Indicates if the user has already voted on the post.
+ `is_locked`
Indicates if the post is locked.
+ `can_answer`
Whether or not the user can answer the post.
+ `answered`
If the post has been answered (will always be False if can't answer).
+ `comment_count`
The amount of comments the post has
+ `get_comments()`
Gets the comments on the post.
+ `post_comment(content)`
Posts a comment on the post.

***
## Comment ('client', 'id', 'content', 'timestamp', 'can_edit', 'can_comment',
		'can_report', 'has_reported', 'path', 'url', 'votes', 'can_vote',
		'has_voted', 'author', 'post', 'replies', 'parent')
+ `id`
The comment ID.
+ `content`
The comment body.
+ `timestamp`
The time the comment was created at.
+ `can_edit`
Indicates if the user can edit the comment.
+ `can_comment`
Whether or not the user can post a comment.
+ `url`
The comment's url.
+ `votes`
Gets the amount of upvotes the comment has.
+ `can_vote`
Indicates if the user can vote on the comment.
+ `has_voted`
Indicates if the user has already upvoted the post.
+ `author`
The *User* for the author of the post.
+ `post`
The post that the comment was made on.
+ `replies`
A list of replies that the comment received.
+ `parent`
The parent comment, if any.
+ `reply(content)`
Replies to the comment with the content.

***
## User ('client', 'data', 'id', 'name', 'avatar', 'url', 'cycles', 'roles',
		'full_name', 'first_name', 'last_name', 'organization', 'is_logged_in',
		'bio', 'subscription', 'languages')
+ `id`
The user ID. Pretty useless since you can't get the user from their id.
+ `name`
The user's username.
+ `avatar`
The user's avatar url.
+ `url`
The user's profile link.
+ `cycles`
The amount of cycles that user has.
+ `roles`
The roles the user has set on their profile.
+ `bio` 
The short description written by a user on their profile.

***
## PostList
Acts like a normal list, except you can iterate over it
+ `next`
Gets the next page of posts.
+ `board`
Gets the board of the repls it's getting from

***
## Repl
+ `id`
The Repl ID.
+ `embed_url`
The url for embedding the Repl on a web page.
+ `url`
The url of the Repl.
+ `title`
The title of the Repl.
+ `language`
The *Language* of the Repl.

***
## Language
Represents a programming language on Repl.it.
+ `id`
Gets the ID of the language (ie python3).
+ `display_name`
Gets the display name of the language (ie Python).
+ `icon`
Gets the url for the language icon.
+ `category`
Gets the category that the language is listed as.
+ `is_new`
Whether the language was recently added to Repl.it.
+ `tagline`
A short description of the language.

***
## Subscription
('name', 'plan_id', 'name', 'plan')