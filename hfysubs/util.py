from beetusbot import config


def filter_post(post):
    if post.subreddit.display_name.lower() != config.SUBREDDIT.lower():
        return False

    if post.link_flair_text is not None and any(k in post.link_flair_text.lower() for k in config.IGNORE):
        return False
    else:
        return post.is_self and not any(k in post.title.lower() for k in config.IGNORE)
