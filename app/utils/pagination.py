

def paginate_queryset(qs, page_num: int, page_size: int):
    total      = qs.count()
    total_page = max(1, (total + page_size - 1) // page_size)
    offset     = (page_num - 1) * page_size
    return {
        "result":      list(qs[offset:offset + page_size]),
        "total":       total,
        "totalPage":   total_page,
        "currentPage": page_num,
    }