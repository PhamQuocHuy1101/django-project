from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.http import HttpResponse
from django.db.models import Q

from ads.models import Ad, Comment, Fav
from ads.forms import AdForm, CreateForm, CommentForm
from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView


class AdListView(OwnerListView):
    template_name = "ads/ad_list.html"
    def get(self, request):
        strval =  request.GET.get("search", False)
        if strval :
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(tags__name__in=[strval]), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().distinct()
        else:
            ad_list = Ad.objects.all()

        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values('id')
            favorites = [ row['id'] for row in rows ]
        ctx = {'ad_list' : ad_list, 'favorites': favorites}

        return render(request, self.template_name, context=ctx)


class AdDetailView(OwnerDetailView):
    model = Ad
    def get(self, request, pk):

        # x = Forum.objects.get(id=pk)
        ad = get_object_or_404(self.model, pk=pk)

        comments = Comment.objects.filter(ad=ad).order_by('-updated_at')
        comment_form = CommentForm()

        context = { 'ad' : ad, 'comments': comments, 'comment_form': comment_form }

        return render(request, 'ads/ad_detail.html', context)

class AdCreateView(LoginRequiredMixin, View):
    template = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    def get(self, request):
        form = CreateForm()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = AdForm(request.POST, request.FILES or None)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template, ctx)

        pic = form.save(commit = False)
        pic.owner = self.request.user
        pic.save()

        form.save_m2m()

        # form = self.form_valid(form)
        return redirect(self.success_url)

class AdUpdateView(LoginRequiredMixin, View):
    model = Ad
    template = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    def get(self, request, pk):
        ad = get_object_or_404(self.model, pk=pk, owner=self.request.user)
        form = CreateForm(instance=ad)

        return render(request, self.template, {'form': form})

    def post(self, request, pk):
        ad = get_object_or_404(self.model, pk=pk, owner=self.request.user)
        form = AdForm(request.POST, request.FILES or None, instance=ad)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template, ctx)

        pic = form.save(commit = False)
        pic.save()

        form.save_m2m()

        return redirect(self.success_url)

class AdDeleteView(OwnerDeleteView):
    model = Ad
    template_name = "ads/ad_confirm_delete.html"


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        ad = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=ad)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])


def stream_file(request, pk):
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.content_type
    response['Content-Length'] = len(ad.picture)
    response.write(ad.picture)
    return response



# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        ad = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=ad)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        ad = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=ad).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()