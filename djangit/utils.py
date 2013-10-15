def seperate_tree_entries(tree, tree_path, repo):
    """ Seperates tree entries

    Iterates through the tree entries to place trees in one list and blobs in
    another depending on the entrys type_num.

    """
    trees = []
    blobs = []

    for name, mode, sha in tree.iteritems():
        if tree_path:
            url = tree_path + '/' + name.decode('utf-8')
        else:
            url = name.decode('utf-8')

        entry = repo.get_object(sha)

        if entry.type_num == 2:
            trees.append((mode, name, url, sha))
        elif entry.type_num == 3:
            blobs.append((mode, name, url, sha))

    return trees, blobs


def get_author(commit):
    ms = commit.author.index('<')
    name = commit.author[:ms].strip(' ')
    email = commit.author[ms + 1:-1]
    gravatar = get_gravatar(email, 60)

    author = {
        'name': name,
        'email': email,
        'gravatar': gravatar,
    }

    return author


def get_gravatar(email, size):
    # import code for encoding urls and generating md5 hashes
    import urllib
    import hashlib

    # Set your variables here
    default = "monsterid"

    # construct the url
    gravatar_url = "https://secure.gravatar.com/avatar/" + \
        hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d': default, 's': str(size)})

    return gravatar_url