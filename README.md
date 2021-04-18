# Examples
```py
# Getting the newest posts on Repl Talk and printing their titles
async for post in client.boards.all.get_posts():
	print(post.title)
```

# API Reference
How to use the `repltalk` lib for Python. The functions are pretty self explanatory but I've added a short description for each of them.
***
> *The following functions are all coroutines unless specifically specified because asyncio is cool*

## Client
`class repltalk.Client()`
+ `await login(username, password)`
Logs in to Repl.it with your username and password. Your bot must be verified in order to use this function.
+ `await get_post(post_id)`
Gets the post with that id. 
*returns Post*
+ `await get_comment(comment_id)`
Gets the comment with that id. 
*returns Comment*
+ `await post_exists(post_id)`
Returns whether or not the post exists.
+ `await get_leaderboard(limit=30)`
Gets the top users from the Repl Talk leaderboard. 
*returns list of `User`s*
+ `await get_all_comments()`
Gets all the recent comments from Repl Talk. 
*returns list of `Comment`s
+ `await get_user(username)`
Gets the user with that username. 
*returns User*
+ `await get_reports(resolved=False)`
Gets a list of reports. Only works for moderators or admins. See *Report List*
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
+ `async for post in get_posts(sort='top', search='')`
Gets the most recent posts from that board.
Sort is the sorting order (top|hot|new) and search is the search query.
*returns AsyncPostList*
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
+

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
+ `timestamp`
The time the post was created at. (datetime.datetime object)
+ `url`
The post url in Repl Talk.
+ `repl`
The repl attached to the post.
+ `language`
The *Language* that the Repl attached to the post uses.
+ `show_hosted`
Indicates whether the post has a hosted repl linked to it.
+ `is_announcement`
Whether the post is marked as an announcement.
+ `pinned`
Whether the post has been pinned to the top of the board.
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
If the post has been answered (will always be False if it's not a question).
+ `comment_count`
The amount of comments the post has
+ `await get_comments()`
Gets the comments on the post.
+ `await post_comment(content)`
Posts a comment on the post.
+ `await report(reason)`
Report the post
+ `await delete()`
Delete the Post


***
## Comment
+ `id`
The comment ID.
+ `content`
The comment body.
+ `timestamp`
The time the comment was created at. (datetime.datetime object)
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
+ `await reply(content)`
Replies to the comment with the content.
+ `await report(reason)`
Report the comment
+ `await delete()`
Delete the comment

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
The amount of cycles/karma that user has.
+ `roles`
The roles the user has set on their profile.
+ `bio` 
The short description written by a user on their profile.
+ `organization` 
The organization that the user is a part of. This can be None. See *Organization*
+ `first_name`
What the user set as their first name in their profile
+ `last_name`
What the user set as their last name in their profile
+ `languages`
The *Language*s that the user uses most often.
+ `timestamp`
The time when the user account was created. (datetime.datetime object)
+ `is_hacker`
Whether the user has the hacker plan
+ `await get_comments(limit=30, order='new')`
Get a list of up to 1100 of the users comments. See *Comment*
+ `await get_posts(limit=30, order='new')`
Get a list of up to 100 of the user's posts. See *Post*
+ `await ban(reason)`
Ban the user


***
## PostList/AsyncPostList
Acts like a normal list, except you can iterate over it
+ `await next()`
Gets the next page of posts. Not present in *AsyncPostList* because it's done automatically.
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
## Organization
The organization users are a part of
+ `name`
The name of the organization

***
## Report List
List of reports. *see Report* If linked post/comment is deleted is lazy report, *See lazyReport*
+ `for report in get_reports`
Cycles through the reports, with lazy posts/comments.
+ `async for report in get_reports`
Cycles through the reports with full posts, if there is a post.

***
## Report
A report on a comment or post
+ `id`
The report id
+ `type`
The type of the report. (`'post'` or `'comment'`)
+ `reason`
Why the report was made
+ `timestamp`
When the report was created
+ `creator`
Who created the report
+ `await get_attached()`
Get the attached post/comment

***
## Lazy Report
A less complete report
+ `id`
The report id
+ `reason`
Why the report was made
+ `creator`
Who created the report

***
## Lazy Post
A less complete post
+ `url`
The url to the post
+ `id`
The post's id
+ `author`
The post's author
+ `content`
The post's content
+ `title`
The post's title
+ `await delete()`
Delete the post
+ `await get_full_post()`
Returns the full post

***
## Lazy Comment
A less complete comment
+ `url`
The url to the comment
+ `id`
The comment's id
+ `author`
The comment's author
+ `content`
The comment's content
+ `await delete()`
Delete the comment
+ `await get_full_comment()`
Returns the full comment


