def custom_paginator(f, l, **kwargs):
    """Simple custom paginator for those can_pageniate() returns false
    :param f: API function
    :param l: name of the list object to paginate
    :param kwargs: Args passes to the API function
    :return: iterator of result object
    """
    next_token = None
    while True:

        if next_token is None:
            # boto3 does not accept f(NextToken=None)
            r = f(**kwargs)
        else:
            r = f(NextToken=next_token, **kwargs)

        for i in r[l]:
            yield i

        try:
            next_token = r['NextToken']
        except KeyError:
            break
