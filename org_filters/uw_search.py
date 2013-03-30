from spotseeker_server.org_filters import search

class Filter(search.Filter):
    keys = set((
        'extended_info:reservable',
        'extended_info:noise_level',
        ))

    def filter_query(self, query):
        """Filter based on reservable and noise_level."""

        if 'extended_info:reservable' in self.request.GET:
            query = query.filter(
                    spotextendedinfo__key="reservable",
                    spotextendedinfo__value__in=['true', 'reservations']
                    )

        if 'extended_info:noise_level' in self.request.GET:
            noise_levels = self.request.GET.getlist("extended_info:noise_level")

            exclude_silent = True
            exclude_quiet = True
            exclude_moderate = True
            exclude_loud = True
            exclude_variable = True

            for level in noise_levels:
                if "silent" == level:
                    exclude_silent = False
                if "quiet" == level:
                    exclude_quiet = False
                    exclude_variable = False
                if "moderate" == level:
                    exclude_moderate = False
                    exclude_variable = False

            if exclude_silent:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="silent"
                        )

            if exclude_quiet:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="quiet"
                        )

            if exclude_moderate:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="moderate"
                        )

            if exclude_loud:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="loud"
                        )

            if exclude_variable:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="variable"
                        )

        return query
