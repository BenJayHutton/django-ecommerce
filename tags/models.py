from django.db import models


class TagQuerySet(models.query.QuerySet):
    def public(self):
        return self.filter(public=True)


class TagManager(models.Manager):
    # overriding get_queryset so we can use the queryset above
    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_queryset().public()


class Tag(models.Model):
    BOOKS_SUB_TAG = ['Adventure', 'Fantasy', 'Fiction', 'Manga', 'Non Fiction', 'True Crime']
    FILM_SUB_TAG = ['Fantasy.', 'Fiction.', 'Sci Fi']
    TRADING_CARD_GAME_SUB_TAG = ['Magic the Gathering', 'Pokemon', 'Yugioh']

    name = models.CharField(max_length=128, unique=True)
    public = models.BooleanField(default=False)
    blurb = models.TextField(null=True, blank=True)

    objects = TagManager()

    def __str__(self):
        return self.name
    
    def sub_tag(sub_tag=None):
        query = None
        if sub_tag is not None:
            if sub_tag == "Film":
                query = Tag.FILM_SUB_TAG
            elif sub_tag == "Books":
                query = Tag.BOOKS_SUB_TAG
            elif sub_tag == "Trading Cards":
                query = Tag.TRADING_CARD_GAME_SUB_TAG
            elif sub_tag in Tag.FILM_SUB_TAG:
                query = Tag.FILM_SUB_TAG
            elif sub_tag in Tag.FILM_SUB_TAG:
                query = Tag.FILM_SUB_TAG
            elif sub_tag in Tag.BOOKS_SUB_TAG:
                query = Tag.BOOKS_SUB_TAG
            elif sub_tag in Tag.TRADING_CARD_GAME_SUB_TAG:
                query = Tag.TRADING_CARD_GAME_SUB_TAG
        return query
        