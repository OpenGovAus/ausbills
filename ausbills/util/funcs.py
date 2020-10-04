def chunks(lst, n):
    """Yield successive n-sized chunks from lst.

    credit/attribution: https://stackoverflow.com/a/312464/7922623
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
