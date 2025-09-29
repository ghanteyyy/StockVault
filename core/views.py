from django.shortcuts import render


def ratelimit_exceeded(request, exception):
    content = {
        "page_title": "Too many requests",
        "message": "You've hit the limit. Please try again in a moment.",
    }

    response = render(request, "errors/403.html", content, status=403)
    return response


def page_not_found(request, exception):
    content = {
        "page_title": "Page not found",
        "message": "The page you're looking for doesn't exist.",
        "path": request.path,
    }

    return render(request, "errors/404.html", content, status=404)
