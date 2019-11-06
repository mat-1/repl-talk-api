# API Reference
How to use the `repltalk` lib for Python. The functions are pretty self explanatory but I've added a short description for each of them.
***
*The following functions are all coroutines because asyncio is cool*

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
The *All* board on Repl Talk
+ `share`
The *Share* board on Repl Talk
+ `ask`
The *Ask* board on Repl Talk
+ `announcements`
The *Announcements* board on Repl Talk
+ `challenge`
The *Challenge* board on Repl Talk
+ `learn`
The *Learn* board on Repl Talk
***
+ `get_posts(sort='top', search='')`
Gets the most recent posts from that board.
Sort is the sorting order (top|hot|new) and search is the search query.
*returns PostList*
***
## Post
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
+ `datetime`
The time the post was created at.
+ `url`
The post url in Repl Talk.
+ `repl`
The repl attached to the post.
+ `language`
The *Language* of the Repl on the post.
+ `show_hosted`
Indicates if the post has a hosted repl linked to it.
+ `is_announcement`
If the post is marked as an announcement.
+ `pinned`
Whether or not the post has been pinned to the top of the board
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
## Comment
+ `id`
The post ID.
+ `content`
The post body.
+ `time_created`
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
+ `reply(content)`
Replies to the comment with the content.
***
## User
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
Acts basically like a normal list.
+ `next`
Gets the next page of posts.
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
Represents a programming language.
+ `name`
Gets the default name of the language (ie python3).
+ `display_name`
Gets the display name of the language (ie Python).
+ `icon`
Gets the url to the SVG for the language icon.