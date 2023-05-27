from django_filters import rest_framework as filters


class DateFilter(filters.FilterSet):
    date = filters.DateRangeFilter(field_name="date")
