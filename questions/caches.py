from django.core.cache import cache

class BaseCache:
    key: str = ""
    timeout: int = 60 * 60 * 24

    @classmethod
    def get_items(cls):
        return cache.get(cls.key) or []

    @classmethod
    def set_items(cls, items):
        cache.set(cls.key, items, cls.timeout)


class LatestQuestionsCache(BaseCache):
    key = "latest_questions_10"
    timeout = 60 * 60 * 24


class PopularTagsCache(BaseCache):
    key = "popular_tags_10_last_3_months"
    timeout = 60 * 60 * 24


class BestMembersCache(BaseCache):
    key = "best_members_10_last_week"
    timeout = 60 * 60 * 24
