from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Book, Rental
from .forms import RentalForm
import logging

logger = logging.getLogger(__name__)


class BookListView(ListView):
    model = Book
    template_name = 'index.html'
    context_object_name = 'books'

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.GET.get('category', '').strip()
        author = self.request.GET.get('author', '').strip()
        year = self.request.GET.get('year')

        if category:
            qs = qs.filter(category__icontains=category)
        if author:
            qs = qs.filter(author_name__icontains=author)
        if year:
            qs = qs.filter(year=year)
        return qs.order_by('title')

@login_required
def rent_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if book.status != 'available':
        messages.error(request, 'Эту книгу нельзя арендовать, так как она не доступна.')
        return redirect('book-list')

    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.user = request.user
            rental.book = book
            rental.save()

            book.status = 'rented'
            book.save()

            messages.success(request, 'Книга успешно арендована!')
            return redirect('book-list')
    else:
        form = RentalForm()

    return render(request, 'rent_book.html', {'book': book, 'form': form})