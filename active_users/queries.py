"""Queries for the active_users app."""
from django.contrib.auth.models import User

from dateutil.relativedelta import relativedelta

from query_utils import get_months_range, parse_date


def get_retained_users_per_month(start_date, end_date):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    months = get_months_range(start_date, end_date)

    previous_month = start_date - relativedelta(months=1)
    months_formatted = []
    for month in months:
        if previous_month:
            months_formatted.append(
                (previous_month, month)
            )
        previous_month = month

    results = []
    for month_tuple in months_formatted:
        previous, current = month_tuple
        curr_qs = User.objects.all().filter(
            activity__day__month=current.month,
            activity__day__year=current.year)
        curr_id = list(curr_qs.values_list('pk', flat=True))
        prev_qs = User.objects.all().filter(
            activity__day__month=previous.month,
            activity__day__year=previous.year)
        prev_id = list(prev_qs.values_list('pk', flat=True))
        results.append(len(set(curr_id).intersection(prev_id)))
    return results


def get_resurrected_users_per_month(start_date, end_date, threshold=2):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    months = get_months_range(start_date, end_date)
    month_diff = relativedelta(months=threshold)

    results = []
    for month in months:
        threshold = month - month_diff
        last_month = month - relativedelta(months=1)
        qs = User.objects.all().filter(
            activity__day__month__lte=threshold.month,
            activity__day__year__lte=threshold.year)
        qs = qs.filter(
            activity__day__month=month.month,
            activity__day__year=month.year)
        qs = qs.exclude(
            activity__day__month=last_month.month,
            activity__day__year=last_month.year)
        results.append(qs.count())
    return results
