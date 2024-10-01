from django.db import models
from rest_framework.filters import SearchFilter


class CustomSearch(SearchFilter):
    search_param = "name"

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = ["name__startswith", "name__icontains"]

        search_queries = [
            models.Q(**{orm_lookup: search_terms[0]})
            for orm_lookup in orm_lookups
        ]
        result = (
            queryset.filter(search_queries[0] | search_queries[1])
            .annotate(
                search_type_order=models.Case(
                    models.When(search_queries[0], then=models.Value(1)),
                    models.When(search_queries[1], then=models.Value(2)),
                )
            )
            .order_by("search_type_order", "name")
        )

        return result
