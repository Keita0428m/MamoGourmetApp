from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from .models import Pref, Category, Review
from .forms import SearchForm, SignUpForm, LoginForm, ReviewForm
import json
import requests
from django.db.models import Avg
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
# グローバル関数
# どこからもkeyidを呼び出すことが出来る


def get_keyid():
    return "e1eca5c6a2a74f9fb49000bc86b7debe"


class IndexView(TemplateView):
    template_name = 'mamogourmet/index.html'

    def get_context_data(self, *args, **kwargs):
        searchform = SearchForm()
        query = get_gnavi_data("", "RSFST09000", "", "花見", 12)
        res_list = rest_search(query)
        pickup_list = extract_restaurant_info(res_list)
        review_list = Review.objects.all()[:10]  # 追加

        params = {
            'searchform': searchform,
            'pickup_list': pickup_list,
            'review_list': review_list  # 追加
        }

        return params


def Search(request):
    if request.method == 'GET':
        searchform = SearchForm(request.POST)

        if searchform.is_valid():
            category_l = request.GET['category_l']
            pref = request.GET['pref']
            freeword = request.GET['freeword']
            query = get_gnavi_data("", category_l, pref, freeword, 10)
            res_list = rest_search(query)
            total_hit_count = len(res_list)
            # 4. 整形した情報をリスト形式で保存し、paramsの一要素として渡す
            restaurants_info = extract_restaurant_info(res_list)

    params = {
        'total_hit_count': total_hit_count,
        'restaurants_info': restaurants_info,
    }

    return render(request, 'mamogourmet/search.html', params)

# 1. 検索条件としてのパラメータを保持するための関数


def get_gnavi_data(id, category_l, pref, freeword, hit_per_page):
    keyid = get_keyid()
    # 一度に取得できる最大件数
    hit_per_page = hit_per_page
    # 店舗のid（グルナビ内で一意になっている）
    id = id
    # 大業態カテゴリ
    category_l = category_l
    # pref
    pref = pref
    # Freeword
    freeword = freeword
    # 今回は関東地方のみ（コール回数を少なくするため）
    area = "AREA110"
    # パラメータ設定
    query = {"keyid": keyid, "id": id, "area": area, "pref": pref,
             "category_l": category_l, "hit_per_page": hit_per_page, "freeword": freeword}

    return query


# 2. 該当の情報を取得するための関数
def rest_search(query):
    res_list = []
    res = json.loads(requests.get(
        "https://api.gnavi.co.jp/RestSearchAPI/v3/", params=query).text)
    # レスポンスがerror でない場合に処理を開始する
    if "error" not in res:
        res_list.extend(res["rest"])
    return res_list


# 3. 取得した情報を整形するための関数
def extract_restaurant_info(restaurants: 'restaurant response') -> 'restaurant list':
    restaurant_list = []
    for restaurant in restaurants:
        id = restaurant["id"]
        name = restaurant["name"]
        name_kana = restaurant["name_kana"]
        url = restaurant["url"]
        url_mobile = restaurant["url_mobile"]
        shop_image1 = restaurant["image_url"]["shop_image1"]
        shop_image2 = restaurant["image_url"]["shop_image2"]
        address = restaurant["address"]
        tel = restaurant["tel"]
        station_line = restaurant["access"]["line"]
        station = restaurant["access"]["station"]
        latitude = restaurant["latitude"]
        longitude = restaurant["longitude"]
        pr_long = restaurant["pr"]["pr_long"]

        restaurant_list.append([id, name, name_kana, url, url_mobile, shop_image1,
                                shop_image2, address, tel, station_line, station, latitude, longitude, pr_long])
    return restaurant_list


def ShopInfo(request, restid):
    keyid = get_keyid()
    id = restid
    query = get_gnavi_data(id, "", "", "", 1)
    res_list = rest_search(query)
    restaurants_info = extract_restaurant_info(res_list)
    review_count = Review.objects.filter(shop_id=restid).count()
    score_ave = Review.objects.filter(shop_id=restid).aggregate(Avg('score'))
    average = score_ave['score__avg']
    if average:
        average_rate = average / 5 * 100
    else:
        average_rate = 0

    if request.method == 'GET':
        review_form = ReviewForm()
        review_list = Review.objects.filter(shop_id=restid)
    else:
        form = ReviewForm(data=request.POST)
        score = request.POST['score']
        comment = request.POST['comment']

        if form.is_valid():
            review = Review()
            review.shop_id = restid
            review.shop_name = restaurants_info[0][1]
            review.image_url = restaurants_info[0][5]
            review.user = request.user
            review.score = score
            review.comment = comment
            # 以下のif文を追加。レビュー投稿済みかの判断。
            is_exist = 0
            is_exist = Review.objects.filter(
                shop_id=review.shop_id).filter(user=review.user).count()

            if not is_exist == 0:
                messages.error(request, '既にレビューを投稿済みです。')
                return redirect('mamogourmet:shop_info', restid)
            else:
                review.save()
                messages.success(request, 'レビューを投稿しました。')  # 追加
                return redirect('mamogourmet:shop_info', restid)
        else:
            messages.error(request, 'エラーがあります。')  # 追加
            return redirect('mamogourmet:shop_info', restid)
        return render(request, 'mamogourmet/index.html', {})

    params = {
        'title': '店舗詳細',
        'review_count': review_count,
        'restaurants_info': restaurants_info,
        'review_form': review_form,
        'review_list': review_list,
        'average': average,
        'average_rate': average_rate,
    }

    return render(request, 'mamogourmet/shop_info.html', params)


class SignUp(CreateView):
    form_class = SignUpForm
    template_name = 'mamogourmet/signup.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('mamogourmet:index')
        return render(request, 'mamogourmet/signup.html', {'form': form})


class Login(LoginView):
    form_class = LoginForm
    template_name = 'mamogourmet/login.html'


class Logout(LogoutView):
    template_name = 'mamogourmet/logout.html'
