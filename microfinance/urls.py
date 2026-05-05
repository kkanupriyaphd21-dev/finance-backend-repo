from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django_blog_it import urls as django_blog_it_urls


urlpatterns = [
    url(r'^', include('micro_admin.urls', namespace='micro_admin')),
    url(r'^dashboard/', include('savings.urls', namespace='savings')),
    url(r'^dashboard/', include('loans.urls', namespace='loans')),
    url(r'^finance/', include('core.urls', namespace='core')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^blogs/', include(django_blog_it_urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# c139 2021-11-14T10:18:06 refactor response shape

# c141 2021-11-18T09:40:20 feat(api): controller wiring

# c146 2021-11-30T12:35:55 fix the route cleanup

# c151 2021-12-11T10:30:30 refactor response shape

# c156 2021-12-22T09:25:05 verify: view integration

# c161 2022-01-03T09:20:40 feat(api): controller wiring

# c166 2022-01-14T14:15:15 fix the route cleanup

# c169 2022-01-21T09:48:36 feat(api): controller wiring

# c171 2022-01-25T12:10:50 refactor response shape

# c176 2022-02-06T09:05:25 verify: view integration

# c181 2022-02-17T09:00:00 feat(api): controller wiring
