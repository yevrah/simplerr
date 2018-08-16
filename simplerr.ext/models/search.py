# ~*~ coding: utf-8 ~*~
"""
fleaker.peewee.mixins.search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module that provides a mixin that can do generic SQL ``LIKE`` queries. If more
complex searching is required, it is strongly recommended that the developer
looks into a searching technology, like ElasticSearch, instead of attempting to
make this more complex.
Example:
    To use this mixin, add it to the classes inheritance chain.
    .. code-block:: python
        import peewee
        from fleaker import db
        from fleaker.peewee import SearchMixin
        class Post(SearchMixin, db.Model):
            title = peewee.CharField(max_length=255, null=False)
            body = peewee.TextField(null=False, default='')
            class Meta:
                # These are the default search fields for this model.
                search_fields = ('title', 'body')
        # Let's create a few posts for this blog
        Post.insert_many([
            {'title': 'Welcome!', body: 'Content'},
            {'title': 'Content is hard to write.', body: 'I am lazy.'},
            {'title': 'Hacked!', body: 'Some malcontent hacked this site!'},
        ])
        # Because all the Posts have the word 'content' in them, a search
        # should return all the posts.
        content_query = Posts.search('Content')
        assert content_query.count() == Posts.select().count()
        # The search query is ordered by relevance in this order:
        #
        # 1. Straight equality (``posts.body = 'Content'``)
        # 2. Right hand ``LIKE`` (``posts.body LIKE 'Content%')
        # 3. Substring ``LIKE`` (``posts.content LIKE %Content%``)
        #
        # The query's search term is applied to the query case insensitively.
        # It should also be noted that matches for title will be ordered above
        # matches for content because of the ordering in Meta.search_fields.
        content_posts = list(content_query)
        # Post.body was an exact match for 'Content'
        assert content_posts[0].title == 'Welcome!'
        # Post.title had content in the title.
        assert content_posts[0].title == 'Content is hard to write.'
        # Post.body was a right hand substring of 'Content'
        assert content_posts[2].title == 'Goodbye!'
        # Post.body had the word 'Content' in there somewhere.
        assert content_posts[3].title == 'Hacked!'
        # The search method can overload the searched fields by providing it's
        # own list.
        hacked_search = Post.search('hacked', fields=('title',))
        assert goodbye_search.count() == 1
"""

from functools import reduce

from playhouse.shortcuts import case
from peewee import operator

from fleaker.orm import PeeweeModel


class SearchMixin(PeeweeModel):
    """Mixin that provides generic SQL ``LIKE`` searching across columns.
    Attributes:
        Meta.search_fields (tuple[str]): These are the names of the fields to
            search over by default. Because of how
            ``peewee.SelectQuery.order_by`` works, items will be weighed by the
            items in this lists order. Which is to say, given a two item list,
            any type of matches for the first item will come before an exact
            match for an item in the second.
    """

    class Meta(object):
        search_fields = ()

    @classmethod
    def search(cls, term, fields=()):
        """Generic SQL search function that uses SQL ``LIKE`` to search the
        database for matching records. The records are sorted by their
        relavancey to the search term.
        The query searches and sorts on the folling criteria, in order, where
        the target string is ``exactly``:
        1. Straight equality (``x = 'exactly'``)
        2. Right hand ``LIKE`` (``x LIKE 'exact%'``)
        3. Substring ``LIKE`` (``x LIKE %act%``)
        Args:
            term (str): The search term to apply to the query.
        Keyword Args:
            fields (list|tuple|None): An optional list of fields to apply the
                search to. If not provided, the class variable
                ``Meta.search_fields`` will be used by default.
        Returns:
            peewee.SelectQuery: An unexecuted query for the records.
        Raises:
            AttributeError: Raised if `search_fields` isn't defined in the
                class and `fields` aren't provided for the function.
        """
        if not any((cls._meta.search_fields, fields)):
            raise AttributeError(
                "A list of searchable fields must be provided in the class's "
                "search_fields or provided to this function in the `fields` "
                "kwarg."
            )

        # If fields are provided, override the ones in the class
        if not fields:
            fields = cls._meta.search_fields

        query = cls.select()

        # Cache the LIKE terms
        like_term = ''.join((term, '%'))
        full_like_term = ''.join(('%', term, '%'))

        # Cache the order by terms
        # @TODO Peewee's order_by supports an `extend` kwarg will will allow
        # for updating of the order by part of the query, but it's only
        # supported in Peewee 2.8.5 and newer. Determine if we can support this
        # before switching.
        # http://docs.peewee-orm.com/en/stable/peewee/api.html#SelectQuery.order_by
        order_by = []

        # Store the clauses seperately because it is needed to perform an OR on
        # them and that's somehow impossible with their query builder in
        # a loop.
        clauses = []

        for field_name in fields:
            # Cache the field, raising an exception if the field doesn't
            # exist.
            field = getattr(cls, field_name)

            # Apply the search term case insensitively
            clauses.append(
                (field == term) |
                (field ** like_term) |
                (field ** full_like_term)
            )

            order_by.append(case(None, (
                # Straight matches should show up first
                (field == term, 0),
                # Similar terms should show up second
                (field ** like_term, 1),
                # Substring matches should show up third
                (field ** full_like_term, 2),
            ), default=3).asc())

        # Apply the clauses to the query
        query = query.where(reduce(operator.or_, clauses))

        # Apply the sort order so it's influenced by the search term relevance.
        query = query.order_by(*order_by)

        return query
